from flask import (
    Blueprint, flash, current_app, g, redirect, render_template, request, url_for, send_from_directory
)
from flaskr.auth import login_required

from flaskr.db import get_db

from flaskr.audio import download_file

from pitch_track.pitch_plot import draw_pitch

from flaskr.data_management import get_unique_id

import parselmouth as praat

import os


bp = Blueprint('/audio_process', __name__)

def process_recording(original_recording, chaptername, audio_data, is_baseline, chapteroccurrence):
    """Yields the template with latest plot and posts recording info into db."""

    print(original_recording)
    # First get a unique id for this recording
    trial_id = get_unique_id() # TODO: better naming system


    # Chaptername passed to the function
    chapter_id = chaptername
    user_id = g.user['id']
    trial_path = os.path.join(current_app.root_path, '../participant_recordings', trial_id)
    error = None
    if is_baseline == False:
        plot_path, recording_path = save_plot(
            original_recording,
            trial_path,
            audio_data,
            chaptername,
            chapteroccurrence
        )
        if not plot_path:
            error += 'Plot_path missing.'
    elif is_baseline == True:

        plot_path, recording_path = save_plot(
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
    return plot_path, recording_path


def save_plot(filename, path, audio_data, chapter_name, trial_num, is_baseline=False):
    """Uses temporary file to write wav file and process in praat into
    pitch plot saved on a given path."""

    recording_path = path + '.wav'
    with open(recording_path, 'wb') as out_file:
        out_file.write(audio_data)
        print('recording saved')

    def is_empty_file(fpath):
        return os.path.isfile(fpath) and os.path.getsize(fpath) > 0

    if is_empty_file(recording_path):

        flash("No audio was recorded.", 'error')
        redirect(url_for('/record.record', chaptername=chapter_name, chapteroccurrence=trial_num))

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




@bp.route('/audio_process/participant_recordings/<string:filename>')
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