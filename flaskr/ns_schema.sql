DROP TABLE IF EXISTS trial_order;
DROP TABLE IF EXISTS ns_data;
DROP TABLE IF EXISTS rater_survey;
DROP TABLE IF EXISTS final_survey_rater;

CREATE TABLE trial_order (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
--    user_id INTEGER NOT NULL,
    username TEXT NOT NULL,
    trial INTEGER NOT NULL,
    learner_id INTEGER NOT NULL,
    sent_typ TEXT NOT NULL,
    sent_group TEXT NOT NULL,

    pre_recording_id TEXT NOT NULL,
    pre_recording_sent TEXT NOT NULL,
    post_recording_id TEXT NOT NULL,
    post_recording_sent TEXT NOT NULL,
    display_order INTEGER NOT NULL

);

CREATE TABLE ns_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trial_id INTEGER NOT NULL,
    rater_id TEXT NOT NULL,
    learner_id INTEGER NOT NULL,
    sent_typ TEXT NOT NULL,
    sent_group TEXT NOT NULL,

    pre_recording_id TEXT NOT NULL,
    pre_recording_sent TEXT NOT NULL,
    post_recording_id TEXT NOT NULL,
    post_recording_sent TEXT NOT NULL,
    display_order TEXT NOT NULL,
    chosen_recording_id TEXT NOT NULL,
    is_improved TEXT NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE rater_survey (

    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rater_id INTEGER,
    age INTEGER,
    gender TEXT,
    grow_up TEXT,
    live_currently TEXT
);

CREATE TABLE final_survey_rater(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rater_id INTEGER,
    comments TEXT
)