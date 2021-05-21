import uuid

import os
import click
from flask import current_app, g
from pitch_track.text_plot import draw_text_plot
from flask.cli import with_appcontext
import flaskr.db

def get_unique_id():
    return str(uuid.uuid1())


def init_chapters(database): # TODO: make only one class of sentence
    """Take chapter titles from Recordings directory and
    create a chapter for each file"""
    recordings_dir = os.path.join(current_app.root_path, '../Recordings')
    sent_id = None
    text = None
    sentence_text_exists = False
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

    # Get matched sentences in db

    for set in sentences['matched'].keys():

        sent_group = set
        set_sents = sentences['matched'][set]

        for n in set_sents.keys():

            current_sent = sentences['matched'][set][n]

            input_sent_pair(recordings_dir, sent_group, current_sent, database)

    for n in sentences['unmatched'].keys():

        current_sent = sentences['unmatched'][n]
        sent_group = 'unmatched'

        input_sent_pair(recordings_dir, sent_group, current_sent, database)


def input_sent_pair(recordings_dir, sent_group, current_sent, database):

    for sent_type in ['Q', 'S']:

        sent_id = current_sent + '(' + sent_type + ')'

        chap_directory = os.path.join(recordings_dir, sent_id)

        # Check that it is a directory
        if os.path.isdir(chap_directory):
            item_pair = os.listdir(chap_directory)
            for file in item_pair:

                if file.endswith('.txt'):
                    with open(os.path.join(chap_directory, file)) as in_file:
                        text = in_file.read()
                        sentence_text_exists = True

                    if not sentence_text_exists:
                        return print('Error: missing text in baseline')

                # Extract the name and path of wav file
                elif file.endswith('.wav'):
                    audio_path = os.path.join(chap_directory, file)

                elif file.endswith('.TextGrid'):
                    textgrid_path = os.path.join(chap_directory, file)
                elif file.endswith('.png'):
                    textplot_path = os.path.join(chap_directory, file)

                elif file == '.DS_Store':
                    pass
                else:
                    return print("Error: filesystem corrupt")

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



