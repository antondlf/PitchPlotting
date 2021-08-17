from flaskr.db import get_db
import datetime

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