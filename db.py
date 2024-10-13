import sqlite3

from config import settings


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DataBase(metaclass=Singleton):
    def __init__(self):
        self.connection = sqlite3.connect('ganjoor.s3db')
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.cursor.close()

    def get_poets(self):
        command = 'SELECT id, name, cat_id FROM poet ORDER BY name'
        self.cursor.execute(command)
        poets = self.cursor.fetchall()
        return poets

    def get_poet(self, poet_id):
        command = 'SELECT * FROM poet WHERE id=?'
        self.cursor.execute(command, (poet_id,))
        poet = self.cursor.fetchone()
        return poet

    def get_poem_text(self, poem_id):
        command = "SELECT text FROM verse WHERE poem_id=? ORDER BY vorder, position"
        self.cursor.execute(command, (poem_id,))
        poem = self.cursor.fetchall()
        return poem

    def get_poem_info(self, poem_id):
        command = "SELECT poem.title, poem.url, poet.name FROM poem JOIN cat ON poem.cat_id=cat.id JOIN poet ON " \
                  "cat.poet_id=poet.id WHERE poem.id=?"
        self.cursor.execute(command, (poem_id,))
        poem_info = self.cursor.fetchone()
        return poem_info

    def get_poet_categories(self, poet_id, category_id):
        command = 'SELECT * FROM cat WHERE poet_id=? AND parent_id=?'
        self.cursor.execute(command, (poet_id, category_id))
        categories = self.cursor.fetchall()
        return categories

    def get_parent_category_id(self, category_id):
        command = 'SELECT parent_id FROM cat WHERE id=?'
        self.cursor.execute(command, (category_id,))
        parent_id = self.cursor.fetchone()
        return parent_id[0]

    def get_category_poems(self, category_id, offset: int = 0, limit: int = settings.POEM_PER_PAGE) -> list:
        command = 'SELECT * FROM poem WHERE cat_id=? ORDER BY id LIMIT ? OFFSET ?'
        self.cursor.execute(command, (category_id, limit, offset))
        poems = self.cursor.fetchall()
        return poems

    def get_category_poems_count(self, category_id):
        command = 'SELECT COUNT(*) FROM poem WHERE cat_id=?'
        self.cursor.execute(command, (category_id,))
        count = self.cursor.fetchone()
        return count

    def search_poem(self, text: str, offset: int, limit: int = settings.SEARCH_RESULT_PER_PAGE) -> list:
        command = "SELECT poem.id, poem.title, verse.text, poet.name FROM verse JOIN poem ON verse.poem_id=poem.id " \
                  f"JOIN cat ON poem.cat_id=cat.id JOIN poet ON cat.poet_id=poet.id WHERE verse.text LIKE '%{text}%'" \
                  "LIMIT ? OFFSET ?"
        self.cursor.execute(command, (limit, offset))
        poems = self.cursor.fetchall()
        return poems

    def search_count(self, text):
        command = f"SELECT COUNT(*) FROM verse WHERE verse.text LIKE '%{text}%'"
        self.cursor.execute(command)
        count = self.cursor.fetchone()[0]
        return count

    def insert_opinion(self, *args):
        command = 'INSERT INTO opinion (user_id, message, creation_datatime) VALUES (?, ?, ?)'
        self.cursor.execute(command, args)
        self.connection.commit()

    def find_user_by_id(self, id_):
        command = 'SELECT * FROM user WHERE id=?'
        self.cursor.execute(command, (id_,))
        user = self.cursor.fetchone()
        return user

    def insert_user(self, *args):
        command = 'INSERT INTO user VALUES (?, ?, ?, ?, ?)'
        self.cursor.execute(command, args)
        self.connection.commit()

    def insert_recitation_data(self, poem_id, id_, title, dnldurl, artist, audio_order, recitation_type):
        command = 'INSERT INTO poemsnd (poem_id, id, title, dnldurl, artist, audio_order, recitation_type) VALUES (?, ?, ?, ?, ?, ?, ?)'
        self.cursor.execute(command, (poem_id, id_, title, dnldurl, artist, audio_order, recitation_type))
        self.connection.commit()

    def add_recitation_file_id(self, file_id, recitation_id):
        command = 'UPDATE poemsnd SET telegram_file_id=? WHERE id=?'
        self.cursor.execute(command, (file_id, recitation_id))
        self.connection.commit()

    def get_recitation(self, poem_id):
        command = 'SELECT telegram_file_id, title, artist FROM poemsnd WHERE poem_id=? ORDER BY audio_order'
        self.cursor.execute(command, (poem_id,))
        recitation = self.cursor.fetchone()
        return recitation
