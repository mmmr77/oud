import sqlite3

from setting import POEM_PER_PAGE


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
        command = 'SELECT id, name, cat_id FROM poet'
        self.cursor.execute(command)
        poets = self.cursor.fetchall()
        return poets

    def get_poet(self, poet_id):
        command = 'SELECT * FROM poet WHERE id=?'
        self.cursor.execute(command, (poet_id,))
        poet = self.cursor.fetchone()
        return poet

    def get_poem_text(self, poem_id):
        command = "SELECT * FROM verse WHERE poem_id=? ORDER BY vorder, position"
        self.cursor.execute(command, (poem_id,))
        poem = self.cursor.fetchall()
        return poem

    def get_poem_info(self, poem_id):
        command = "SELECT * FROM poem WHERE id=?"
        self.cursor.execute(command, (poem_id,))
        poem_info = self.cursor.fetchone()
        return poem_info

    def get_poet_categories(self, poet_id):
        command = 'SELECT * FROM cat WHERE poet_id=? AND parent_id!=0'
        self.cursor.execute(command, (poet_id,))
        categories = self.cursor.fetchall()
        return categories

    def get_category_poems(self, category_id, offset: int = 0, limit: int = POEM_PER_PAGE):
        command = 'SELECT * FROM poem WHERE cat_id=? ORDER BY id LIMIT ? OFFSET ?'
        self.cursor.execute(command, (category_id, limit, offset))
        poems = self.cursor.fetchall()
        return poems

    def get_category_poems_count(self, category_id):
        command = 'SELECT COUNT(*) FROM poem WHERE cat_id=?'
        self.cursor.execute(command, (category_id,))
        count = self.cursor.fetchone()
        return count

    def search_poem(self, text: str) -> list:
        command = f"SELECT poem.id, poem.title, verse.text, poet.name FROM verse JOIN poem ON verse.poem_id=poem.id " \
                  f"JOIN cat ON poem.cat_id=cat.id JOIN poet ON cat.poet_id=poet.id WHERE verse.text LIKE '%{text}%'"
        self.cursor.execute(command)
        poems = self.cursor.fetchall()
        return poems

    def insert_opinion(self, *args):
        # TODO
        command = 'INSERT INTO opinion VALUES ...'
        self.cursor.execute(command, args)
        self.connection.commit()

    def insert_user(self, *args):
        # TODO
        command = 'INSERT INTO user VALUES ...'
        self.cursor.execute(command, args)
        self.connection.commit()
