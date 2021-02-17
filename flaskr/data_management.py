import uuid

import os
import click
from flask import current_app, g
from pitch_track.text_plot import draw_text_plot
from flask.cli import with_appcontext
import flaskr.db

def get_unique_id():
    return str(uuid.uuid1())


def init_chapters(database):
    """Take chapter titles from Recordings directory and
    create a chapter for each file"""
    recordings_dir = os.path.join(current_app.root_path, '../Recordings')
    title = None
    text = None
    sentence_text_exists = False
    # Get chapter directory
    for dirname in os.listdir(recordings_dir):
        print(dirname)
        chap_directory = os.path.join(recordings_dir, dirname)

        # Check that it is a directory
        if os.path.isdir(chap_directory):
            title = dirname
            item_pair = os.listdir(chap_directory)
            print(item_pair)
            item_pair.sort(key=lambda f: f.rsplit('.')[-1], reverse=True)
            print('after sort:')
            print(item_pair)
            for file in item_pair:

                if file.endswith('.txt'):
                    with open(os.path.join(chap_directory, file)) as in_file:
                        text = in_file.read()
                        sentence_text_exists = True
                    if not sentence_text_exists:
                        return print('Error: missing text in baseline')
                if dirname.startswith('Chapter'):
                    # Extract the name and path of wav file
                    if file.endswith('.wav'):
                        audio_path = os.path.join(chap_directory, file)

                    elif file.endswith('.TextGrid'):
                        plotname = file.rsplit('.')[0] + '.png'
                        textplot_path = os.path.join(chap_directory, plotname)
                        textgrid_path = os.path.join(chap_directory, file)
                        draw_text_plot(audio_path, textgrid_path, textplot_path)
                elif dirname.startswith('Baseline'):
                    textplot_path = 'Baseline'
                    audio_path = 'Baseline'
                else:
                    return print("Error: filesystem corrupt")

            if title and text:
                database.execute(
                    'INSERT INTO chapters (chapter_title, audio_path, textplot_path, text)'
                    ' VALUES (?, ?, ?, ?)',
                    (title, audio_path, textplot_path, text)
                )
                database.commit()

            else:
                return print('Missing title or text')
        else:
            print("Error:", chap_directory, 'is a file, not a directory.')



