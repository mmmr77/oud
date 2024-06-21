# TODO primary key, ...
USER_TABLE = """
CREATE TABLE IF NOT EXISTS user (
    id int NOT NULL UNIQUE,
    first_name varchar(255),
    last_name varchar(255),
    username varchar(255),
    creation_datatime datetime,
    last_interaction_datetime datetime
)
"""

# TODO primary key, foregn key, ...
OPINION_TABLE = """
CREATE TABLE IF NOT EXISTS opinion (
    id int,
    user_id int,
    message text,
    creation_datatime datetime
)
"""

POET_NAME_IN_POEM = """
ALTER TABLE POEM ADD poet_name varchar(255)
"""


# TODO
def fill_poet_in_poem_table():
    pass


def init_database():
    pass
