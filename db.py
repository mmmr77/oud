from urllib.parse import quote_plus

from sqlalchemy import create_engine, delete, func, select, update
from sqlalchemy.dialects.postgresql import insert

from config import settings
from db_schema import Cat, Fav, Omen, Opinion, Poem, PoemSnd, Poet, Song, User, Verse


def _build_engine_url() -> str:
    user = quote_plus(str(settings.DB_USER))
    password = quote_plus(str(settings.DB_PASSWORD))
    return f"postgresql+psycopg2://{user}:{password}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class DataBase(metaclass=Singleton):
    def __init__(self) -> None:
        self._engine = create_engine(
            _build_engine_url(),
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_POOL_MAX_OVERFLOW,
            pool_pre_ping=True,
            pool_recycle=1800,
        )

    def close(self) -> None:
        self._engine.dispose()

    def _fetch_all(self, statement) -> list[dict]:
        with self._engine.connect() as connection:
            return [dict(row) for row in connection.execute(statement).mappings()]

    def _fetch_one(self, statement) -> dict | None:
        with self._engine.connect() as connection:
            row = connection.execute(statement).mappings().first()
            return dict(row) if row is not None else None

    def _fetch_scalar(self, statement):
        with self._engine.connect() as connection:
            return connection.execute(statement).scalar_one()

    def _execute_write(self, statement) -> None:
        with self._engine.begin() as connection:
            connection.execute(statement)

    def get_poets(self, search_text: str = None) -> list[dict]:
        statement = select(Poet.id, Poet.name, Poet.cat_id).order_by(Poet.name)
        if search_text:
            statement = statement.where(Poet.name.ilike(f'%{search_text}%'))
        return self._fetch_all(statement)

    def get_poet(self, poet_id: int) -> dict:
        return self._fetch_one(select(Poet.name, Poet.cat_id, Poet.description).where(Poet.id == poet_id))

    def get_poem_text(self, poem_id: int) -> list[dict]:
        return self._fetch_all(select(Verse.text).where(Verse.poem_id == poem_id).order_by(Verse.vorder))

    def get_poem_info(self, poem_id: int) -> dict:
        return self._fetch_one(select(Poem.title, Poem.url, Poet.name)
                               .join(Cat, Poem.cat_id == Cat.id)
                               .join(Poet, Cat.poet_id == Poet.id)
                               .where(Poem.id == poem_id))

    def get_poet_categories(self, poet_id: int, category_id: int) -> list[dict]:
        return self._fetch_all(select(Cat.id, Cat.text).where(Cat.poet_id == poet_id, Cat.parent_id == category_id))

    def get_parent_category_id(self, category_id: int) -> int:
        return self._fetch_scalar(select(Cat.parent_id).where(Cat.id == category_id))

    def get_category_poems(self, category_id: int, offset: int = 0, limit: int = settings.POEM_PER_PAGE) -> list[dict]:
        return self._fetch_all(select(Poem.id, Poem.title).where(Poem.cat_id == category_id)
                               .order_by(Poem.id).limit(limit).offset(offset))

    def search_title(self, text: str, offset: int, limit: int = settings.SEARCH_RESULT_PER_PAGE) -> list[dict]:
        return self._fetch_all(select(Poem.id, Poem.title, Poet.name)
                               .join(Cat, Poem.cat_id == Cat.id)
                               .join(Poet, Cat.poet_id == Poet.id)
                               .where(Poem.title.ilike(f'%{text}%'))
                               .limit(limit).offset(offset))

    def search_title_count(self, text: str):
        return self._fetch_scalar(select(func.count()).select_from(Poem).where(Poem.title.ilike(f'%{text}%')))

    def insert_opinion(self, *args) -> None:
        user_id, message, creation_datetime = args
        self._execute_write(insert(Opinion).values(user_id=user_id, message=message,
                                                   creation_datetime=creation_datetime))

    def upsert_user_activity(self, user_id: int, first_name: str | None, last_name: str | None, username: str | None,
                             seen_at) -> None:
        statement = insert(User).values(id=user_id, first_name=first_name, last_name=last_name, username=username,
                                        creation_datetime=seen_at, last_seen_at=seen_at)
        statement = statement.on_conflict_do_update(
            index_elements=['id'],
            set_={
                'first_name': statement.excluded.first_name,
                'last_name': statement.excluded.last_name,
                'username': statement.excluded.username,
                'last_seen_at': func.greatest(func.coalesce(User.last_seen_at, statement.excluded.last_seen_at),
                                              statement.excluded.last_seen_at),
            })
        self._execute_write(statement)

    def count_active_users_since(self, since_dt) -> int:
        return self._fetch_scalar(select(func.count()).select_from(User).where(User.last_seen_at >= since_dt))

    def count_users(self) -> int:
        return self._fetch_scalar(select(func.count()).select_from(User))

    def insert_recitation_data(self, poem_id: int, id_: int, title: str, dnldurl: str, artist: str, audio_order: int,
                               recitation_type: int) -> None:
        self._execute_write(insert(PoemSnd).values(poem_id=poem_id, id=id_, title=title, dnldurl=dnldurl, artist=artist,
                                                   audio_order=audio_order, recitation_type=recitation_type))

    def add_recitation_file_id(self, file_id: str, recitation_id: int) -> None:
        self._execute_write(update(PoemSnd).where(PoemSnd.id == recitation_id).values(telegram_file_id=file_id))

    def get_recitations(self, poem_id: int) -> list[dict]:
        statement = (select(PoemSnd.id, PoemSnd.artist, PoemSnd.recitation_type, PoemSnd.audio_order)
                     .where(PoemSnd.poem_id == poem_id, PoemSnd.telegram_file_id.is_not(None))
                     .order_by(PoemSnd.audio_order))
        return self._fetch_all(statement)

    def get_recitation(self, recitation_id: int) -> dict:
        return self._fetch_one(select(PoemSnd.telegram_file_id, PoemSnd.title, PoemSnd.artist)
                               .where(PoemSnd.id == recitation_id))

    def get_all_users(self, offset: int = 0, limit: int = settings.USER_FETCH_COUNT) -> list[dict]:
        return self._fetch_all(select(User.id).order_by(User.id).limit(limit).offset(offset))

    def check_is_favorite(self, poem_id: int, user_id: int) -> bool:
        favorite = self._fetch_one(select(Fav.__table__).where(Fav.poem_id == poem_id, Fav.user_id == user_id))
        return favorite is not None

    def remove_from_favorites(self, poem_id: int, user_id: int) -> None:
        self._execute_write(delete(Fav).where(Fav.poem_id == poem_id, Fav.user_id == user_id))

    def add_to_favorites(self, poem_id: int, user_id: int) -> None:
        self._execute_write(insert(Fav).values(poem_id=poem_id, user_id=user_id).on_conflict_do_nothing())

    def get_favorite_count(self, user_id: int) -> int:
        return self._fetch_scalar(select(func.count()).select_from(Fav).where(Fav.user_id == user_id))

    def get_favorite_poems(self, user_id: int, offset: int, limit: int = settings.MAX_FAVORITE_PER_PAGE) -> list[dict]:
        return self._fetch_all(select(Poem.title, Poet.name, Verse.text, Fav.poem_id)
                               .select_from(Fav)
                               .join(Poem, Poem.id == Fav.poem_id)
                               .join(Cat, Poem.cat_id == Cat.id)
                               .join(Poet, Cat.poet_id == Poet.id)
                               .join(Verse, (Verse.poem_id == Poem.id) & (Verse.vorder == 1))
                               .where(Fav.user_id == user_id)
                               .order_by(Fav.poem_id)
                               .limit(limit).offset(offset))

    def get_random_poem(self, poem_name: str, category_name: str) -> int:
        poet_cat_id = self._fetch_scalar(select(Cat.id).where(Cat.text == poem_name).limit(1))
        cat_id = self._fetch_scalar(select(Cat.id).where(Cat.text == category_name,
                                                         Cat.parent_id == poet_cat_id).limit(1))
        return self._fetch_scalar(select(Poem.id).where(Poem.cat_id == cat_id).order_by(func.random()).limit(1))

    def get_omen(self, poem_id: int) -> str:
        return self._fetch_scalar(select(Omen.interpretation).where(Omen.poem_id == poem_id).limit(1))

    def insert_song_data(self, poem_id: int, id_: int, title: str, artist: str, download_url: str, duration: int,
                         source_page: str) -> None:
        self._execute_write(insert(Song).values(poem_id=poem_id, id=id_, title=title, artist=artist, duration=duration,
                                                download_url=download_url, source_page=source_page))

    def add_song_file_id(self, file_id: str, song_id: int) -> None:
        self._execute_write(update(Song).where(Song.id == song_id).values(telegram_file_id=file_id))

    def get_songs(self, poem_id: int) -> list[dict]:
        return self._fetch_all(select(Song.id, Song.artist)
                               .where(Song.poem_id == poem_id, Song.telegram_file_id.is_not(None))
                               .distinct(Song.source_page))

    def get_song(self, song_id: int) -> dict:
        return self._fetch_one(select(Song.telegram_file_id, Song.title, Song.artist, Song.duration)
                               .where(Song.id == song_id))
