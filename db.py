import sqlite3

from config import settings


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DataBase(metaclass=Singleton):
    def __init__(self) -> None:
        self.connection = sqlite3.connect('ganjoor.s3db')
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()

    def __del__(self) -> None:
        self.cursor.close()

    def get_poets(self, search_text: str = None) -> list[sqlite3.Row]:
        command = 'SELECT id, name, cat_id FROM poet {search}ORDER BY name'
        if search_text:
            command = command.format(search=f'WHERE name LIKE "%{search_text}%" ')
            self.cursor.execute(command)
        else:
            command = command.format(search='')
            self.cursor.execute(command)
        poets = self.cursor.fetchall()
        return poets

    def get_poet(self, poet_id: int) -> sqlite3.Row:
        command = 'SELECT name, cat_id, description FROM poet WHERE id=?'
        self.cursor.execute(command, (poet_id,))
        poet = self.cursor.fetchone()
        return poet

    def get_poem_text(self, poem_id: int) -> list[sqlite3.Row]:
        command = "SELECT text FROM verse WHERE poem_id=? ORDER BY vorder"
        self.cursor.execute(command, (poem_id,))
        poem = self.cursor.fetchall()
        return poem

    def get_poem_info(self, poem_id: int) -> sqlite3.Row:
        command = "SELECT poem.title, poem.url, poet.name FROM poem JOIN cat ON poem.cat_id=cat.id JOIN poet ON " \
                  "cat.poet_id=poet.id WHERE poem.id=?"
        self.cursor.execute(command, (poem_id,))
        poem_info = self.cursor.fetchone()
        return poem_info

    def get_poet_categories(self, poet_id: int, category_id: int) -> list[sqlite3.Row]:
        command = 'SELECT id, text FROM cat WHERE poet_id=? AND parent_id=?'
        self.cursor.execute(command, (poet_id, category_id))
        categories = self.cursor.fetchall()
        return categories

    def get_parent_category_id(self, category_id: int) -> int:
        command = 'SELECT parent_id FROM cat WHERE id=?'
        self.cursor.execute(command, (category_id,))
        row = self.cursor.fetchone()
        return row['parent_id']

    def get_category_poems(self, category_id: int, offset: int = 0, limit: int = settings.POEM_PER_PAGE) -> list[sqlite3.Row]:
        command = 'SELECT id, title FROM poem WHERE cat_id=? ORDER BY id LIMIT ? OFFSET ?'
        self.cursor.execute(command, (category_id, limit, offset))
        poems = self.cursor.fetchall()
        return poems

    def get_category_poems_count(self, category_id: int) -> int:
        command = 'SELECT COUNT(*) FROM poem WHERE cat_id=?'
        self.cursor.execute(command, (category_id,))
        count = self.cursor.fetchone()[0]
        return count

    def search_poem(self, text: str, offset: int, limit: int = settings.SEARCH_RESULT_PER_PAGE) -> list[sqlite3.Row]:
        command = "SELECT poem.id, poem.title, verse.text, poet.name FROM verse JOIN poem ON verse.poem_id=poem.id " \
                  f"JOIN cat ON poem.cat_id=cat.id JOIN poet ON cat.poet_id=poet.id WHERE verse.text LIKE '%{text}%'" \
                  "LIMIT ? OFFSET ?"
        self.cursor.execute(command, (limit, offset))
        poems = self.cursor.fetchall()
        return poems

    def search_count(self, text: str) -> int:
        command = f"SELECT COUNT(*) FROM verse WHERE verse.text LIKE '%{text}%'"
        self.cursor.execute(command)
        count = self.cursor.fetchone()[0]
        return count

    def search_title(self, text: str, offset: int, limit: int = settings.SEARCH_RESULT_PER_PAGE) -> list[sqlite3.Row]:
        command = "SELECT poem.id, poem.title, poet.name FROM poem JOIN cat ON poem.cat_id=cat.id JOIN poet ON " \
                   f"cat.poet_id=poet.id WHERE poem.title LIKE '%{text}%' LIMIT ? OFFSET ?"
        self.cursor.execute(command, (limit, offset))
        titles = self.cursor.fetchall()
        return titles

    def search_title_count(self, text: str):
        command = f"SELECT COUNT(*) FROM poem WHERE poem.title LIKE '%{text}%'"
        self.cursor.execute(command)
        count = self.cursor.fetchone()[0]
        return count

    def insert_opinion(self, *args) -> None:
        command = 'INSERT INTO opinion (user_id, message, creation_datatime) VALUES (?, ?, ?)'
        self.cursor.execute(command, args)
        self.connection.commit()

    def find_user_by_id(self, id_: int) -> sqlite3.Row:
        command = 'SELECT * FROM user WHERE id=?'
        self.cursor.execute(command, (id_,))
        user = self.cursor.fetchone()
        return user

    def insert_user(self, *args) -> None:
        command = 'INSERT INTO user VALUES (?, ?, ?, ?, ?)'
        self.cursor.execute(command, args)
        self.connection.commit()

    def insert_recitation_data(self, poem_id: int, id_: int, title: str, dnldurl: str, artist: str, audio_order: int,
                               recitation_type: int) -> None:
        command = 'INSERT INTO poemsnd (poem_id, id, title, dnldurl, artist, audio_order, recitation_type) VALUES (?, ?, ?, ?, ?, ?, ?)'
        self.cursor.execute(command, (poem_id, id_, title, dnldurl, artist, audio_order, recitation_type))
        self.connection.commit()

    def add_recitation_file_id(self, file_id: str, recitation_id: int) -> None:
        command = 'UPDATE poemsnd SET telegram_file_id=? WHERE id=?'
        self.cursor.execute(command, (file_id, recitation_id))
        self.connection.commit()

    def get_recitations(self, poem_id: int) -> list[sqlite3.Row]:
        command = 'SELECT DISTINCT id, artist, recitation_type FROM poemsnd WHERE poem_id=? ORDER BY audio_order'
        self.cursor.execute(command, (poem_id,))
        recitations = self.cursor.fetchall()
        return recitations

    def get_recitation(self, recitation_id: int) -> sqlite3.Row:
        command = 'SELECT telegram_file_id, title, artist FROM poemsnd WHERE id=?'
        self.cursor.execute(command, (recitation_id,))
        recitation = self.cursor.fetchone()
        return recitation

    def get_all_users(self, offset: int = 0, limit: int = settings.USER_FETCH_COUNT) -> list[sqlite3.Row]:
        command = 'SELECT id FROM user LIMIT ? OFFSET ?'
        self.cursor.execute(command, (limit, offset))
        user_ids = self.cursor.fetchall()
        return user_ids

    def check_is_favorite(self, poem_id: int, user_id: int) -> bool:
        command = 'SELECT * FROM fav WHERE poem_id=? AND user_id=?'
        self.cursor.execute(command, (poem_id, user_id))
        favorite = self.cursor.fetchone()
        return True if favorite else False

    def remove_from_favorites(self, poem_id: int, user_id: int) -> None:
        command = 'DELETE FROM fav WHERE poem_id=? AND user_id=?'
        self.cursor.execute(command, (poem_id, user_id))
        self.connection.commit()

    def add_to_favorites(self, poem_id: int, user_id: int) -> None:
        command = 'INSERT INTO fav VALUES (?, ?)'
        self.cursor.execute(command, (poem_id, user_id))
        self.connection.commit()

    def get_favorite_count(self, user_id: int) -> int:
        command = 'SELECT COUNT(*) FROM fav WHERE user_id=?'
        self.cursor.execute(command, (user_id,))
        count = self.cursor.fetchone()
        return count[0]

    def get_favorite_poems(self, user_id: int, offset: int, limit: int = settings.MAX_FAVORITE_PER_PAGE) -> list[sqlite3.Row]:
        command = ('SELECT poem.title, poet.name, verse.text, fav.poem_id FROM fav JOIN poem ON poem.id=fav.poem_id '
                   'JOIN cat ON poem.cat_id=cat.id JOIN poet ON cat.poet_id=poet.id JOIN verse ON verse.poem_id=poem.id'
                   ' WHERE fav.user_id=? AND verse.vorder=1 LIMIT ? OFFSET ?')
        self.cursor.execute(command, (user_id, limit, offset))
        favorite_poems = self.cursor.fetchall()
        return favorite_poems

    def get_random_poem(self, poem_name: str, category_name: str) -> int:
        command = 'SELECT id FROM cat WHERE text=?'
        self.cursor.execute(command, (poem_name,))
        poet_cat_id = self.cursor.fetchone()[0]
        command = 'SELECT id FROM cat WHERE text=? AND parent_id=?'
        self.cursor.execute(command, (category_name, poet_cat_id))
        cat_id = self.cursor.fetchone()[0]
        command = 'SELECT id FROM poem WHERE cat_id=? ORDER BY RANDOM() LIMIT 1'
        self.cursor.execute(command, (cat_id,))
        poem_id = self.cursor.fetchone()[0]
        return poem_id

    def get_omen(self, poem_id: int) -> str:
        command = 'SELECT interpretation FROM omen WHERE poem_id=?'
        self.cursor.execute(command, (poem_id,))
        interpretation = self.cursor.fetchone()["interpretation"]
        return interpretation
