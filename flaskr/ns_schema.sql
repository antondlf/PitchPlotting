DROP TABLE IF EXISTS trial_order;
DROP TABLE IF EXISTS ns_data;

CREATE TABLE trial_order(
    user_id INTEGER NOT NULL,
    username TEXT NOT NULL,
    trial INTEGER NOT NULL,
    learner_id INTEGER NOT NULL,
    sent_typ TEXT NOT NULL,
    sent_group TEXT NOT NULL,

    pre_recording_id TEXT NOT NULL,
    pre_recording_sent TEXT NOT NULL,
    post_recording_id TEXT NOT NULL,
    post_recording_sent TEXT NOT NULL,
    display_order TEXT NOT NULL,

);

CREATE TABLE ns_data(

    rater_id INTEGER NOT NULL,
    learner_id INTEGER NOT NULL,
    sent_typ TEXT NOT NULL,
    sent_group TEXT NOT NULL,

    pre_recording_id TEXT NOT NULL,
    pre_recording_sent TEXT NOT NULL,
    post_recording_id TEXT NOT NULL,
    post_recording_sent TEXT NOT NULL,
    display_order TEXT NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    chosen_recording_id TEXT NOT NULL,
    is_improved TEXT NOT NULL
);