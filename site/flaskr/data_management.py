import uuid

import os
from flask import current_app

# This file provides utilities to initialize the database
# inputting native speaker recording and plot paths.

def get_unique_id():
    """This function generates a unique four character id
    meant to disambiguate repetitions of the same trial
    that a participant may do.
    """

    return str(uuid.uuid1())[:4]


def init_chapters(database): # TODO: make only one class of sentence
    """Take chapter titles from Recordings directory and
    create a chapter for each file"""

    # Get path for recordings (hardcoded)
    recordings_dir = os.path.join(current_app.root_path, '../../Recordings')
    sent_id = None
    text = None
    sentence_text_exists = False

    # A bit of hardcoding, these will change so probably moving to
    # a json file stored on the server will be better once that
    # change is implemented
    # TODO: move to json
    sentences = {
        'matched':
            {'set_1': {
                '1': 'Mario_vola','2': 'Delia_guida',
                '3': 'Livia_dorme', '4': 'Barbara_vive',
                '5': 'Angelo_giunge', '6': 'Debora_gira',
                '7': 'Daria_brinda'
            },
                'set_2': {
                '1': 'Adriana_beve', '2': 'Giuliana_mangia',
                '3': 'Damiano_morde', '4': 'Amedeo_lava',
                '5': 'Edoardo_vede', '6': 'Loredana_vende',
                '7': 'Gabriele_ama'
            },
                'set_3': {
                    '1': 'Il_lago', '2': 'Il_brodo',
                    '3': 'La_legna', '4': 'La_rana',
                    '5': 'Il_ladro', '6': 'La_via',
                    '7': 'Il_nome'
                },
                'set_4': {
                    '1': 'Il_giornale', '2': 'La_balena',
                    '3': 'Il_melone', '4': 'La_bambina',
                    '5': 'La_ragione', '6': 'Il_rumore',
                    '7': 'La_bevanda'
                }},
        'unmatched': {
            '1': 'Anna_lavora', '2': 'Emilia_arriva',
            '3': 'Bernardo_viene', '4': 'Andrea_rimane',
            '5': 'Luigi_odia', '6': 'Elena_guarda',
            '7': 'Giovanni_ruba', '8': 'Irene_disegna'}
    }
    question_tag = '(Q)'
    statement_tag = '(S)'

    # Input matched sentences into db
    for set in sentences['matched'].keys():

        sent_group = set
        set_sents = sentences['matched'][set]

        for n in set_sents.keys():

            current_sent = sentences['matched'][set][n]

            input_sent_pair(recordings_dir, sent_group, current_sent, database)

    # Input unmatched sentences into db
    for n in sentences['unmatched'].keys():

        current_sent = sentences['unmatched'][n]
        sent_group = 'unmatched'

        input_sent_pair(recordings_dir, sent_group, current_sent, database)


def input_sent_pair(recordings_dir, sent_group, current_sent, database):
    """Takes sentence pair ids, processes corresponding
    files, and inputs them into the database."""

    # For both individuals in pair
    for sent_type in ['Q', 'S']:

        # Hardcoded id format is <sent_id>(<sent_type>)
        # e.g. Mario_vola(Q)
        sent_id = current_sent + '(' + sent_type + ')'

        # Get directory for sentence
        chap_directory = os.path.join(recordings_dir, sent_id)

        # Check that it is a directory
        if os.path.isdir(chap_directory):

            item_pair = os.listdir(chap_directory)
            # Iterate through directory files
            for file in item_pair:

                # Get orthography from text file
                if file.endswith('.txt'):
                    with open(os.path.join(chap_directory, file)) as in_file:
                        text = in_file.read()
                        sentence_text_exists = True

                    if not sentence_text_exists:
                        return print('Error: missing text in baseline')

                # Get audio file path
                elif file.endswith('.wav'):
                    audio_path = os.path.join(chap_directory, file)

                # Get textgrid for text_plot generation (deprecated)
                elif file.endswith('.TextGrid'):
                    #textgrid_path = os.path.join(chap_directory, file)
                    pass
                # Get path to text_plot
                elif file.endswith('.png'):
                    textplot_path = os.path.join(chap_directory, file)

                # In case files have been uploaded from mac and .DS_Store
                # was not deleted
                elif file == '.DS_Store':
                    pass
                # I
                else:
                    return print("Error: filesystem corrupt")

            # TODO: this check is not exhaustive
            if sent_id and text:

                database.execute(
                    'INSERT INTO chapters (sent_group, sent_type, sent_id, text, audio_path, textplot_path)'
                    ' VALUES (?, ?, ?, ?, ?, ?)',
                    (sent_group, sent_type, sent_id, text, audio_path, textplot_path)
                )
                database.commit()

            else:
                return print('Missing title or text')
        else:
            print("Error:", chap_directory, 'is a file, not a directory.')



