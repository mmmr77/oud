from typing import Optional

from elasticsearch import Elasticsearch

from config import settings
from util import Util


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ElasticSearchDB(metaclass=Singleton):
    def __init__(self) -> None:
        """Establishes a connection to the Elasticsearch."""
        try:
            self.client = Elasticsearch(settings.ES_HOSTES_HOST, api_key=settings.ES_API_KEY)
            if self.client.ping():
                print("Successfully connected to Elasticsearch.")
            else:
                raise "Could not connect to Elasticsearch."
        except Exception as e:
            raise f"An error occurred while connecting to Elasticsearch: {e}"
        self.index_name = "poems"

    @Util.send_typing_action
    def perform_search(self, search_text: str, poet_filter: Optional[str], offset: int,
                       limit: int = settings.SEARCH_RESULT_PER_PAGE) -> tuple:
        if poet_filter:
            query_body = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "match": {
                                    "verse_text": search_text
                                }
                            }
                        ],
                        "filter": [
                            {"term": {"poet_name": poet_filter}},
                        ]
                    }
                }
            }
        else:
            query_body = {
                "query": {
                    "match": {
                        "verse_text": search_text
                    }
                }
            }

        try:
            response = self.client.search(index=self.index_name, body=query_body, size=limit, offset=offset)
            hits = response['hits']['hits']
            total_hits = response['hits']['total']['value']
            return total_hits, hits
        except Exception as e:
            raise f"An error occurred during search: {e}"
