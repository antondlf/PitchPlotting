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
    """Yields record template with audio."""

    recordings = list()
    db = get_db()

    sentence = db.execute(
        'SELECT audio_path, text, textplot_path'
        ' FROM chapters WHERE chapter_title=?'  # p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC',
        (chaptername,)
    ).fetchall()

    # Make sure there is only one identified sentence
    if not len(sentence) == 1:
        print(sentence)
        abort(404, "Audio '{0}' doesn't exist or database entry is corrupt.".format(chaptername))

    # Get paths and text
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

        if textplot_path == 'Baseline':
            return render_template('/record/baseline.html', sentence=text)
        if len(user_audio) > 0:
            plot_path = user_audio[0]['trial_id'] + '.png'
        else:
            plot_path = None

        recordings = [row['trial_id'] + '.wav' for row in user_audio]


    elif request.method == 'POST':

        audio_data = request.data

        if textplot_path == 'Baseline':
            is_baseline = True
            process_recording(text, audio_path, chaptername, audio_data, is_baseline, chapteroccurrence)
            return render_template('/record/baseline.html', sentence=text)

        process_recording(text, audio_path, chaptername, audio_data, is_baseline, chapteroccurrence)


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


def process_recording(text, original_recording, chaptername, audio_data, is_baseline, chapteroccurrence):
    """Yields the template with latest plot and posts recording info into db."""

    print(original_recording)
    user_id = g.user['id']
    # First get a unique id for this recording
    toks = text.split(' ')
    sent_name = toks[0] + '_' + toks[1]
    sent_type = 'QUESTION' if toks[-1][-1] == '?' else 'STATEMENT'
    unique_identifier = get_unique_id()
    trial_id = str(user_id) + '_' + sent_name + '_' + sent_type + '_' + unique_identifier # TODO: better naming system

    print(trial_id)

    # Chaptername passed to the function
    chapter_id = chaptername
    user_id = g.user['id']
    trial_path = os.path.join(current_app.root_path, '../participant_recordings', trial_id)
    error = None

    save_plot(
        original_recording, trial_path,
        audio_data, chaptername,
        chapteroccurrence,
        is_baseline=True
    )

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


def save_plot(filename, path, audio_data, chapter_name, trial_num, is_baseline=False):
    """Uses temporary file to write wav file and process in praat into
    pitch plot saved on a given path."""

    recording_path = path + '.wav'
    with open(recording_path, 'wb') as out_file:
        out_file.write(audio_data)
        print('recording saved')

    if os.path.isfile(recording_path) and os.path.getsize(recording_path) > 0:
        flash("No audio was recorded.", 'error')
        redirect(url_for('/record.record', chaptername=chapter_name, chapteroccurrence=trial_num))
        return None

    if is_baseline is True:
        plot_path = 'Baseline'
        return plot_path, recording_path
    else:
        plot_path = path + '.png'

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

@bp.route('/textplot/<string:chaptername>/<string:filename>')
@login_required
def return_textplot_file(chaptername, filename):
    """Get the plot file from tmp directory."""

    path = os.path.join(current_app.root_path, '../Recordings/', chaptername)

    return send_from_directory(path, filename, as_attachment=True)

@bp.route('/record/<string:chaptername>/<string:chapter_order>/post_trial/next_chapter')
@login_required
def next_chapter(chaptername, chapter_order): # TODO:create Baseline condition


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

            return redirect(url_for('/record.end_message'))


@bp.route('/done')
@login_required

def end_message():
    return 'Done!'