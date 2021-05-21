from flask import (
    Blueprint, flash,  current_app, g, redirect, render_template, request, url_for, send_from_directory
)
from flaskr.auth import login_required

from flaskr.db import get_db

from werkzeug.exceptions import abort

from pitch_track.audio_processing import process_recording

from pitch_track.user_dict import user_state

import os


def get_user_state(user_id):
    if 'user_dict' not in g:
        g.user_dict = user_state(user_id)

    return g.user_dict

bp = Blueprint('/instructions', __name__)

@bp.route('/instructions/intro')
@login_required
def intro():
    return render_template('/Instructions/Introduction.html')

@bp.route('/instructions/test_recordings')
@login_required
def test_recordings():
    return render_template('/Instructions/Test_instructions.html')

@bp.route('/instructions/training')
@login_required
def training():
    user_id = g.user['id']
    condition = get_user_state(user_id).get_condition()

    return render_template('/Instructions/training.html', condition=condition)

@bp.route('/instructions/<string:filename>')
@login_required
def get_image(filename):
    path = os.path.join(current_app.root_path, '../instructions_pics')
    return send_from_directory(path, filename, as_attachment=True)