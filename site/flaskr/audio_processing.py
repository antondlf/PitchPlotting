from flask import (
    flash, current_app
)

from flaskr.db import get_db

from site.pitch_track import pitch_plot

from flaskr.data_management import get_unique_id

import parselmouth as praat

import numpy as np

import os


def process_recording(original_audio_path, audio_data, chaptername, database_inputs):
    """Yields the template with latest plot and posts recording info into db."""

    print(original_audio_path)


    error = None

    # Unpack database inputs
    user_id, sent_order, experimental_condition, \
    session, trial_type, sent_group, \
    sent_type, sent_id, repetition = database_inputs

    trial_id = str(user_id) + '_' + str(sent_id) + '_' + str(sent_type) + '_' + str(repetition) + '_' + str(get_unique_id())
    trial_path = os.path.join(current_app.root_path, '../participant_recordings', trial_id)


    recording_path = save_audio(trial_path, audio_data)
    print(recording_path)

    # If recording_path = None then wav file is empty.
    if recording_path == None:

        return None

    if trial_type == 'training':
        result = save_plot(original_audio_path, trial_path)

        # if result = None then wav file only contains 0s.
        if result == None:
            return None

    if not chaptername:
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
            'INSERT INTO recordings ('
            'user_id, sent_order, experimental_condition,'
            'session_number, trial_type, sent_group,'
            'sent_type, sent_id, repetition, trial_id'
            ')'
            ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (
                user_id, sent_order, experimental_condition,
                session, trial_type, sent_group,
                sent_type, sent_id, repetition, trial_id
            )
        )
        db.commit()
    return recording_path


def save_audio(path, audio_data):
    """Save the audio to filename."""

    recording_path = path + '.wav'
    with open(recording_path, 'wb') as out_file:
        out_file.write(audio_data)
        print('recording saved')

    if os.stat(recording_path).st_size == 0:

        return None

    else:
        return recording_path

def save_plot(filename, path):
    """Uses temporary file to write wav file and process in praat into
    pitch plot saved on a given path."""

    plot_path = path + '.png'

    recording_path = path + '.wav'

    sound = praat.Sound(recording_path)

    if np.count_nonzero(sound.as_array()) == 0:
        return None

    # Calculate the pitch track with Parselmouth
    new_pitch = sound.to_pitch()
    old_pitch = praat.Sound(filename).to_pitch()
    pitch_plot.draw_pitch(new_pitch, old_pitch, plot_path)

    return plot_path, recording_path

