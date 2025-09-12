from typing import Optional

from elasticsearch import Elasticsearch

from config import settings


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
            self.client = Elasticsearch(settings.ES_HOST, api_key=settings.ES_API_KEY)
            if self.client.ping():
                print("Successfully connected to Elasticsearch.")
            else:
                raise "Could not connect to Elasticsearch."
        except Exception as e:
            raise f"An error occurred while connecting to Elasticsearch: {e}"
        self.index_name = "oud"

    def __del__(self) -> None:
        self.client.close()

    def perform_search(self, search_text: str, offset: int, poet_filter: Optional[str] = None,
                       limit: int = settings.SEARCH_RESULT_PER_PAGE) -> list[dict]:
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
        results = []
        try:
            response = self.client.search(index=self.index_name, body=query_body, size=limit, from_=offset, highlight={
                "fields": {"verse_text": {"pre_tags": ["<b>"], "post_tags": ["</b>"]}},
                "require_field_match": False
            })
            hits = response['hits']['hits']
            for hit in hits:
                source = hit.get("_source", {})
                poem_id = source.get("poem_id")
                poet_name = source.get("poet_name")
                poem_title = source.get("poem_title")
                score = hit.get("_score")
                highlight_snippets = hit.get("highlight", {}).get("verse_text", [])
                snippet = highlight_snippets[0] if highlight_snippets else source.get("verse_text", "")

                results.append({
                    "id": poem_id,
                    "name": poet_name,
                    "title": poem_title,
                    "score": score,
                    "text": snippet
                })
            return results
        except Exception as e:
            raise f"An error occurred during search: {e}"

    def search_count(self, search_text: str) -> int:
        query_body = {
            "query": {
                "match": {
                    "verse_text": search_text
                }
            }
        }
        response = self.client.count(index=self.index_name, body=query_body)
        return response['count']
