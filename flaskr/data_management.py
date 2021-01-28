import uuid

import os
import click
from flask import current_app, g
from flask.cli import with_appcontext
import flaskr.db

def get_unique_id():
    return uuid.uuid1() # TODO: figure out id generation


def init_chapters(database): # TODO: clean up paths
    """Take chapter titles from Recordings directory and
    create a chapter for each file"""
    recordings_dir = os.path.join(current_app.root_path, '../Recordings')
    # Get chapter directory
    for dirname in os.listdir(recordings_dir):

        chap_directory = os.path.join(recordings_dir, dirname)

        # Check that it is a directory
        if os.path.isdir(chap_directory):

            item_pair = os.listdir(chap_directory)

            # Check that there are two files in directory
            if len(item_pair) == 3: #TODO decide whether or not textgrids will be included
                #database = get_db()

                # Extract info from the directories
                for file in item_pair:

                    # Extract the name and path of wav file
                    if file.endswith('.wav'):
                        title = dirname
                        audio_path = os.path.join(chap_directory, file)

                    # Extract text from txt file
                    elif file.endswith('.txt'):
                        with open(os.path.join(chap_directory, file)) as in_file:
                            text = in_file.read()

                    elif file.endswith('.TextGrid'):
                        textgrid_path = os.path.join(chap_directory, file)
            else:
                print("Error: incorrect number of files in directory")
            if title and text:
                database.execute(
                    'INSERT INTO chapters (chapter_title, audio_path, textgrid_path, text)'
                    ' VALUES (?, ?, ?, ?)',
                    (title, audio_path, textgrid_path, text)
                )
                database.commit()
        else:
            print("Error:", chap_directory, 'is a file, not a directory.')



