import sqlite3

USER_TABLE = """
CREATE TABLE IF NOT EXISTS user (
    id int NOT NULL UNIQUE PRIMARY KEY,
    first_name varchar(255),
    last_name varchar(255),
    username varchar(255),
    creation_datatime datetime
)
"""

OPINION_TABLE = """
CREATE TABLE IF NOT EXISTS opinion (
    id INTEGER NOT NULL UNIQUE PRIMARY KEY AUTOINCREMENT,
    user_id int,
    message text,
    creation_datatime datetime,
    FOREIGN KEY(user_id) REFERENCES user(id)
)
"""

OMEN_TABLE = """
CREATE TABLE IF NOT EXISTS omen (
    id INTEGER NOT NULL UNIQUE PRIMARY KEY AUTOINCREMENT,
    poem_id int,
    interpretation text,
)
"""

"""
ALTER TABLE poemsnd DROP COLUMN filepath;
ALTER TABLE poemsnd RENAME COLUMN description to title
ALTER TABLE poemsnd RENAME COLUMN isdirect to audio_order
ALTER TABLE poemsnd RENAME COLUMN syncguid to artist
ALTER TABLE poemsnd RENAME COLUMN fchksum to telegram_file_id
ALTER TABLE poemsnd RENAME COLUMN isuploaded to recitation_type
"""

"""
ALTER TABLE fav DROP COLUMN pos;
ALTER TABLE fav RENAME COLUMN verse_id to user_id
"""

def init_database():
    connection = sqlite3.connect('ganjoor.s3db')
    cursor = connection.cursor()
    cursor.execute(USER_TABLE)
    cursor.execute(OPINION_TABLE)
    connection.commit()
    cursor.close()
