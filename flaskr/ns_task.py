from flask import (
    Blueprint, flash,  current_app, g, redirect, render_template, request, url_for, send_from_directory
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.auth import login_required

import sqlite3

import click

import random

import pandas as pd

import csv

import diceware


#from flaskr.db import get_db

#from werkzeug.exceptions import abort

#from flaskr.audio_processing import process_recording

#from flaskr.user_dict import user_state

#from flaskr.notification_cue import notify_next_week

import os


@click.command('init-ns-db')
def init_ns_db():

    dir_path = os.path.dirname(os.path.realpath(__file__))

    db = sqlite3.connect(dir_path + '/../instance/ns_base.sqlite')

    with open(dir_path + '/ns_schema.sql') as f:
        db.executescript(f.read())

    usernames = pd.read_csv(dir_path + '/../apportioned.csv').iloc[:, 0].unique()

    user_list = list()
    flaskr_db = sqlite3.connect(dir_path+'/../instance/flaskr.sqlite')

    csv2sql(dir_path + '/../apportioned.csv')

    for user in usernames:

        passwrd = diceware.get_passphrase()

        user_not_exists = register_rater(user, passwrd, flaskr_db)
        if user_not_exists:
            user_list.append(str((user, passwrd)))

        else:
            continue

    with open(dir_path + '/../users.txt', 'a') as f:
        for userpass in user_list:
            f.write(userpass + '\n')

    db.commit()


def get_ns_db():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    #print(dir_path)
    #if 'ns_db' not in g:
    ns_db = sqlite3.connect(
        dir_path + '/../instance/ns_base.sqlite',
        detect_types=sqlite3.PARSE_DECLTYPES
    )
    return ns_db


bp = Blueprint('/ns_task', __name__)


def route_user():

    username = g.user['username']

    db = get_ns_db()
    trial_list = db.execute(
        'SELECT trial_id FROM ns_data'
        ' WHERE rater_id=?'
        ' ORDER BY trial_id DESC',
        (username,)
    ).fetchall()

    if len(trial_list) == 0:

        last_trial = 0
        return redirect(url_for('/survey.rater_survey'))
    else:
        last_trial = trial_list[0][0] + 1

    progress = round((last_trial/511)*100)

    return redirect(url_for('/ns_task.display_trial', trial_order=last_trial))


def get_test_trial(trial_order,test_trial):

    # Users 11071, 11072, 11073
    test_trials = {0: ('11071_Angelo_giunge(S)_0_cb70', '11071_Livia_dorme(S)_0_458b'), # user 11071 set_1
    1: ('11072_Damiano_morde(Q)_0_0624', '11072_Giuliana_mangia(Q)_0_33e0'), # user 11072 set_2
    2: ('11073_La_ragione(S)_0_4770', '11073_La_balena(S)_0_56a1') # user 11073 set_4
     }

    current_test_trial = test_trials[trial_order]

    return render_template(
        '/ns_task/ns_task.html',
        trial_type='test trial',
        first_recording=current_test_trial[0],
        second_recording=current_test_trial[1],
        test_trial=test_trial
    )


@bp.route('/ns_task/<int:trial_order>', methods=['GET', 'POST'])
@bp.route('/ns_task/<int:trial_order>/<string:test_trial>', methods=['GET', 'POST'])
@login_required
def display_trial(trial_order, test_trial=False):

    if bool(test_trial) == True:

        get_test_trial(trial_order, test_trial)



    username = g.user['username']

    db = get_ns_db()

    # Maybe add a sanity check here?
    pre_recording, post_recording, display_order = db.execute(
        'SELECT pre_recording_id, post_recording_id, display_order '
        'FROM trial_order WHERE trial=? AND username=?',
        (trial_order, username,)
    ).fetchall()[0]

    # pre_recording = '11144_Il_ladro(S)_0_9dea.wav' #'1_Anna_lavora(Q)_0_9f1f.wav'#

    # post_recording = '11144_Il_brodo(S)_0_79e9.wav' #'2_Daria_brinda(S)_0_e2b7.wav' #

    # display_order = 0  # another query statement

    current_trial_pair = (pre_recording,
                          post_recording)  # some query statement on whatever structure we build returning a tuple of filenames
    trial_type = 'Interrogativa' if pre_recording.split('_')[-3][-2] == 'Q' else 'Enunciativa'

    if test_trial:
        trial_type = 'di test'

    first_recording = current_trial_pair[display_order] + '.wav'

    second_recording = current_trial_pair[display_order - 1] + '.wav'

    if request.method == 'GET':

        progress = round((trial_order / 511) * 100)

        return render_template('/ns_task/ns_task.html', trial_type=trial_type, first_recording=first_recording, second_recording=second_recording, progress=progress)

    elif request.method == 'POST':

        response = request.json['value']
        print(response)

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
        db = get_ns_db()
        print(db, 'db registration about to start')
        register_response(
            db, username, trial_order,
            response, chosen_recording, bool_response)
        # return get_next_trial()


@bp.route('/ns_task/<int:trial_order>/next_trial')
@bp.route('/ns_task/<int:trial_order>/<string:test_trial>/next_trial')
def next_trial(trial_order, test_trial = False):

    if bool(test_trial) == True:

        if trial_order == 2:
            return redirect(url_for('/instructions.rater_ready'))
        else:
            trial_order += 1
            return redirect(url_for('/ns_task.display_trial', trial_order=trial_order, test_trial=True))

    username = g.user['username']
    db = get_ns_db()
    trial_total = db.execute(
        'SELECT trial FROM trial_order'
        ' WHERE username=?'
        ' ORDER BY trial DESC',
        (username,)
    ).fetchall()[0][0]

    if trial_order == trial_total:

        return redirect(url_for('/survey.final_rater_survey'))

    if trial_order % 102 == 0:
        return render_template('/ns_task/session_over.html')
    # The number here indicates how often a break option is given
    elif trial_order % 20 == 0:
        trial_order += 1
        return render_template('/ns_task/break.html', trial_order=trial_order)

    else:
        trial_order += 1
        return redirect(url_for('/ns_task.display_trial', trial_order=trial_order))


def register_response(db, username, trial_order, response, chosen_recording, bool_response):

    #print('Registration has started')
    trial_metadata = db.execute(
        'SELECT * FROM trial_order '
        'WHERE trial=? AND username=?',#'WHERE user_id=? AND trial=?',
        (trial_order, username)#(user_id, trial_order,)
    ).fetchall()[0]

    row_id, username, trial, learner_id, sent_typ,\
    sent_group,pre_recording_id,pre_recording_sent,\
    post_recording_id,post_recording_sent,\
    display_order = trial_metadata

    #if user_id_fromdb != user_id:
    #    ValueError('The user_id number taken from the database does not equal the one queried')

    print('Database execution has started')
#    try:
    db.execute(
        'INSERT INTO ns_data (trial_id, rater_id, learner_id, sent_typ,'
        'sent_group, pre_recording_id, pre_recording_sent, post_recording_id, '
        'post_recording_sent, display_order, chosen_recording_id, is_improved)'
        'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (trial, username, learner_id, sent_typ, sent_group,
         pre_recording_id, pre_recording_sent,
         post_recording_id, post_recording_sent,
         display_order,
         chosen_recording,
         str(bool_response)
         )
    )
    db.commit()
#    except:
    #     print('Exception')
        #print('Exception')
        #sqlite3.OperationalError('syntax error')

    print()


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

        cur.executemany('INSERT INTO trial_order (username, trial, learner_id, sent_typ,'
            'sent_group, pre_recording_id, pre_recording_sent,'
            'post_recording_id, post_recording_sent, display_order)'
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',rows)

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


def register_rater(username, password, db):

    error = None

    sus_strings = ['crypto', 'NFT', '$', 'BTC ', 'Ukraine', 'Russia', 'Novy originalny', 'Support the fund', ' ']

    if not username:
        error = 'Username is required.'
    elif not password:
        error = 'Password is required.'
    #elif not email:
    #    error = 'Valid email is required.'
    elif len(username) > 20:
        error = 'Username entered is not valid'

    elif '>>' in username:

        error = "Username entered is not valid, disallowed characters are contained."

    elif ' ' in username:
        error = 'Username entered is not valid, please do not include spaces.'

    elif db.execute(
        'SELECT id FROM user WHERE username = ?', (username,)
    ).fetchone() is not None:
        error = 'User {} is already registered'.format(username)

    if error is None:
        db.execute(
            'INSERT INTO user (username, password) VALUES (?, ?)',
            (username, generate_password_hash(password))
        )
        db.commit()
        return True

    else:
        print(error)
        return False


if __name__ == '__main__':

    init_ns_db()

