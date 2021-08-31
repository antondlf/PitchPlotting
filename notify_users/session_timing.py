import datetime
import pickle
import click
from database import get_flaskr_db, connect_email_db
from auto_email import notify, server_login


def id2email(user_id):

    flaskr_db = get_flaskr_db()

    email_db = connect_email_db()

    # Get username
    username = flaskr_db.execute(
        "SELECT username FROM user WHERE id=?",
        (user_id,)
    ).fetchall()[0]['username']
    print(username)

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
@click.option('--password', default=None)
def send_notifications(password):
    """Checks if it is time to send a new notification and automatically
    notifies the user of the new session."""

    time_now = datetime.datetime.now()

    db = get_flaskr_db()
    notification_cue = db.execute(
        "SELECT * FROM notifications"
    ).fetchall()

    server = server_login(password)

    counter = 0

    for user in notification_cue:
        click.echo('user {} has a notification in the cue'.format(str(user['user_id'])))
        notification_time = datetime.datetime.strptime(user['notification_time'], '%Y-%m-%d %H:%M:%S.%f')
        click.echo(print(time_now, notification_time))
        click.echo(print())
        click.echo(print(time_now > notification_time))

        if time_now > notification_time:
            click.echo("user {}'s notification is due".format(str(user['user_id'])))
            counter += 1
            email = id2email(user['user_id'])

            if user['is_reminder'] == 'False':
                click.echo("user {}'s notification is not a reminder". format(str(user['user_id'])))
                reminder_cue(user['user_id'], user['next_session'])
                click.echo("a reminder was added for user {}".format(str(user['user_id'])))

                notify(user['next_session'], email, server=server)
                click.echo("user {}'s notification was sent".format(str(user['user_id'])))

            else:
                click.echo("user {}'s notification is a reminder".format(str(user['user_id'])))
                notify(user['next_session'], email, server=server, is_reminder=True)
                click.echo("user {}'s notification was sent".format(str(user['user_id'])))
            print(user['user_id'], type(user['user_id']))
            db.execute(
                "DELETE FROM notifications WHERE user_id=?",
                (str(user['user_id']),)
            )
            db.commit()

    server.quit()
    click.echo('{} scheduled notifications sent'.format(str(counter)))


if __name__ == '__main__':
    send_notifications()
