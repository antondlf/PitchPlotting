import datetime
import pickle
import click
from database import get_flaskr_db, connect_email_db
from notify_users.auto_email import notify, server_login


def id2email(user_id):

    flaskr_db = get_flaskr_db()

    email_db = connect_email_db()

    # Get username
    username = flaskr_db.execute(
        "SELECT username FROM user WHERE id=?",
        (user_id,)
    ).fetchall()[0]['username']

    # Get user email
    user_email = email_db.execute(
        "SELECT email FROM email_data WHERE username=?",
        (username,)
    ).fetchall()[0]['email']

    return user_email

def reminder_cue(user_id, notification_session):
    """Removes initial notification and adds user email to a
    cue where they will be reminded two days later to complete the next
    session.
    """
    db = get_flaskr_db()

    reminder_time = datetime.datetime.now() + datetime.timedelta(days=2)

    #
    db.execute(
        "DELETE FROM notifications WHERE user_id=?",
        (user_id,)
    )
    db.commit()

    db.execute(
        "INSERT INTO notifications (user_id, notification_time, next_session, is_reminder)"
        "VALUES (?, ?, ?, ?)",
        (user_id, reminder_time, notification_session, 'True',)
    )


@click.command('send_notifications')
@click.argument('password')
def send_notifications(password):
    """Checks if it is time to send a new notification and automatically
    notifies the user of the new session."""

    time_now = datetime.datetime.now()

    db = get_flaskr_db()
    notification_cue = db.execute(
        "SELECT * FROM notifications"
    ).fetchall()

    server = server_login(password)

    for user in notification_cue:

        notification_time = pickle.load(user['time'])

        if time_now > notification_time:

            email = id2email(user['user_id'])

            if user['is_reminder'] == 'False':

                reminder_cue(user['user_id'], user['next_session'])

                notify(user['next_session'], email, server=server)

            else:
                notify(user['next_session'], email, server=server, is_reminder=True)

            db.execute(
                "DELETE FROM notifications WHERE user_id=?",
                (user['user_id'])
            )
            db.commit()

    server.quit()
    click.echo('All scheduled notifications sent')


if __name__ == '__main__':
    send_notifications()
