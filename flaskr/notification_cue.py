from flaskr.db import get_db
import datetime

def notify_next_week(user_id, notification_session):
    """Adds user email to a cue where they will be notified about
    the next session a week later"""

    db = get_db()

    # Get notification time for next week
    notification_time = datetime.datetime.now() + datetime.timedelta(days=7)

    # Delete any prior entries with that email to avoid duplicate emails
    db.execute(
        "DELETE FROM notifications WHERE user_id=?",
        (user_id,)
    )
    db.commit()

    # Insert email, next week's notification time
    # The session to be notified, and whether this is a reminder
    # Or the initial notification
    db.execute(
        "INSERT INTO notifications (user_id, notification_time, notification_session, is_reminder)",
        (user_id, notification_time, notification_session, 'False',)
    )
    db.commit()