import sqlite3
import os


def init_email_db():

    db = sqlite3.connect('./backend_instance/base.sqlite')

    with open('./notify_users/email_schema.sql') as f:
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
        with open('./flaskr/schema.sql') as f:
            db.executescript(f.read())
        db.commit()
    return db

def connect_email_db():

    if os.path.isfile('./backend_instance/base.sqlite'):
        db = sqlite3.connect('./backend_instance/base.sqlite',
        detect_types=sqlite3.PARSE_DECLTYPES
        )
        db.row_factory = sqlite3.Row
    else:
        db = sqlite3.connect('base.sqlite')
        with open('./notify_users/email_schema.sql') as f:
            db.executescript(f.read())
        db.commit()
    return db

