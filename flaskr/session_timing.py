import datetime
import pickle
from flaskr.db import get_db
from flaskr.auto_email import notify

def notify_next_week(user_id, notification_session):
    """Adds user email to a cue where they will be notified about
    the next session a week later"""

    db = get_db()

    # Get notification time for next week
    notification_time = datetime.datetime.now() + datetime.timedelta(days=7)

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

    # Delete any prior entries with that email to avoid duplicate emails
    db.execute(
        "DELETE FROM notifications WHERE email=?",
        (user_email,)
    )
    db.commit()

    # Insert email, next week's notification time
    # The session to be notified, and whether this is a reminder
    # Or the initial notification
    db.execute(
        "INSERT INTO notifications (email, notification_time, notification_session, is_reminder)",
        (user_email, notification_time, notification_session, 'False',)
    )
    db.commit()


def reminder_cue(email, notification_session):
    """Removes initial notification and adds user email to a
    cue where they will be reminded two days later to complete the next
    session.
    """
    db = get_db()

    reminder_time = datetime.datetime.now() + datetime.timedelta(days=2)

    #
    db.execute(
        "DELETE FROM notifications WHERE email=?",
        (email,)
    )
    db.commit()

    db.execute(
        "INSERT INTO notifications (email, notification_time, next_session, is_reminder)",
        (email, reminder_time, notification_session, 'True',)
    )

def send_notifications():
    """Checks if it is time to send a new notification and automaticallly
    notifies the user of the new session."""

    time_now = datetime.datetime.now()

    db = get_db()
    notification_cue = db.execute(
        "SELECT * FROM notifications"
    ).fetchall()

    for user in notification_cue:

        notification_time = pickle.load(user['time'])

        if time_now > notification_time:

            if user['is_reminder'] == 'False':

                reminder_cue(user['email'], user['next_session'])

                notify(user['next_session'], user['email'])

            else:
                notify(user['next_session'], user['email'], is_reminder=True)

            db.execute(
                "DELETE FROM notifications WHERE email=?",
                (user['email'])
            )
            db.commit()