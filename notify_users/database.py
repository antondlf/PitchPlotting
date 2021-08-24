import sqlite3
import os
from email_management import start_experiment


def get_flaskr_db():

    if os.path.isfile('./instance/flaskr.sqlite'):
        db = sqlite3.connect('./instance/flaskr.sqlite',
        detect_types=sqlite3.PARSE_DECLTYPES
        )
        db.row_factory = sqlite3.Row
    else:
        db = sqlite3.connect('./instance/base.sqlite')
        with open('/Users/anton/PycharmProjects/FlaskTutorial/flaskr/schema.sql') as f:
            db.executescript(f.read())
        db.commit()
    return db

def connect_email_db():

    if os.path.isfile('./instance/base.sqlite'):
        db = sqlite3.connect('./instance/base.sqlite',
        detect_types=sqlite3.PARSE_DECLTYPES
        )
        db.row_factory = sqlite3.Row
    else:
        db = sqlite3.connect('./instance/base.sqlite')
        with open('/Users/anton/PycharmProjects/FlaskTutorial/notify_users/email_schema.sql') as f:
            db.executescript(f.read())
        db.commit()
    return db


def main():

    start_experiment('notify_users/emails.txt')





if __name__ == '__main__':

    main()