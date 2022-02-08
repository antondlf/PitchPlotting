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

bp = Blueprint('/survey', __name__)

@bp.route('/equipment_survey/<string:post>', methods=['POST', 'GET'])
@login_required
def equipment_survey(post):
    """Renders the equipment survey"""

    if request.method == 'GET':

        return render_template('/survey/equipment_survey.html', post=post)

    elif request.method == 'POST':

        post = post.replace('_', ' ')

        post_name = post.lower()
        user_id = g.user['id']

        input_form2db(request.form, user_id, post)
        print(request.form)
        return render_template('/Instructions/Test_instructions.html', post=post, post_name=post_name)


def input_form2db(form, user_id, session):

    db = get_db()

    device = form['device']
    system = form['system']
    browser = form['browser']
    phones = form['phones']
    mic = form['mic']
    comments = form['comments']

    if device == '':
        device = form['other_device']

    if system == '':
        system = form['other_system']

    if mic == '':
        mic = form['other_mic']

    if browser == '':
        browser = form['other_browser']

    db.execute(
        'INSERT INTO survey '
        '(user_id, session_number, device, system, browser, mic, headphones, comments)'
        'VALUES (?, ?, ?, ?, ?, ?, ?)',
        (
            user_id, session, device, system, browser, mic, phones, comments
        )
    )
    db.commit()

    try:

        db.execute(
            'SELECT FROM survey WHERE user_id=?',
            (user_id)
        ).fetchall()[0]

    except:

        return print('Error inputing into db')