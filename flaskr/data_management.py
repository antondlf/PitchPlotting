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
    # Get chapter directory
    for dirname in os.listdir(recordings_dir):
        print(dirname)
        chap_directory = os.path.join(recordings_dir, dirname)

        # Check that it is a directory
        if os.path.isdir(chap_directory):
            sent_id = dirname
            item_pair = os.listdir(chap_directory)
            print(item_pair)
            item_pair.sort(key=lambda f: f.rsplit('.')[-1], reverse=True)
            print('after sort:')
            print(item_pair)
            for file in item_pair:

                sent_group = 'Group' # TODO: figure out where to source

                if file.endswith('.txt'):
                    with open(os.path.join(chap_directory, file)) as in_file:
                        text = in_file.read()
                        sentence_text_exists = True
                    if text.endswith('?'):
                        sent_type = 'Q'
                    else:
                        sent_type = 'S'

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
                # TODO: get new variables from schema
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



