DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS recordings;
DROP TABLE IF EXISTS chapters;
DROP TABLE IF EXISTS userdata;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE userdata (
    user_id TEXT UNIQUE NOT NULL,
    experimental_condition TEXT NOT NULL,
    chapter_list TEXT NOT NULL,
);

CREATE TABLE recordings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  chapter_id TEXT NOT NULL,
  trial_id TEXT NOT NULL,
  is_baseline TEXT NOT NULL,
  FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE chapters (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  chapter_title TEXT NOT NULL,
  audio_path TEXT NOT NULL,
  textplot_path TEXT NOT NULL,
  text TEXT NOT NULL
);