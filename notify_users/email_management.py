import click
import random
import diceware
from auto_email import server_login
from database import get_flaskr_db, connect_email_db, init_email_db
from werkzeug.security import generate_password_hash
from user_dict import create_user_dict
from auto_email import notify


def read_email_list(email_list):

    with open(email_list, 'r') as in_file:
        # TODO: add encryption
        emails = in_file.read().splitlines()
        print(emails)

    return emails


def input_email_db(username, email):
    db = connect_email_db()

    db.execute(
        'INSERT INTO email_data (username, email)'
        ' VALUES (?, ?)',
        (username, email)
    )
    db.commit()


def register_account(username, password):

    db = get_flaskr_db()
    db.execute(
        'INSERT INTO user (username, password) VALUES (?, ?)',
        (username, generate_password_hash(password))
    )
    db.commit()


def generate_group(group_list, username_list, db, server=None, group='a'):

    for i in range(len(group_list)):

        # Create a username and password
        username = username_list[i]
        password = diceware.get_passphrase()

        # Input into database
        input_email_db(username, group_list[i])
        register_account(username, password)

        # Notify the user to start the experiment
        notify("Session_1", group_list[i], server=server, username=username, password=password, is_reminder=False)

        # Generate user_dict
        user_id = db.execute(
            'SELECT id FROM user WHERE username=?',
            (username,)
        ).fetchall()[0]['id']
        create_user_dict(user_id, group=group)


def create_accounts(email_list, server=None):

    # Shuffle emails
    print(email_list)
    random.shuffle(email_list)
    print(email_list)

    # Get two groups
    half_len = int(len(email_list)/2)
    print(half_len)

    # Get two random groups
    group_a = email_list[:half_len]
    group_b = email_list[half_len:]

    db = get_flaskr_db()

    # Get random usernames
    with open(diceware.get_wordlist_path('en')) as in_file:
        wordlist = in_file.read().splitlines()
        username_list = random.choices(wordlist, k=len(email_list))

    # Apportion usernames to groups
    usernames_a = username_list[:half_len]
    usernames_b = username_list[half_len:]

    # Generate groups
    generate_group(group_a, usernames_a, db, server=server, group='a')
    generate_group(group_b, usernames_b, db, server=server, group='b')


@click.command('start-experiment')
@click.argument('email_list', type=click.Path(exists=True))
@click.option('--password', default=None)
def start_experiment(email_list, password):

    server = server_login(password)
    init_email_db()
    emails = read_email_list(email_list)
    create_accounts(emails, server=server)

    click.echo('Users registered and notifications sent.')

    server.quit()


if __name__ == '__main__':

    start_experiment()
