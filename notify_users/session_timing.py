import datetime
import pickle
from flaskr.db import get_db
from notify_users.auto_email import notify


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


