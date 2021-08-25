import sqlite3
import os


def init_email_db():

    db = sqlite3.connect('base.sqlite')

    with open('/Users/anton/PycharmProjects/FlaskTutorial/notify_users/email_schema.sql') as f:
        db.executescript(f.read())
    db.commit()

def get_flaskr_db():

    if os.path.isfile('./instance/flaskr.sqlite'):
        db = sqlite3.connect('./instance/flaskr.sqlite',
        detect_types=sqlite3.PARSE_DECLTYPES
        )
        db.row_factory = sqlite3.Row
    else:
        db = sqlite3.connect('./instance/flaskr.sqlite')
        with open('/Users/anton/PycharmProjects/FlaskTutorial/flaskr/schema.sql') as f:
            db.executescript(f.read())
        db.commit()
    return db

def connect_email_db():

    if os.path.isfile('base.sqlite'):
        db = sqlite3.connect('base.sqlite',
        detect_types=sqlite3.PARSE_DECLTYPES
        )
        db.row_factory = sqlite3.Row
    else:
        db = sqlite3.connect('base.sqlite')
        with open('/Users/anton/PycharmProjects/FlaskTutorial/notify_users/email_schema.sql') as f:
            db.executescript(f.read())
        db.commit()
    return db

