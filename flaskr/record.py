from flask import (
    Blueprint, current_app, g, redirect, render_template, request, url_for, send_from_directory
)
from flaskr.auth import login_required

from flaskr.db import get_db

from werkzeug.exceptions import abort

from pitch_track.audio_processing import process_recording

import os

user_dict = {
    '1': {
        'condition': 'a',
        'order': {
            'Session 1': {
                'pre_train': {'0': 'Chapter_1', '1': 'Chapter_2'},
                'training': {'0': 'Chapter_5', '1': 'Chapter_6'},
                'post_train': {'0': 'Chapter_3', '1': 'Baseline_4'}
            },
            'Session_2': {
                'pre_train': {'0': 'Chapter_1', '1': 'Chapter_2'},
                'training': {'0': 'Chapter_5', '1': 'Chapter_6'},
                'post_train': {'0': 'Chapter_3', '1': 'Baseline_4'}
            },
            'Session_3': {
                'generalization': {'0': 'Chapter_7', '1': 'Chapter_8'}
            }
        },
    }
} # TODO: Query this from database
bp = Blueprint('/record', __name__)

@bp.route('/')
@login_required
def index():

    posts = ['Session 1', 'Session 2', 'Session 3']

    return render_template('blog/index.html', posts=posts)


@bp.route('/record/<string:session>/<string:trial_type>/<string:chapterorder>', methods=['POST', 'GET'])
@login_required
def record(session, trial_type, chapterorder): # TODO: maybe session and chapterorder and trial_type
    """Extracts relevant information from database and then
    yields record html template with audio."""

    print(session, chapterorder)
    # TODO: add functionality to access order from user table.
    user_id = g.user['id']
    print(user_id)
    # Query database here for dict
    # user_dict = some sql query
    # Query dict for session, condition, and order
    current_user = user_dict[str(user_id)]
    condition = current_user['condition']
    chaptername = current_user['order'][session][trial_type][chapterorder]

    recordings = list()
    db = get_db()

    sentence = db.execute(
        'SELECT sent_group, sent_type, text, audio_path, textplot_path' #TODO: get all variables necessary
        ' FROM chapters WHERE sent_id=?'  # p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC',
        (chaptername,)
    ).fetchall()

    # Make sure there is only one identified sentence
    if not len(sentence) == 1:
        print(sentence)
        abort(404, "Audio '{0}' doesn't exist or database entry is corrupt.".format(chaptername))

    # Get paths and text
    sent_group,\
        sent_type,\
        text,\
        audio_path,\
        textplot_path = sentence[0]

    # make sure textplot only contains the name of the file
    textplot = textplot_path.rsplit('/', 1)[-1]

    if request.method == 'GET':
        user_audio = db.execute(
            'SELECT trial_id'
            ' FROM recordings WHERE sent_id=? AND user_id=? AND session_number=? AND sent_order=?'
            ' ORDER BY created DESC',
            (chaptername, user_id, session, chapterorder)
        ).fetchall()

        if trial_type != 'training':
            return render_template('/record/baseline.html', sentence=text)
        if len(user_audio) > 0:
            plot_path = user_audio[0]['trial_id'] + '.png'
        else:
            plot_path = None

        recordings = [row['trial_id'] + '.wav' for row in user_audio]


    elif request.method == 'POST':

        audio_data = request.data
        database_inputs = (user_id,
                             chapterorder,  # sent_order in schema
                             condition,
                             session,
                             trial_type,
                             sent_group,
                             sent_type,
                             chaptername,  # sent_id in schema
                             False) #TODO: figure out how to get rep info
        process_recording(audio_path, audio_data, chaptername, database_inputs)

        if trial_type != 'training':
            return render_template('/record/baseline.html', sentence=text)

        return redirect(url_for('/record.post_trial', trial_type=trial_type, chapter_order=chapterorder))

    return render_template(
            '/record/index.html', recording=chaptername, sentence=text, textplot=textplot, plot=plot_path, audio=recordings
        ) #TODO: fix index.html to reflect changes


@bp.route('/record/<string:session>/<string:trial_type>/<string:chapter_order>/post_trial')
@login_required
# TODO: figure out arguments necessary to query
# Variables I need at the end of this function:
#   session, trial_type, chapter_order
# Repetition is probably necessary
def post_trial(session, trial_type, chapter_order):

    db = get_db()
    user_id = g.user['id']
    # TODO: change database queries to align with new sql schema
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



@bp.route('/record/<string:session>/<string:chaptername>/<string:chapter_order>/post_trial/next_chapter')
@login_required
def next_chapter(session, trial_type, chapter_order): # TODO: revamp this function


    sequence = {
        'pre_train': 8,
        'training': 32,
        'post_train': 8
    }

    # I need the following variables at the end of this function:
    # session, trial_type, chapterorder
    # session only changes

    if trial_type == 'pre_train':

    user_id = int(g.user['id'])
    if user_id <= 4:
        order_list =
    else:
        order_list =

    index_dir = os.path.join(current_app.root_path, '../Recordings')
    name_sections = trial_type.rsplit('_', 1)
    if trial_type == 'Baseline':  # TODO: add intermediate message between baseline and chapters
        new_chapter = ''.join([name_sections[0], '_', str(int(name_sections[-1]) + 1)])
        if new_chapter in os.listdir(index_dir):
            print('chapter exists')
            chapter_order = 0
            return redirect(url_for('/record.record', chaptername=new_chapter, chapteroccurrence=chapter_order))
        else:
            print('Baseline completed')

            return redirect(url_for('/record.record', chaptername=order_list['0'], chapteroccurrence=chapter_order))
    else:
        if chapter_order in order_list.keys():
            chapter_order = str(int(chapter_order) + 1)
            new_chapter = order_list[chapter_order]
            return redirect(url_for('/record.record', chaptername=new_chapter, chapteroccurrence=chapter_order))
        else:
            return redirect(url_for('/record.end_message'))


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

@bp.route('/done')
@login_required

def end_message():
    return 'Done!'