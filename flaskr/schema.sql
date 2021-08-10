DROP TABLE IF EXISTS email;
DROP TABLE IF EXISTS notifications;
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS recordings;
DROP TABLE IF EXISTS chapters;
DROP TABLE IF EXISTS userdata;


CREATE TABLE email_data (
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL
);

CREATE TABLE notifications(
    email INTEGER,
    notification_time BLOB NOT NULL,
    next_session TEXT NOT NULL,
    is_reminder TEXT NOT NULL
);

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
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
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);