import sqlite3
import os


# Two different databases are created, one holds emails and the other
# is the flask app db. This script provides utilities for access to them.

def init_email_db():

    dir_path = os.path.dirname(os.path.realpath(__file__))

    db = sqlite3.connect(dir_path + '/../backend_instance/base.sqlite')

    with open(dir_path + '/email_schema.sql') as f:
        db.executescript(f.read())
    db.commit()


def get_flaskr_db():

    dir_path = os.path.dirname(os.path.realpath(__file__))

    if os.path.isfile(dir_path + '/../site/instance/flaskr.sqlite'):
        db = sqlite3.connect(dir_path + '/../site/instance/flaskr.sqlite',
        detect_types=sqlite3.PARSE_DECLTYPES
        )
        db.row_factory = sqlite3.Row
    else:
        db = sqlite3.connect(dir_path + '/../site/instance/flaskr.sqlite')
        with open(dir_path + '/../site/flaskr/schema.sql') as f:
            db.executescript(f.read())
        db.commit()
    return db


def connect_email_db():

    dir_path = os.path.dirname(os.path.realpath(__file__))

    if os.path.isfile(dir_path + '/../backend_instance/base.sqlite'):
        db = sqlite3.connect(dir_path + '/../backend_instance/base.sqlite',
        detect_types=sqlite3.PARSE_DECLTYPES
        )
        db.row_factory = sqlite3.Row
    else:
        db = sqlite3.connect(dir_path + '/../backend_instance/base.sqlite')
        with open(dir_path + '/../notify_users/email_schema.sql') as f:
            db.executescript(f.read())
        db.commit()
    return db

