from config import settings
import meilisearch


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class MeilisearchDB(metaclass=Singleton):
    def __init__(self) -> None:
        self.client = meilisearch.Client('http://127.0.0.1:7700', 'masterKey')
        self.index = self.client.index('poems')

    def search(self, text,  offset: int, limit: int = settings.SEARCH_RESULT_PER_PAGE) -> dict:
        result = self.index.search(text, {
            'offset': offset, 'limit': limit, 'filter': ['verse_text']
        })
        return result['hits']
