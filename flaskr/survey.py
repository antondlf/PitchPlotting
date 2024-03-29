from flask import (
    Blueprint, flash,  current_app, g, redirect, render_template, request, url_for, send_from_directory
)
from flaskr.auth import login_required

from flaskr.db import get_db

from flaskr.ns_task import get_ns_db


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
        #print(request.form)
        return render_template('/Instructions/Test_instructions.html', post=post, post_name=post_name)


def input_form2db(form, user_id, session):

    db = get_db()

    device = form['device']
    system = form['system']
    browser = form['browser']
    phones = form['phones']
    mic = form['mic']
    comments = form['comments']

    db.execute(
        'INSERT INTO survey '
        '(user_id, session_number, device, system, browser, mic, headphones, comments)'
        'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
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


@bp.route('/final_survey', methods=['POST', 'GET'])
@login_required
def final_survey():

    if request.method == 'GET':

        return render_template('/survey/final_survey.html')

    elif request.method == 'POST':

        user_id = g.user['id']

        final_survey_input(request.form, user_id)

        return redirect(url_for('/record.end_message', session='Session 3'))


def final_survey_input(form, user_id):

    db = get_db()

    what = form['what_learn']
    satisfaction = form['satisfaction']
    tech_issues = form['tech_issues']
    comments = form['final_comments']

    db.execute(

        'INSERT INTO final_survey'
        '(user_id, what_learn, satisfaction, tech_issues, comments)'
        'VALUES (?, ?, ?, ?, ?)',
        (
            user_id, what, satisfaction, tech_issues, comments
        )
    )
    db.commit()


@bp.route('/rater_survey', methods=['POST', 'GET'])
@login_required
def rater_survey():
    """Renders the equipment survey"""

    if request.method == 'GET':

        return render_template('/survey/rater_survey.html')

    elif request.method == 'POST':

        user_id = g.user['id']

        rater_survey_input(request.form, user_id)
        #print(request.form)
        return render_template('/Instructions/rater_instructions.html')


def rater_survey_input(form, user_id):

    db = get_ns_db()

    age = form['age']
    gender = form['gender']
    grow_up = form['grow_up']
    live_currently = form['live_currently']

    db.execute(
        'INSERT INTO rater_survey '
        '(rater_id, age, gender, grow_up, live_currently)'
        'VALUES (?, ?, ?, ?, ?)',
        (
            user_id, age, gender, grow_up, live_currently
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


@bp.route('/final_rater_survey', methods=['POST', 'GET'])
@login_required
def final_rater_survey():
    """Renders the equipment survey"""

    if request.method == 'GET':

        return render_template('/ns_task/completed.html')

    elif request.method == 'POST':

        user_id = g.user['id']

        final_rater_input(request.form, user_id)
        #print(request.form)
        return render_template('/ns_task/ns_done.html')


def final_rater_input(form, user_id):

    db = get_ns_db()

    comments = form['comments']

    db.execute(
        'INSERT INTO final_survey_rater '
        '(rater_id, comments)'
        'VALUES (?, ?)',
        (
            user_id, comments
        )
    )
    db.commit()

    try:

        db.execute(
            'SELECT FROM final_survey_rater WHERE user_id=?',
            (user_id)
        ).fetchall()[0]

    except:

        return print('Error inputing into db')

