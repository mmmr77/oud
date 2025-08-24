import psycopg2
from psycopg2.extras import RealDictCursor
from config import settings

USER_TABLE = """
CREATE TABLE IF NOT EXISTS "user" (
    id INTEGER NOT NULL UNIQUE PRIMARY KEY,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    username VARCHAR(255),
    creation_datetime TIMESTAMP
)
"""

OPINION_TABLE = """
CREATE TABLE IF NOT EXISTS opinion (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    message TEXT,
    creation_datetime TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES "user"(id)
)
"""

OMEN_TABLE = """
CREATE TABLE IF NOT EXISTS omen (
    id SERIAL PRIMARY KEY,
    poem_id INTEGER,
    interpretation TEXT
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
    connection = psycopg2.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        database=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD
    )
    cursor = connection.cursor(cursor_factory=RealDictCursor)
    cursor.execute(USER_TABLE)
    cursor.execute(OPINION_TABLE)
    connection.commit()
    cursor.close()
    connection.close()
