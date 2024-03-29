import functools
from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

from flaskr.user_dict import create_user_dict

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        db = get_db()
        error = None

        sus_strings = ['crypto', 'NFT', '$', 'BTC ', 'Ukraine', 'Russia', 'Novy originalny', 'Support the fund', ' ']

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif not email:
            error = 'Valid email is required.'
        elif len(username) > 10:
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
            db.execute(
                'INSERT INTO new_emails (username, email, password) VALUES (?, ?, ?)',
                (username, email, password)
            )
            db.commit()
            user_id = db.execute(
                'SELECT id FROM user WHERE username=?',
                (username,)
            ).fetchall()[0]['id']
            create_user_dict(user_id)
            return redirect(url_for('auth.login'))
        flash(error)
    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            print('user not logged in')
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view



