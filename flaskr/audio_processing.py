from flask import (
    flash, current_app
)

from click import echo

from flaskr.db import get_db

from pitch_track import pitch_plot

from flaskr.data_management import get_unique_id

import parselmouth as praat

import numpy as np

import pickle

import os

# This is a backend file that processes all of the audio input by speakers
# It takes in frontend data and manages all backend processing


def process_recording(original_audio_path, audio_data, chaptername, database_inputs):
    """Function takes in audio data and metadata, processes it and
    and posts recording info into db.
    Returns a the path where the recording is stored.
    """

    #print(original_audio_path)


    error = None

    # Unpack database inputs
    user_id, sent_order, experimental_condition, \
    session, trial_type, sent_group, \
    sent_type, sent_id, repetition = database_inputs

    trial_id = str(user_id) + '_' + str(sent_id) + '_' + str(repetition) + '_' + str(get_unique_id())
    trial_path = os.path.join(current_app.root_path, '../participant_recordings', trial_id)

    recording_path = save_audio(trial_path, audio_data)
    #print(recording_path)

    # If recording_path = None then wav file is empty.
    if recording_path == None:

        return None

    if trial_type == 'training':
        result = save_plot(chaptername, trial_path)

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

        trial_type_dict = {'pre_train': 1, 'training': 2, 'post_train': 3}
        trial_type_ord = trial_type_dict[trial_type]
        # TODO: Write try block to verify complete data storage
        db.execute(
            'INSERT INTO recordings ('
            'user_id, sent_order, experimental_condition,'
            'session_number, trial_type, trial_type_ord, sent_group,'
            'sent_type, sent_id, repetition, trial_id'
            ')'
            ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (
                user_id, sent_order, experimental_condition,
                session, trial_type, trial_type_ord, sent_group,
                sent_type, sent_id, repetition, trial_id
            )
        )
        db.commit()
        #
        # try:
        #     sentence = db.execute(
        #         'SELECT sent_group, sent_type, text, audio_path, textplot_path'  # TODO: get all variables necessary
        #         ' FROM chapters WHERE sent_id=?'  # p JOIN user u ON p.author_id = u.id'
        #         ' ORDER BY created DESC',
        #         (sent_id,)
        #     ).fetchall()
        #     print(sentence[0])
        #
        # except:
        #
        #     print('Error, audio entry corrupt')

    return recording_path


def save_audio(path, audio_data):
    """Writes audio to given path"""

    recording_path = path + '.wav'
    with open(recording_path, 'wb') as out_file:
        out_file.write(audio_data)
        print('recording saved')

    if os.stat(recording_path).st_size == 0:

        return None

    else:
        return recording_path


def save_plot(chaptername, path):
    """produces comparison plot using draw_pitch
    and returns path to plot and recording.
    """

    plot_path = path + '.png'

    recording_path = path + '.wav'


    # Generate praat sound objects
    new_pitch = praat.Sound(recording_path)

    # Make sure that written audio isn't empty
    # TODO: this will yield an error, make sure there's an escape
    if np.count_nonzero(new_pitch.as_array()) == 0:
        return None

    db = get_db()
    old_pitch_pickle = db.execute(
        'SELECT precomputed_trace'
        ' FROM chapters'
        ' WHERE sent_id=?',
        (chaptername,)
    ).fetchall()[0]['precomputed_trace']

    old_pitch = pickle.loads(old_pitch_pickle)

    pitch_plot.draw_pitch(new_pitch, old_pitch, plot_path)

    return plot_path, recording_path

