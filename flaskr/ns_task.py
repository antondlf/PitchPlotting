from flask import (
    Blueprint, flash,  current_app, g, redirect, render_template, request, url_for, send_from_directory
)
from flaskr.auth import login_required

import sqlite3

import click

import random

import pandas as pd

import csv

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

    csv2sql(dir_path + '/../apportioned.csv')
    db.commit()


def get_ns_db():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    print(dir_path)
    #if 'ns_db' not in g:
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
        'FROM trial_order WHERE trial=?',
        (trial_order,)  # (user_id, trial_order,)
    ).fetchall()[0]

    # pre_recording = '11144_Il_ladro(S)_0_9dea.wav' #'1_Anna_lavora(Q)_0_9f1f.wav'#

    # post_recording = '11144_Il_brodo(S)_0_79e9.wav' #'2_Daria_brinda(S)_0_e2b7.wav' #

    # display_order = 0  # another query statement

    current_trial_pair = (pre_recording,
                          post_recording)  # some query statement on whatever structure we build returning a tuple of filenames

    first_recording = current_trial_pair[display_order] + '.wav'

    second_recording = current_trial_pair[display_order - 1] + '.wav'

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
            response, chosen_recording, bool_response)
        # return get_next_trial()
        return redirect(url_for('/ns_task.display_trial', trial_order=trial_order))

@bp.route('/ns_task/<int:trial_order>/next_trial')
def next_trial(trial_order):

    trial_order += 1
    return redirect(url_for('/ns_task.display_trial', trial_order=trial_order))


def register_response(db, user_id, trial_order, response, chosen_recording, bool_response):

    trial_metadata = db.execute(
        'SELECT * FROM trial_order '
        'WHERE trial=?',#'WHERE user_id=? AND trial=?',
        (trial_order,)#(user_id, trial_order,)
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
            'sent_group, pre_recording_id, pre_recording_sent, post_recording_id, '
            'post_recording_sent, display_order, chosen_recording_id, is_improved)'
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (user_id, learner_id, sent_typ, sent_group,
             pre_recording_id, pre_recording_sent,
             post_recording_id, post_recording_sent,
             display_order,
             chosen_recording,
             bool_response
             )
        )
        db.commit()


def get_trial_metadata(trial_order, user_id):
    db = get_ns_db()
    # Maybe add a sanity check here?
    pre_recording, post_recording, display_order = db.execute(
        'SELECT pre_recording_id, post_recording_id, display_order '
        'FROM trial_order WHERE trial=?',
        (trial_order,)  # (user_id, trial_order,)
    ).fetchall()[0]

    # pre_recording = '11144_Il_ladro(S)_0_9dea.wav' #'1_Anna_lavora(Q)_0_9f1f.wav'#

    # post_recording = '11144_Il_brodo(S)_0_79e9.wav' #'2_Daria_brinda(S)_0_e2b7.wav' #

    # display_order = 0  # another query statement

    current_trial_pair = (pre_recording,
                          post_recording)  # some query statement on whatever structure we build returning a tuple of filenames

    first_recording = current_trial_pair[display_order] + '.wav'

    second_recording = current_trial_pair[display_order - 1] + '.wav'

    return first_recording, second_recording, display_order


def csv2sql(path_to_csv):

    db = get_ns_db()

    cur = db.cursor()

    with open(path_to_csv, 'r') as f:

        rows = csv.reader(f)

        cur.executemany('INSERT INTO trial_order (user_id, username, trial, learner_id, sent_typ,'
            'sent_group, pre_recording_id, pre_recording_sent,'
            'post_recording_id, post_recording_sent, display_order)'
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',rows)

    db.commit()


def input_trials(path_to_csv):
    data = pd.read_csv(path_to_csv)
    db = get_ns_db()
    trial_counter = 0
    for row in data.iterrows():
        #print('function entered')

        row_data = row[1]

        #try:

        paired_row = data.sample(1)
        #print(paired_row)
        # paired_row = data.loc[(data['user_id'] == row_data['user_id']) &
        #                       (data['trial_type'] == row_data['trial_id']) &
        #                       (data['sent_type'] == row_data['sent_type'])&
        #                       (data['sent_group'] == row_data['sent_group'])
        # ][0]
        #print(row[1]['trial_id'])

        display_order = random.choice([0,1])

        db.execute(

            'INSERT INTO trial_order'
            '(user_id, username, trial, learner_id, sent_typ,'
            'sent_group, pre_recording_id, pre_recording_sent,'
            'post_recording_id, post_recording_sent, display_order)'
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (
                1,
                'test',
                trial_counter,
                row_data['user_id'],
                row_data['sent_type'],
                row_data['sent_group'],
                row_data['trial_id'],
                row_data['sent_id'],
                paired_row['trial_id'].item(),
                paired_row['sent_id'].item(),
                display_order,
            )
        )
        db.commit()

        trial_counter += 1
        # except:
        #     print(IndexError('Index out of bounds'))
        #     #break


if __name__ == '__main__':

    init_ns_db()

