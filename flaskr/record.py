from flask import (
    Blueprint, flash,  current_app, g, redirect, render_template, request, url_for, send_from_directory
)
from flaskr.auth import login_required

from flaskr.db import get_db

from werkzeug.exceptions import abort

from pitch_track.audio_processing import process_recording

import os

user_dict = {
    '1': {
        'condition': 'b',
        'order': {
            'Session 1': {
                'pre_train': {'0': 'Chapter_1', '1': 'Chapter_2'},
                'training': {
                    '0': 'Chapter_5', '1': 'Chapter_6',
                    '2':'Chapter_7', '3': 'Chapter_8'
                },
                'post_train': {'0': 'Chapter_3', '1': 'Baseline_4'}
            },
            'Session_2': {
                'pre_train': {'0': 'Chapter_1', '1': 'Chapter_2'},
                'training': {
                    '0': 'Chapter_5', '1': 'Chapter_6',
                    '2':'Chapter_7', '3': 'Chapter_8'
                },
                'post_train': {'0': 'Chapter_3', '1': 'Baseline_4'}
            },
            'Session 3': {
                'pre_train': {'0': 'Chapter_7', '1': 'Chapter_8'}
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

        recording_path = process_recording(audio_path, audio_data, chaptername, database_inputs)

        # Make sure the microphone picked up a recording
        if recording_path == None:
            flash("No audio was recorded.", 'error')
            return redirect(url_for('/record.record', session=session, trial_type=trial_type, chapterorder=chapterorder))

        # If it's not a training trial no post_trial necessary
        if trial_type != 'training':
            return render_template('/record/baseline.html', sentence=text)

        return redirect(url_for('/record.post_trial', session=session, trial_type=trial_type, chapter_order=chapterorder))

    if condition == 'a':
        return render_template(
                '/record/index.html', recording=chaptername, sentence=text, textplot=textplot, plot=plot_path, audio=recordings
            ) #TODO: fix index.html to reflect changes Done?
    else:
        return render_template(
                '/record/index.html', recording=chaptername, sentence=text, textplot=None, plot=None, audio=recordings
            )


@bp.route('/record/<string:session>/<string:trial_type>/<string:chapter_order>/post_trial')
@login_required
# TODO: figure out arguments necessary to query
# Variables I need at the end of this function:
#   session, trial_type, chapter_order
# Repetition is probably necessary
def post_trial(session, trial_type, chapter_order):

    db = get_db()
    user_id = str(g.user['id'])
    condition = user_dict[user_id]['condition']

    # TODO: change database queries to align with new sql schema
    user_audio = db.execute(
        'SELECT trial_id, sent_id'
        ' FROM recordings WHERE session_number=? AND user_id=? AND sent_order=?'
        ' ORDER BY created DESC',
        (session, user_id, chapter_order)
    ).fetchall()


    sent_id = user_audio[0]['sent_id']

    sentence = db.execute(
        'SELECT audio_path, text'
        ' FROM chapters WHERE sent_id=?'  # p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC',
        (sent_id,)
    ).fetchall()

    if len(user_audio) > 0:
        plot_path = user_audio[0]['trial_id'] + '.png'
    else:
        print("No audio was processed")
        plot_path = None

    recording_path = user_audio[0]['trial_id'] + '.wav'

    text = sentence[0]['text']
    if condition == 'a':
        return render_template('/record/post_trial.html', sentence=text, recording=recording_path, plot=plot_path, original_audio=sent_id)

    elif condition == 'b':
        return render_template('/record/post_trial.html', sentence=text, recording=recording_path, plot=None, original_audio=sent_id)



@bp.route('/record/<string:session>/<string:trial_type>/<string:chapter_order>/post_trial/next_chapter')
@login_required
def next_chapter(session, trial_type, chapter_order): # TODO: revamp this function

    # zero indexing so one less than real length
    # sequence = {
    #     'pre_train': 7,
    #     'training': 31,
    #     'post_train': 7
    # }
    # TODO: Remember to change this to actual sequence for experiment
    sequence = {
     'pre_train': 1,
     'training': 3,
     'post_train': 1,
    }

    # Get the list of trial types for this session.
    user_id = str(g.user['id'])
    trial_type_list = \
        user_dict[user_id] \
            ['order'] \
            [session].keys()

    # Cast to int in order to run int operations
    chapter_order_int = int(chapter_order)
    if chapter_order_int < int(sequence[trial_type]):

        chapter_order_int += 1
        chapter_order = str(chapter_order_int)
        return redirect(url_for('/record.record', chapterorder=chapter_order, session=session, trial_type=trial_type))

    elif chapter_order == sequence[trial_type]:
        if trial_type == trial_type_list[-1]:
            return redirect(url_for('/record.end_message'))
        else:
            new_trial_type_index = \
                trial_type_list.index(trial_type) + 1
            new_trial_type = trial_type_list[new_trial_type_index]

            return redirect(url_for('/record.record', chapterorder=chapter_order, session=session, trial_type=new_trial_type))
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