from flask import (
    Blueprint, flash,  current_app, g, redirect, render_template, request, url_for, send_from_directory
)
from flaskr.auth import login_required

import sqlite3

import click

from werkzeug.exceptions import abort

from flaskr.audio_processing import process_recording

from flaskr.user_dict import user_state

from flaskr.notification_cue import notify_next_week

import os

@click.command('init-ns-db')
def init_ns_db():

    dir_path = os.path.dirname(os.path.realpath(__file__))

    db = sqlite3.connect(dir_path + '/../instance/ns_base.sqlite')

    with open(dir_path + '/ns_schema.sql') as f:
        db.executescript(f.read())
    db.commit()


def get_ns_db():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    if 'ns_db' not in g:
        ns_db = sqlite3.connect(
            dir_path + '/../instance/ns_base.sqlite',
            detect_types=sqlite3.PARSE_DECLTYPES
        )
    return ns_db


bp = Blueprint('/ns_task', __name__)

@bp.route('/ns_task/<int:trial_order>', methods=['GET', 'POST'])
@login_required
def display_trial(trial_order):

    user_id = g.user['id']

    db = get_ns_db()

    # Maybe add a sanity check here?
    pre_recording, post_recording, display_order = db.execute(
        'SELECT pre_recording_id, post_recording_id, display_order '
        'FROM trial_order WHERE user_id=? AND trial=?',
        (user_id, trial_order)
    ).fetchall()[0]

    #pre_recording = '11144_Il_ladro(S)_0_9dea.wav' #'1_Anna_lavora(Q)_0_9f1f.wav'#

    #post_recording = '11144_Il_brodo(S)_0_79e9.wav' #'2_Daria_brinda(S)_0_e2b7.wav' #

    #display_order = 0  # another query statement

    current_trial_pair = (pre_recording,
                          post_recording)  # some query statement on whatever structure we build returning a tuple of filenames

    first_recording = current_trial_pair[display_order]

    second_recording = current_trial_pair[display_order - 1]

    if request.method == 'GET':

        return render_template('/ns_task/ns_task.html', first_recording=first_recording, second_recording=second_recording)

    elif request.method == 'POST':

        response = request.json['value']

        if response == 'first':
            chosen_recording = first_recording
            if display_order == 0:

                bool_response = False

            elif display_order == 1:

                bool_response = True

            else:
                bool_response = None
                print('error, display order is outside domain')
            print('trial response:', bool_response)

        elif response == 'second':
            chosen_recording = second_recording
            if display_order == 0:

                bool_response = True

            elif display_order == 1:

                bool_response = False

            else:
                bool_response = None
                print('error, display order is outside domain')
            print('trial response:', bool_response)

        else:
            print(response)
            print('some error has ocurred')

        register_response(
            db, user_id, trial_order,
            response, bool_response, chosen_recording)

        trial_order += 1
        # return get_next_trial()
        return redirect(url_for('/ns_task.display_trial', trial_order=trial_order))


def register_response(db, user_id, trial_order, response, bool_response, chosen_recording):

    trial_metadata = db.execute(
        'SELECT * FROM trial_order'
        'WHERE user_id=? AND trial=?',
        (user_id, trial_order)
    ).fetchall()[0]

    row_id, user_id_fromdb, username, trial, learner_id, sent_typ,\
    sent_group,pre_recording_id,pre_recording_sent,\
    post_recording_id,post_recording_sent,\
    display_order = trial_metadata

    if user_id_fromdb != user_id:
        ValueError('The user_id number taken from the database does not equal the one queried')

    else:

        db.execute(
            'INSERT INTO ns_data (rater_id, learner_id, sent_typ,'
            'sent_group, pre_recording_id, pre_recording_sent, post_recording_id'
            'post_recording_sent, display_order, chosen_recording_id, is_improved)'
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (user_id, learner_id, sent_typ, sent_group,
             pre_recording_id, pre_recording_sent,
             post_recording_id, post_recording_sent,
             display_order, chosen_recording, bool_response)
        )
        db.commit()


if __name__ == '__main__':

    init_ns_db()

