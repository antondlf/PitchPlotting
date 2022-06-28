from flask import (
    Blueprint, flash, current_app, g, render_template, send_from_directory
)
from auth import login_required

from user_dict import user_state

import os



bp = Blueprint('/instructions', __name__)


# Frontend utility for serving html templates with instructions

def get_user_state(user_id):
    if 'user_dict' not in g:
        g.user_dict = user_state(user_id)

    return g.user_dict


@bp.route('/instructions/intro/<string:post>')
@login_required
def intro(post):

    return render_template('Instructions/Introduction.html', post=post)


@bp.route('/instructions/test_recordings/<string:post>')
@login_required
def test_recordings(post):
    user_id = g.user['id']
    condition = get_user_state(user_id).get_condition()
    if condition == 'Error, user not properly registered. Contact the support email to get a new account.':
        return flash(condition)

    post = post.replace('_', ' ')

    post_name = post.lower()

    return render_template(
            'Instructions/Test_instructions.html',
            post=post, post_name=post_name)


@bp.route('/instructions/training/<string:session>/<string:is_session>')
@login_required
def training(session, is_session):
    user_id = g.user['id']
    condition = get_user_state(user_id).get_condition()
    if condition == 'Error, user not properly registered. Contact the support email to get a new account.':
        return flash(condition)

    if is_session == 'True':
        print('session is true')
        what_next = 'training'
    elif is_session == 'False':
        what_next = 'menu'

    return render_template(
            'Instructions/training.html',
            condition=condition,
            next_panel=what_next,
            session=session
    )


@bp.route('/instructions/<string:session>/post_train')
@login_required
def post_training(session):
    return render_template('Instructions/post_test.html', session=session)


@bp.route('/instructions/<string:filename>')
@login_required
def get_image(filename):
    path = os.path.join(current_app.root_path, 'instructions_pics')
    #print(path)
    return send_from_directory(path, filename, as_attachment=True)


@bp.route('/mic_test/<string:post>')
@login_required
def mic_test(post):

    return render_template('Instructions/mic_test.html', post=post)