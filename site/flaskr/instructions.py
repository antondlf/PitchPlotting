from flask import (
    Blueprint, flash, current_app, g, render_template, send_from_directory
)
from site.flaskr.auth import login_required

from site.flaskr.user_dict import user_state

import os


def get_user_state(user_id):
    if 'user_dict' not in g:
        g.user_dict = user_state(user_id)

    return g.user_dict


bp = Blueprint('/instructions', __name__)


@bp.route('/instructions/intro')
@login_required
def intro():
    return render_template('Instructions/Introduction.html')


@bp.route('/instructions/test_recordings/<string:is_session>')
@login_required
def test_recordings(is_session):
    user_id = g.user['id']
    condition = get_user_state(user_id).get_condition()
    if condition == 'Error, user not properly registered. Contact the support email to get a new account.':
        return flash(condition)

    if is_session == 'True':
        print('session is true')
        what_next = 'pre_train'
    elif is_session == 'False':
        what_next = 'menu'

    return render_template(
            'Instructions/Test_instructions.html',
            next_panel=what_next)


@bp.route('/instructions/training/<string:is_session>')
@login_required
def training(is_session):
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
            next_panel=what_next)


@bp.route('/instructions/post_train')
@login_required
def post_training():
    return render_template('Instructions/post_test.html')


@bp.route('/instructions/<string:filename>')
@login_required
def get_image(filename):
    path = os.path.join(current_app.root_path, 'instructions_pics')
    print(path)
    return send_from_directory(path, filename, as_attachment=True)