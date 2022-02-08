DROP TABLE IF EXISTS notifications;
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS recordings;
DROP TABLE IF EXISTS chapters;
DROP TABLE IF EXISTS userdata;
DROP TABLE IF EXISTS new_emails;
DROP TABLE IF EXISTS survey;


CREATE TABLE notifications(
    user_id INTEGER,
    notification_time BLOB NOT NULL,
    next_session TEXT NOT NULL,
    is_reminder TEXT NOT NULL
);

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE new_emails(
    username TEXT UNIQUE NOT NULL,
    email TEXT NOT NULL
);

CREATE TABLE userdata (
    user_id INT NOT NULL,
    user_dict BLOB NOT NULL
);

CREATE TABLE recordings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  sent_order TEXT NOT NULL, --TODO: clarify naming
  experimental_condition TEXT NOT NULL,
  session_number TEXT NOT NULL,
  trial_type TEXT NOT NULL, --Only three categories encoded (7 categories encoded together with session_number
  trial_type_ord INT NOT NULL,
  sent_group TEXT NOT NULL, --TODO: Some sentences will not belong to any tracked group
  sent_type TEXT NOT NULL, --TODO: check if this is easy to encode (maybe str.endswith('?'))
  sent_id TEXT NOT NULL, --TODO: come up with sentence identifiers (change to sent_id)
  repetition TEXT NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  trial_id TEXT NOT NULL, --TODO: trial id creation (record.py)
  FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE chapters (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  sent_group TEXT NOT NULL,
  sent_type TEXT NOT NULL,
  sent_id TEXT NOT NULL,
  text TEXT NOT NULL,
  audio_path TEXT NOT NULL,
  textplot_path TEXT NOT NULL,
  precomputed_trace BLOB NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE survey (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_number TEXT NOT NULL,
    device TEXT NOT NULL,
    system TEXT NOT NULL,
    browser TEXT NOT NULL,
    mic TEXT NOT NULL,
    headphones TEXT NOT NULL,
    comments TEXT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);