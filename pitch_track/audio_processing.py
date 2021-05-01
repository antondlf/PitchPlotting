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


def process_recording(original_audio_path, audio_data, chaptername, database_inputs):
    """Yields the template with latest plot and posts recording info into db."""

    print(original_audio_path)
    # First get a unique id for this recording
    trial_id = get_unique_id() # TODO: better naming system


    # Chaptername passed to the function
    chapter_id = chaptername
    user_id = g.user['id']
    trial_path = os.path.join(current_app.root_path, '../participant_recordings', trial_id)
    error = None
    if is_baseline == False:
        plot_path, recording_path = save_plot(
            original_audio_path,
            trial_path,
            audio_data,
            chaptername,
            chapteroccurrence
        )
        if not plot_path:
            error += 'Plot_path missing.'
    elif is_baseline == True:
        # TODO: split into save_plot and save_audio
        # TODO: add condition for save_plot
        plot_path, recording_path = save_plot(
            original_audio_path, trial_path,
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
        return flash(error) # TODO: test error message
    else:
        db = get_db()
        db.execute(
            'INSERT INTO recordings (chapter_id, user_id, chapter_order, trial_id, is_baseline)'
            # 'user_id, sent_order, experimental_condition, session_number, trial_type, sent_group,'
            # 'sent_type, sent_id, repetition, trial_id'
            ' VALUES (?, ?, ?, ?, ?)',
            (chapter_id, user_id, chapteroccurrence, trial_id, is_baseline)
        )
        db.commit()
    return plot_path, recording_path


def save_plot(filename, path, audio_data, chaptername, trial_num, is_baseline=False):
    """Uses temporary file to write wav file and process in praat into
    pitch plot saved on a given path."""

    recording_path = path + '.wav'
    with open(recording_path, 'wb') as out_file:
        out_file.write(audio_data)
        print('recording saved')

    if os.path.isfile(recording_path) and os.path.getsize(recording_path) > 0: #TODO: fix error message here

        flash("No audio was recorded.", 'error')
        return redirect(url_for('/record.record', chaptername=chaptername, chapteroccurrence=trial_num))

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

