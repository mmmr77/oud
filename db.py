import sqlite3


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

    def get_poem(self, poem_id):
        command = "SELECT * FROM verse WHERE poem_id=? ORDER BY vorder"
        self.cursor.execute(command, (poem_id,))
        poem = self.cursor.fetchall()
        return poem

    def get_poet_categories(self, poet_id):
        command = 'SELECT * FROM cat WHERE poet_id=?'
        self.cursor.execute(command, (poet_id,))
        categories = self.cursor.fetchall()
        return categories

    def get_category_poems(self, category_id):
        command = 'SELECT * FROM poem WHERE cat_id=?'
        self.cursor.execute(command, (category_id,))
        poems = self.cursor.fetchall()
        return poems

    def insert_opinion(self, *args):
        command = 'INSERT INTO opinion VALUES ...'
        self.cursor.execute(command, args)
        self.connection.commit()
