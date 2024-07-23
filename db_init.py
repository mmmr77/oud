import sqlite3

USER_TABLE = """
CREATE TABLE IF NOT EXISTS user (
    id int NOT NULL UNIQUE PRIMARY KEY,
    first_name varchar(255),
    last_name varchar(255),
    username varchar(255),
    creation_datatime datetime,
    last_interaction_datetime datetime
)
"""

OPINION_TABLE = """
CREATE TABLE IF NOT EXISTS opinion (
    id int NOT NULL PRIMARY KEY,
    user_id int REFERENCES user(id),
    message text,
    creation_datatime datetime
)
"""


def init_database():
    connection = sqlite3.connect('ganjoor.s3db')
    cursor = connection.cursor()
    cursor.execute(USER_TABLE)
    cursor.execute(OPINION_TABLE)
    connection.commit()
    cursor.close()
