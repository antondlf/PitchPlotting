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


bp = Blueprint('/ns_task', __name__)

bp.route('/ns_task/<int:trial_order')
def display_trial(trial_order):

    user_id = g.user['id']

    current_trial_pair = ('11144_Il_ladro(S)_0_9dea', '11144_Il_brodo(S)_0_79e9')#some query statement on whatever structure we build returning a tuple of filenames

