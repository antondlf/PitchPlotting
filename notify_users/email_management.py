import click
from auto_email import server_login
from database import get_flaskr_db, connect_email_db
from werkzeug.security import generate_password_hash
from auto_email import notify

# This script creates a click command that starts the experiment
# from an uploaded list of emails (this flow is to be deprecated
# in favor of individual sign ups through the flask app.


def input_email_db(db, username, email):
    """Inputs emails into db"""

    db.execute(
        'INSERT INTO email_data (username, email)'
        ' VALUES (?, ?)',
        (username, email)
    )
    db.commit()

# to be deprecated and workflow reversed
# (Account sign up triggers email reminder)
def register_account(username, password):
    """Registers an account in flask for each email"""

    db = get_flaskr_db()
    db.execute(
        'INSERT INTO user (username, password) VALUES (?, ?)',
        (username, generate_password_hash(password))
    )
    db.commit()

# Click command to start experiment
@click.command('notify_new')
@click.option('--password', default=None)
def notify_new(password):
    """Checks for emails in flaskr db"""

    user_counter = 0
    server = server_login(password)
    flaskr_db = get_flaskr_db()
    email_db = connect_email_db()
    email_list = flaskr_db.execute(
        'SELECT * FROM new_emails'
    ).fetchall()
    print(email_list[0])

    for row in email_list:
        user_counter += 1
        iter_email = row['email']
        iter_username = row['username']

        input_email_db(email_db, iter_username, iter_email)

        notify("Session_1", iter_email, server=server, username=iter_username, is_reminder=False)

        flaskr_db.execute(
            'DELETE FROM new_emails WHERE email=?',
            (iter_email,)
        )
        flaskr_db.commit()
    click.echo('{} new users have been registered and notified'.format(user_counter))



if __name__ == '__main__':

    notify_new()
