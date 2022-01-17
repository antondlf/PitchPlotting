from flask import (
    Blueprint, flash,  current_app, g, redirect, render_template, request, url_for, send_from_directory
)
from flaskr.auth import login_required

from flaskr.db import get_db

from werkzeug.exceptions import abort

from flaskr.audio_processing import process_recording

from flaskr.user_dict import user_state

from flaskr.notification_cue import notify_next_week

import os


# Main frontent utility, with backend functions mixed in

def get_user_state(user_id):
    if 'user_dict' not in g:
        g.user_dict = user_state(user_id)

    return g.user_dict


def get_progress(session, chapterorder):
    """Returns progress throughout the session."""

    chapterorder = int(chapterorder)

    if session != 'Session 3':

        progress = round((chapterorder/48)*100)

    elif session == 'Session 3':

        progress = round((chapterorder/8)*100)

    return progress


def is_repetition(trial_type, chapterorder):
    """Determine if recording is a repetition
    ____________________________________________
    Repetitions are every other recording for a
    training trial only, so theymust be divisible
    by 2. Since Python uses 0 indexing then the
    mod2 operation should equal 1.

    Returns 1 if it's repetition and 0 if not
    """
    if trial_type == 'Training':
        if int(chapterorder) % 2 == 1:
            return '1'

    else:
        return '0'

bp = Blueprint('/record', __name__)

# Simple login index
@bp.route('/')
@login_required
def index():

    post = 'Session_1'

    print(post)

    return render_template('/Instructions/Introduction.html', post=post)


# Specific session index, to be sent through email
@bp.route('/session_menu/<session>')
@login_required
def specific_index(session):

    if session == 'Session_3':

        return render_template('/Instructions/Introduction.html', post=session)

    return render_template('/Instructions/Introduction.html', post=session)


@bp.route('/record/<string:session>/<string:trial_type>/<string:chapterorder>', methods=['POST', 'GET'])
@login_required
def record(session, trial_type, chapterorder):
    """Extracts relevant information from database and then
    yields record html template with audio."""

    # Get user info
    print(session, chapterorder)
    db = get_db()
    user_id = g.user['id']
    user_dict = get_user_state(user_id)
    sent_id = user_dict.get_current_state(session, trial_type, chapterorder)
    condition = user_dict.get_condition()
    recordings = list()

    # Get current user sentence
    sentence = db.execute(
        'SELECT sent_group, sent_type, text, audio_path, textplot_path' #TODO: get all variables necessary
        ' FROM chapters WHERE sent_id=?'  # p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC',
        (sent_id,)
    # Fetchall should only yield one sentence
    ).fetchall()

    # Make sure there is only one identified sentence
    if not len(sentence) == 1:
        print(sentence)
        # This error message is misleading
        abort(404, "Audio '{0}' doesn't exist or database entry is corrupt.".format(sent_id))

    # Get paths and text
    sent_group,\
        sent_type,\
        text,\
        audio_path,\
        textplot_path = sentence[0]

    if text[-1] == '?':
        sentence_type = 'QUESTION: '
    else:
        sentence_type = 'STATEMENT: '

    progress = get_progress(session, chapterorder, trial_type)

    repetition = is_repetition(trial_type, chapterorder)

    # make sure textplot only contains the name of the file
    textplot = textplot_path.rsplit('/', 1)[-1]

    if request.method == 'GET':
        user_audio = db.execute(
            'SELECT trial_id'
            ' FROM recordings WHERE sent_id=? AND user_id=? AND session_number=? AND sent_order=?'
            ' ORDER BY created DESC',
            (sent_id, user_id, session, chapterorder)
        ).fetchall()

        if trial_type != 'training':
            return render_template('/record/baseline.html', sentence=text, sent_type=sentence_type, progress=progress)
        if len(user_audio) > 0:
            plot_path = user_audio[0]['trial_id'] + '.png'
        else:
            plot_path = None

        recordings = [row['trial_id'] + '.wav' for row in user_audio]

    # When there is a post process the data
    elif request.method == 'POST':

        # The audio data is contained in the request object
        audio_data = request.data
        # Wrap metadata in a tuple
        database_inputs = (user_id,
                             chapterorder,  # sent_order in schema
                             condition,
                             session,
                             trial_type,
                             sent_group,
                             sent_type,
                             sent_id,  # sent_id in schema
                             repetition)

        # Use utility from audio_processing.py to process the audio
        recording_path = process_recording(audio_path, audio_data, sent_id, database_inputs)

        # Make sure the microphone picked up a recording
        # This may not catch all recording errors
        if recording_path == None:
            flash("No audio was recorded.", 'error')
            return redirect(url_for('/record.record', session=session, trial_type=trial_type, chapterorder=chapterorder))

        # If it's not a training trial no post_trial necessary
        if trial_type != 'training':
            return render_template('/record/baseline.html', sentence=text, sent_type=sentence_type, progress=progress)

        # Redirect to the post_trial (comparison plot template)
        return redirect(url_for('/record.post_trial', session=session, trial_type=trial_type, chapter_order=chapterorder))


    if condition == 'a':
        # full feedback condition
        return render_template(
                '/record/index.html', recording=sent_id, sentence=text,
            sent_type=sentence_type, textplot=textplot, audio=recordings, progress=progress
            )
    else:
        # audio only condition
        return render_template(
                '/record/index.html', recording=sent_id, sentence=text,
            sent_type=sentence_type, textplot=None, audio=recordings, progress=progress
            )


@bp.route('/record/<string:session>/<string:trial_type>/<string:chapter_order>/post_trial')
@login_required
# one dummy argument a result of js code appending "/post_trial" to url
def post_trial(session, trial_type, chapter_order):
    """This function serves templates for the comparison plot
    or post_trial auditory feedback."""

    print('function entered')
    # Get user context
    #print('function entered')
    db = get_db()
    user_id = g.user['id']

    user_dict = get_user_state(user_id)
    condition = user_dict.get_condition()
    #print('condition: ' + condition)

    progress = get_progress(session, chapter_order, trial_type)

    # Query user recording
    user_audio = db.execute(
        'SELECT trial_id, sent_id'
        ' FROM recordings WHERE session_number=? AND user_id=? AND sent_order=?'
        ' ORDER BY created DESC',
        (session, user_id, chapter_order)
    ).fetchall()

    # Get actual ids
    sent_id = user_audio[0]['sent_id']
    trial_id = user_audio[0]['trial_id']

    # Query native audio
    sentence = db.execute(
        'SELECT audio_path, text'
        ' FROM chapters WHERE sent_id=?'  # p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC',
        (sent_id,)
    ).fetchall()

    # Avoid breaking app if no trial_id
    if trial_id:
        plot_path = trial_id + '.png'
    else:
        print("No audio was processed")
        plot_path = None

    recording_path = user_audio[0]['trial_id'] + '.wav'

    text = sentence[0]['text']

    # Render templates by condition
    if condition == 'a':
        return render_template(
            '/record/post_trial.html', sentence=text, recording=recording_path,
            plot=plot_path, original_audio=sent_id, progress=progress
        )

    else:
        return render_template(
            '/record/post_trial.html', sentence=text,
            recording=recording_path, plot=None, original_audio=sent_id, progress=progress
        )


@bp.route('/record/<string:session>/<string:trial_type>/<string:chapter_order>/post_trial/next_chapter')
@login_required
def next_chapter(session, trial_type, chapter_order):
    """Reroute to the next sentence trial."""

    # zero indexing so one less than real length
    # sequence = {
    #     'pre_train': 7,
    #     'training': 31,
    #     'post_train': 7
    # }
    trial_length = {
     'pre_train': 7,
     'training': 30,
     'post_train': 7,
    }

    # Get user specific info
    user_id = str(g.user['id'])
    user_dict = user_state(user_id)
    trial_length = user_dict.get_trial_length(session, trial_type)

    # Hardcoded list
    trial_type_list = ['pre_train', 'training', 'post_train']


    # Cast to int in order to run int operations
    chapter_order_int = int(chapter_order)

    # If the current chapter is less than the total add one
    if chapter_order_int < int(trial_length):

        chapter_order_int += 1
        chapter_order = str(chapter_order_int)
        return redirect(url_for('/record.record', chapterorder=chapter_order, session=session, trial_type=trial_type))

    # This part of the code got very hardcoded when automatic
    # notification was added.

    # If it's the third session and we reached the end it's over
    elif session == 'Session 3':
        if trial_type == 'pre_train':
            # TODO: send thank you message
            #notify('done', )

            return redirect(url_for('/record.end_message'))

    # if it's the last sentence
    elif int(chapter_order) == int(trial_length):

        # For the first two sessions we want to serve the instruction templates
        if session != 'Session 3':
            # Check which template to serve
            if trial_type == 'pre_train':
                return redirect(url_for('/instructions.training', is_session=True))
            elif trial_type == 'training':
                return redirect(url_for('/instructions.post_training'))
            elif trial_type == 'post_train':

                # If finished add to notification cue for session 2
                if session == 'Session 1':
                    notify_next_week(user_id, 'Session 2')
                else:
                    notify_next_week(user_id, 'Session 3')

                return redirect(url_for('/record.end_message'))

        # If last sentence but not last trial, serve 0 for next trial
        elif trial_type != trial_type_list[-1]:
            new_trial_type_index = \
                trial_type_list.index(trial_type) + 1
            new_trial_type = trial_type_list[new_trial_type_index]
            chapter_order = 0

            return redirect(url_for('/record.record', chapterorder=chapter_order, session=session, trial_type=new_trial_type))

    else:
        # when all else fails it must be over
        return redirect(url_for('/record.end_message'))


@bp.route('/audio_process/participant_recordings/<string:filename>')
@login_required
def return_plot_file(filename):
    """Get the comparison plot"""
    print('plot filename:', filename)
    dir = os.path.join(current_app.root_path, '../participant_recordings')
    return send_from_directory(dir, filename, as_attachment=True)

@bp.route('/textplot/<string:chaptername>/<string:filename>')
@login_required
def return_textplot_file(chaptername, filename):
    """Get the orthographic plot"""

    path = os.path.join(current_app.root_path, '../Recordings/', chaptername)

    return send_from_directory(path, filename, as_attachment=True)


@bp.route('/done')
@login_required
def end_message():
    return 'Done!'
