import psycopg2
from psycopg2.extras import RealDictCursor

from config import settings


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DataBase(metaclass=Singleton):
    def __init__(self) -> None:
        self.connection = psycopg2.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            database=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD
        )
        self.connection.autocommit = False
        self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)

    def __del__(self) -> None:
        self.cursor.close()
        self.connection.close()

    def _execute(self, command, fetchone=True, params=None):
        try:
            if params:
                self.cursor.execute(command, params)
            else:
                self.cursor.execute(command)
            return self.cursor.fetchone() if fetchone else self.cursor.fetchall()
        except psycopg2.Error:
            self.connection.rollback()

    def get_poets(self, search_text: str = None) -> list[dict]:
        command = 'SELECT id, name, cat_id FROM poet {search}ORDER BY name'
        if search_text:
            command = command.format(search='WHERE name ILIKE %s ')
            return self._execute(command, False, (f'%{search_text}%',))
        else:
            command = command.format(search='')
            return self._execute(command, False)

    def get_poet(self, poet_id: int) -> dict:
        command = 'SELECT name, cat_id, description FROM poet WHERE id=%s'
        return self._execute(command, True, (poet_id,))

    def get_poem_text(self, poem_id: int) -> list[dict]:
        command = "SELECT text FROM verse WHERE poem_id=%s ORDER BY vorder"
        return self._execute(command, False, (poem_id,))

    def get_poem_info(self, poem_id: int) -> dict:
        command = "SELECT poem.title, poem.url, poet.name FROM poem JOIN cat ON poem.cat_id=cat.id JOIN poet ON " \
                  "cat.poet_id=poet.id WHERE poem.id=%s"
        return self._execute(command, True, (poem_id,))

    def get_poet_categories(self, poet_id: int, category_id: int) -> list[dict]:
        command = 'SELECT id, text FROM cat WHERE poet_id=%s AND parent_id=%s'
        return self._execute(command, False, (poet_id, category_id))

    def get_parent_category_id(self, category_id: int) -> int:
        command = 'SELECT parent_id FROM cat WHERE id=%s'
        return self._execute(command, True, (category_id,))['parent_id']

    def get_category_poems(self, category_id: int, offset: int = 0, limit: int = settings.POEM_PER_PAGE) -> list[dict]:
        command = 'SELECT id, title FROM poem WHERE cat_id=%s ORDER BY id LIMIT %s OFFSET %s'
        return self._execute(command, False, (category_id, limit, offset))

    def get_category_poems_count(self, category_id: int) -> int:
        command = 'SELECT COUNT(*) as count FROM poem WHERE cat_id=%s'
        return self._execute(command, True, (category_id,))['count']

    def search_poem(self, text: str, offset: int, limit: int = settings.SEARCH_RESULT_PER_PAGE) -> list[dict]:
        command = "SELECT poem.id, poem.title, verse.text, poet.name FROM verse JOIN poem ON verse.poem_id=poem.id " \
                  "JOIN cat ON poem.cat_id=cat.id JOIN poet ON cat.poet_id=poet.id WHERE verse.text ILIKE %s" \
                  " LIMIT %s OFFSET %s"
        return self._execute(command, False, (f'%{text}%', limit, offset))

    def search_count(self, text: str) -> int:
        command = "SELECT COUNT(*) as count FROM verse WHERE verse.text ILIKE %s"
        return self._execute(command, True, (f'%{text}%',))['count']

    def search_title(self, text: str, offset: int, limit: int = settings.SEARCH_RESULT_PER_PAGE) -> list[dict]:
        command = "SELECT poem.id, poem.title, poet.name FROM poem JOIN cat ON poem.cat_id=cat.id JOIN poet ON " \
                  "cat.poet_id=poet.id WHERE poem.title ILIKE %s LIMIT %s OFFSET %s"
        return self._execute(command, False, (f'%{text}%', limit, offset))

    def search_title_count(self, text: str):
        command = "SELECT COUNT(*) as count FROM poem WHERE poem.title ILIKE %s"
        return self._execute(command, True, (f'%{text}%',))['count']

    def insert_opinion(self, *args) -> None:
        command = 'INSERT INTO opinion (user_id, message, creation_datatime) VALUES (%s, %s, %s)'
        self.cursor.execute(command, args)
        self.connection.commit()

    def find_user_by_id(self, id_: int) -> dict:
        command = 'SELECT * FROM "user" WHERE id=%s'
        return self._execute(command, True, (id_,))

    def insert_user(self, *args) -> None:
        command = 'INSERT INTO "user" VALUES (%s, %s, %s, %s, %s)'
        self.cursor.execute(command, args)
        self.connection.commit()

    def insert_recitation_data(self, poem_id: int, id_: int, title: str, dnldurl: str, artist: str, audio_order: int,
                               recitation_type: int) -> None:
        command = 'INSERT INTO poemsnd (poem_id, id, title, dnldurl, artist, audio_order, recitation_type) VALUES (%s, %s, %s, %s, %s, %s, %s)'
        self.cursor.execute(command, (poem_id, id_, title, dnldurl, artist, audio_order, recitation_type))
        self.connection.commit()

    def add_recitation_file_id(self, file_id: str, recitation_id: int) -> None:
        command = 'UPDATE poemsnd SET telegram_file_id=%s WHERE id=%s'
        self.cursor.execute(command, (file_id, recitation_id))
        self.connection.commit()

    def get_recitations(self, poem_id: int) -> list[dict]:
        command = 'SELECT DISTINCT id, artist, recitation_type, audio_order FROM poemsnd WHERE poem_id=%s ORDER BY audio_order'
        return self._execute(command, False, (poem_id,))

    def get_recitation(self, recitation_id: int) -> dict:
        command = 'SELECT telegram_file_id, title, artist FROM poemsnd WHERE id=%s'
        return self._execute(command, True, (recitation_id,))

    def get_all_users(self, offset: int = 0, limit: int = settings.USER_FETCH_COUNT) -> list[dict]:
        command = 'SELECT id FROM "user" LIMIT %s OFFSET %s'
        return self._execute(command, False, (limit, offset))

    def check_is_favorite(self, poem_id: int, user_id: int) -> bool:
        command = 'SELECT * FROM fav WHERE poem_id=%s AND user_id=%s'
        favorite = self._execute(command, True, (poem_id, user_id))
        return True if favorite else False

    def remove_from_favorites(self, poem_id: int, user_id: int) -> None:
        command = 'DELETE FROM fav WHERE poem_id=%s AND user_id=%s'
        self.cursor.execute(command, (poem_id, user_id))
        self.connection.commit()

    def add_to_favorites(self, poem_id: int, user_id: int) -> None:
        command = 'INSERT INTO fav VALUES (%s, %s)'
        self.cursor.execute(command, (poem_id, user_id))
        self.connection.commit()

    def get_favorite_count(self, user_id: int) -> int:
        command = 'SELECT COUNT(*) as count FROM fav WHERE user_id=%s'
        return self._execute(command, True, (user_id,))['count']

    def get_favorite_poems(self, user_id: int, offset: int, limit: int = settings.MAX_FAVORITE_PER_PAGE) -> list[dict]:
        command = ('SELECT poem.title, poet.name, verse.text, fav.poem_id FROM fav JOIN poem ON poem.id=fav.poem_id '
                   'JOIN cat ON poem.cat_id=cat.id JOIN poet ON cat.poet_id=poet.id JOIN verse ON verse.poem_id=poem.id'
                   ' WHERE fav.user_id=%s AND verse.vorder=1 LIMIT %s OFFSET %s')
        return self._execute(command, False, (user_id, limit, offset))

    def get_random_poem(self, poem_name: str, category_name: str) -> int:
        command = 'SELECT id FROM cat WHERE text=%s'
        poet_cat_row = self._execute(command, True, (poem_name,))
        poet_cat_id = poet_cat_row['id']
        command = 'SELECT id FROM cat WHERE text=%s AND parent_id=%s'
        cat_row = self._execute(command, True, (category_name, poet_cat_id))
        cat_id = cat_row['id']
        command = 'SELECT id FROM poem WHERE cat_id=%s ORDER BY RANDOM() LIMIT 1'
        poem_row = self._execute(command, True, (cat_id,))
        return poem_row['id']

    def get_omen(self, poem_id: int) -> str:
        command = 'SELECT interpretation FROM omen WHERE poem_id=%s'
        return self._execute(command, True, (poem_id,))['interpretation']
