DROP TABLE IF EXISTS email_data;

CREATE TABLE email_data (
    username TEXT UNIQUE NOT NULL,
    email TEXT NOT NULL
);