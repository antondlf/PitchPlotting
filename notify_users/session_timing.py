import datetime
import pickle
from flaskr.db import get_db
from notify_users.auto_email import notify


def id2email(user_id):

    db = get_db()

    # Get username
    username = db.execute(
        "SELECT username FROM user WHERE id=?",
        (user_id,)
    ).fetchall()[0]['username']

    # Get user email
    user_email = db.execute(
        "SELECT email FROM email_data WHERE username=?",
        (username,)
    ).fetchall()[0]['email']

    return user_email

def reminder_cue(user_id, notification_session):
    """Removes initial notification and adds user email to a
    cue where they will be reminded two days later to complete the next
    session.
    """
    db = get_db()

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

def send_notifications():
    """Checks if it is time to send a new notification and automatically
    notifies the user of the new session."""

    time_now = datetime.datetime.now()

    db = get_db()
    notification_cue = db.execute(
        "SELECT * FROM notifications"
    ).fetchall()

    for user in notification_cue:

        notification_time = pickle.load(user['time'])

        if time_now > notification_time:

            email = id2email(user['user_id'])

            if user['is_reminder'] == 'False':

                reminder_cue(user['user_id'], user['next_session'])


                notify(user['next_session'], email)

            else:
                notify(user['next_session'], email, is_reminder=True)

            db.execute(
                "DELETE FROM notifications WHERE user_id=?",
                (user['user_id'])
            )
            db.commit()


