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


@bp.route('/record/<string:chaptername>', methods=['POST', 'GET'])
@login_required
def record(chaptername):
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
        # if len (user_audio) < 1: #TODO: limit recording opportunities
        #     #render_template()#TODO: create 'Go to Next chapter' template
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
        if len(recordings) > 1: #TODO:decide limit to recordings
            recordings = recordings[-1]

        #return render_template('/record/index.html', recording=chaptername, sentence=text, plot=plot_path)

    elif request.method == 'POST':
        audio_data = request.data
        # TODO: this is the issue with baseline ones
        if textplot_path == 'Baseline':
            is_baseline = True
            process_recording(audio_path, chaptername, audio_data, is_baseline)
            return render_template('/record/baseline.html', sentence=text)

        process_recording(audio_path, chaptername, audio_data, is_baseline)


        return redirect(url_for('/record.record', chaptername=chaptername), code=302)

    return render_template(
            '/record/index.html', recording=chaptername, sentence=text, textplot=textplot, plot=plot_path, audio=recordings
        )



def process_recording(original_recording, chaptername, audio_data, is_baseline):
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
        recording_path = trial_path + '.wav'

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
            'INSERT INTO recordings (chapter_id, user_id, trial_id, is_baseline)'
            ' VALUES (?, ?, ?, ?)',
            (chapter_id, user_id, trial_id, is_baseline)
        )
        db.commit()
    return plot_path, recording_path


# @bp.route('/recorded/<string:filename>')
# def recorded(filename):
#     return render_template()


#bp = Blueprint('pitch_track', __name__, url_prefix='/pitch_track')


#@bp.route('/record/send/<string:filename>/<string:path>', methods=['POST'])
def save_plot(filename, path, audio_data):
    """Uses temporary file to write wav file and process in praat into
    pitch plot saved on a given path."""

    recording_path = path + '.wav'
    plot_path = path + '.png'
    # Save the file that was sent, and read it into a parselmouth.Sound
    with open(recording_path, 'wb') as out_file: # TODO: turn into path to participant_recordings
        out_file.write(audio_data)
    sound = praat.Sound(recording_path)



    # Calculate the pitch track with Parselmouth
    new_pitch = sound.to_pitch()
    old_pitch = praat.Sound(filename).to_pitch()
    draw_pitch(new_pitch, old_pitch, plot_path)

    return plot_path, recording_path




@bp.route('/record/participant_recordings/<string:filename>')
@login_required
def return_plot_file(filename):
    """Get the plot file from tmp directory."""
    dir = os.path.join(current_app.root_path, '../participant_recordings')
    return send_from_directory(dir, filename, as_attachment=True)

@bp.route('/record/<string:chaptername>/<string:filename>')
@login_required
def return_textplot_file(chaptername, filename):
    """Get the plot file from tmp directory."""

    path = os.path.join(current_app.root_path, '../Recordings/', chaptername)

    return send_from_directory(path, filename, as_attachment=True)

@bp.route('/record/<string:chaptername>/next_chapter')
@login_required
def next_chapter(chaptername): # TODO:create Baseline condition


    index_dir = os.path.join(current_app.root_path, '../Recordings')
    name_sections = chaptername.rsplit('_', 1)
    new_chapter = ''.join([name_sections[0], '_', str(int(name_sections[-1]) + 1)])

    if new_chapter in os.listdir(index_dir):
        print('chapter exists')
        return redirect(url_for('/record.record', chaptername=new_chapter, code=302))
    else:
        if name_sections[0] == 'Baseline':
            return redirect(url_for('/record.record', chaptername='Chapter_1'))
        else:
            print('chapter does not exist, redirect')
            return redirect(url_for('/record.end_message'))



@bp.route('/done')
@login_required

def end_message():
    return 'Done!'