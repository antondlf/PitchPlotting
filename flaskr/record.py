from flask import (
    Blueprint, flash, current_app, g, redirect, render_template, request, url_for, send_from_directory
)
from flaskr.auth import login_required

from flaskr.db import get_db

from flaskr.audio import download_file

from werkzeug.exceptions import abort

import tempfile

import parselmouth as praat

from pitch_track.pitch_plot import draw_pitch

from flaskr.data_management import get_unique_id

import os


bp = Blueprint('/record', __name__)

@bp.route('/')
@login_required
def index():
    db = get_db()
    posts = db.execute(
        'SELECT created, chapter_title, audio_path' 
        ' FROM chapters'# p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)


@bp.route('/record/<string:chaptername>/<string:chapteroccurrence>', methods=['POST', 'GET'])
@login_required
def record(chaptername, chapteroccurrence):
    """Yields the template without a plot."""

    recordings = list()
    db = get_db()
    sentence = db.execute(
        'SELECT audio_path, text, textplot_path'
        ' FROM chapters WHERE chapter_title=?'  # p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC',
        (chaptername,)
    ).fetchall()
    if not len(sentence) == 1:
        print(sentence)
        abort(404, "Audio '{0}' doesn't exist or database entry is corrupt.".format(chaptername))
    audio_path, text, textplot_path = sentence[0]

    is_baseline = False

    # make sure textplot only contains the name of the file
    textplot = textplot_path.rsplit('/', 1)[-1]
    user_id = g.user['id']
    if request.method == 'GET':
        user_audio = db.execute(
            'SELECT trial_id'
            ' FROM recordings WHERE chapter_id=? AND user_id=?'
            ' ORDER BY created DESC',
            (chaptername, user_id)
        ).fetchall()
        # if len (user_audio) < 1:
        #     #render_template()
        #
        #     plot_path = None
        #else:
        if textplot_path == 'Baseline':
            return render_template('/record/baseline.html', sentence=text)
        if len(user_audio) > 0:
            plot_path = user_audio[0]['trial_id'] + '.png'
        else:
            plot_path = None

        recordings = [row['trial_id'] + '.wav' for row in user_audio]
        # if len(recordings) > 1:
        #     recordings = recordings[-1]

        #return render_template('/record/index.html', recording=chaptername, sentence=text, plot=plot_path)

    elif request.method == 'POST':
        audio_data = request.data

        if textplot_path == 'Baseline':
            is_baseline = True
            process_recording(audio_path, chaptername, audio_data, is_baseline, chapteroccurrence)
            return render_template('/record/baseline.html', sentence=text)

        process_recording(audio_path, chaptername, audio_data, is_baseline, chapteroccurrence)


        return redirect(url_for('/record.post_trial', chapter_id=chaptername, chapter_order=chapteroccurrence))

    return render_template(
            '/record/index.html', recording=chaptername, sentence=text, textplot=textplot, plot=plot_path, audio=recordings
        )


@bp.route('/record/<string:chapter_id>/<string:chapter_order>/post_trial')
@login_required
def post_trial(chapter_id, chapter_order):

    db = get_db()
    user_id = g.user['id']
    user_audio = db.execute(
        'SELECT trial_id'
        ' FROM recordings WHERE chapter_id=? AND user_id=? AND chapter_order=?'
        ' ORDER BY created DESC',
        (chapter_id, user_id, chapter_order)
    ).fetchall()
    sentence = db.execute(
        'SELECT audio_path, text'
        ' FROM chapters WHERE chapter_title=?'  # p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC',
        (chapter_id,)
    ).fetchall()

    if len(user_audio) > 0:
        plot_path = user_audio[0]['trial_id'] + '.png'
    else:
        print("No audio was processed")
        plot_path = None

    recording_path = user_audio[0]['trial_id'] + '.wav'

    text = sentence[0]['text']

    return render_template('/record/post_trial.html', sentence=text, recording=recording_path, plot=plot_path, original_audio=chapter_id)


def process_recording(original_recording, chaptername, audio_data, is_baseline, chapteroccurrence):
    """Yields the template with latest plot and posts recording info into db."""
    # First get a unique id for this recording
    trial_id = get_unique_id()

    #plot_id = '{}.png'.format(trial_id)
    #recording_id = '{}.wav'.format(trial_id)

    # Chaptername passed to the function
    chapter_id = chaptername
    user_id = g.user['id']
    trial_path = os.path.join(current_app.root_path, '../participant_recordings', trial_id)
    error = None
    if is_baseline == False:
        plot_path, recording_path = save_plot(original_recording, trial_path, audio_data)
        if not plot_path:
            error += 'Plot_path missing.'
    elif is_baseline == True:
        plot_path = 'Baseline' # TODO:get better solutions
        recording_path = save_plot(original_recording, trial_path, audio_data, is_baseline=True)

    if not chapter_id:
        error += 'Chapter_id is missing.'
    if not trial_id:
        error += 'trial_id missing.'
    if not trial_path:
        error += 'trial_path missing.'
    if error is not None:
        flash(error)
    else:
        db = get_db()
        db.execute(
            'INSERT INTO recordings (chapter_id, user_id, chapter_order, trial_id, is_baseline)'
            ' VALUES (?, ?, ?, ?, ?)',
            (chapter_id, user_id, chapteroccurrence, trial_id, is_baseline)
        )
        db.commit()
    return plot_path, recording_path


# @bp.route('/recorded/<string:filename>')
# def recorded(filename):
#     return render_template()


#bp = Blueprint('pitch_track', __name__, url_prefix='/pitch_track')


#@bp.route('/record/send/<string:filename>/<string:path>', methods=['POST'])
def save_plot(filename, path, audio_data, is_baseline=False):
    """Uses temporary file to write wav file and process in praat into
    pitch plot saved on a given path."""

    recording_path = path + '.wav'
    with open(recording_path, 'wb') as out_file:  # TODO: turn into path to participant_recordings
        out_file.write(audio_data)
        print('recording saved')

    if is_baseline is True:
        plot_path = 'Baseline'
        return plot_path, recording_path
    else:
        plot_path = path + '.png'
        # Save the file that was sent, and read it into a parselmouth.Sound
        with open(recording_path, 'wb') as out_file: # TODO: turn into path to participant_recordings
            out_file.write(audio_data)
        sound = praat.Sound(recording_path)



        # Calculate the pitch track with Parselmouth
        new_pitch = sound.to_pitch(time_step=0.005)
        old_pitch = praat.Sound(filename).to_pitch(time_step=0.005)
        draw_pitch(new_pitch, old_pitch, plot_path)

        return plot_path, recording_path




@bp.route('/record/participant_recordings/<string:filename>')
@login_required
def return_plot_file(filename):
    """Get the plot file from tmp directory."""
    dir = os.path.join(current_app.root_path, '../participant_recordings')
    return send_from_directory(dir, filename, as_attachment=True)

@bp.route('/textplot/<string:chaptername>/<string:filename>')
@login_required
def return_textplot_file(chaptername, filename):
    """Get the plot file from tmp directory."""

    path = os.path.join(current_app.root_path, '../Recordings/', chaptername)

    return send_from_directory(path, filename, as_attachment=True)

@bp.route('/record/<string:chaptername>/<string:chapter_order>/post_trial/next_chapter')
@login_required
def next_chapter(chaptername, chapter_order): # TODO:create Baseline condition


    terr_list = {
        '0': 'Chapter_1', '1': 'Chapter_1',
        '2': 'Chapter_2', '3': 'Chapter_2',
        '4': 'Chapter_1', '5': 'Chapter_3',
        '6': 'Chapter_3', '7': 'Chapter_2',
        '8': 'Chapter_4', '9': 'Chapter_4',
        '10': 'Chapter_3', '11': 'Chapter_4',
    }



    demo_list = {
        '0': 'Chapter_1', '1': 'Chapter_1', '2': 'Chapter_2', '3': 'Chapter_2',
        '4': 'Chapter_1', '5': 'Chapter_3', '6': 'Chapter_3', '7': 'Chapter_2',
        '8': 'Chapter_4', '9': 'Chapter_4', '10': 'Chapter_3', '11': 'Chapter_5',
        '12': 'Chapter_5', '13': 'Chapter_4', '14': 'Chapter_6', '15': 'Chapter_6',
        '16': 'Chapter_5', '17': 'Chapter_7', '18': 'Chapter_7', '19': 'Chapter_6',
        '20': 'Chapter_8', '21': 'Chapter_8', '22': 'Chapter_7', '23': 'Chapter_8'
    }


    user_id = int(g.user['id'])
    if user_id <= 4:
        order_list = terr_list
    else:
        order_list = demo_list

    index_dir = os.path.join(current_app.root_path, '../Recordings')
    name_sections = chaptername.rsplit('_', 1)
    if name_sections[0] == 'Baseline':  # TODO: add intermediate message between baseline and chapters
        new_chapter = ''.join([name_sections[0], '_', str(int(name_sections[-1]) + 1)])
        if new_chapter in os.listdir(index_dir):
            print('chapter exists')
            chapter_order = 0
            return redirect(url_for('/record.record', chaptername=new_chapter, chapteroccurrence=chapter_order))
        else:
            print('Baseline completed')

            return redirect(url_for('/record.record', chaptername=order_list[0], chapteroccurrence=chapter_order))
    else:
        if chapter_order in order_list.keys():
            new_chapter = order_list[chapter_order]
            chapter_order = str(int(chapter_order) + 1)
            return redirect(url_for('/record.record', chaptername=new_chapter, chapteroccurrence=chapter_order))
        else:
            return redirect(url_for('/record.end_message'))


@bp.route('/done')
@login_required

def end_message():
    return 'Done!'