from flask import (
    Blueprint, flash,  current_app, g, redirect, render_template, request, url_for, send_from_directory
)
from flaskr.auth import login_required

import sqlite3

from werkzeug.exceptions import abort

from flaskr.audio_processing import process_recording

from flaskr.user_dict import user_state

from flaskr.notification_cue import notify_next_week

import os


# def get_ns_db():
#     dir_path = os.path.dirname(os.path.realpath(__file__))
#     if 'ns_db' not in g:
#         g.ns_db = sqlite3.connect(
#             current_app.config["DATABASE"],
#             detect_types=sqlite3.PARSE_DECLTYPES
#         )
#         g.db.row_factory = sqlite3.Row
#     return g.db

bp = Blueprint('/ns_task', __name__)

@bp.route('/ns_task/<int:trial_order>', methods=['GET', 'POST'])
@login_required
def display_trial(trial_order):

    user_id = g.user['id']

    pre_recording = '11144_Il_ladro(S)_0_9dea.wav' #'1_Anna_lavora(Q)_0_9f1f.wav'#

    post_recording = '11144_Il_brodo(S)_0_79e9.wav' #'2_Daria_brinda(S)_0_e2b7.wav' #

    current_trial_order = 0  # another query statement

    current_trial_pair = (pre_recording,
                          post_recording)  # some query statement on whatever structure we build returning a tuple of filenames

    first_recording = current_trial_pair[current_trial_order]

    second_recording = current_trial_pair[current_trial_order - 1]

    if request.method == 'GET':

        return render_template('/ns_task/ns_task.html', first_recording=first_recording, second_recording=second_recording)

    elif request.method == 'POST':

        response = request.json['value']

        if response == 'first':

            if current_trial_order == 0:

                bool_response = False

            elif current_trial_order == 1:

                bool_response = True
            print('trial response:', bool_response)

        elif response == 'second':

            if current_trial_order == 0:

                bool_response = True

            elif current_trial_order == 1:

                bool_response = False
            print('trial response:', bool_response)

        else:
            print(response)
            print('some error has ocurred')

        # return get_next_trial()
        return render_template('/ns_task/ns_task.html', first_recording=first_recording, second_recording=second_recording)

