INDEX_DEFINITION = {
    "settings": {
        "index": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "analysis": {
            "char_filter": {
                "persian_char_normalizer": {
                    "type": "mapping",
                    "mappings": [
                        "\\u064A => \\u06CC",
                        "\\u0649 => \\u06CC",
                        "\\u0643 => \\u06A9",
                        "\\u0623 => \\u0627",
                        "\\u0625 => \\u0627",
                        "\\u0622 => \\u0627",
                        "\\u0629 => \\u0647",
                        "\\u200C => \\u0020"
                    ]
                }
            },
            "filter": {
                "persian_stop_words": {
                    "type": "stop",
                    "stopwords": ["و", "در", "به", "از", "که", "این", "آن", "با", "را", "برای", "تا", "هر", "همه",
                                  "هیچ", "چه", "بسیار", "خیلی", "فقط", "چون", "هم", "نیز", "اما", "ولی", "اگر", "یا",
                                  "نه", "پس", "باید", "شاید", "دیگر", "بر", "بی", "جز", "مثل", "مانند", "روی", "زیر",
                                  "بالای", "کنار", "میان", "پیش", "بعد", "قبل", "چنین", "چنان", "همین", "همان", "جایی",
                                  "کسی", "چیزی", "وقتی", "هنوز"]
                },
                "shingle_2_3": {
                    "type": "shingle",
                    "min_shingle_size": 2,
                    "max_shingle_size": 3,
                }
            },
            "analyzer": {
                "persian_no_stop": {
                    "type": "custom",
                    "char_filter": ["html_strip", "persian_char_normalizer"],
                    "tokenizer": "standard",
                    "filter": ["lowercase", "decimal_digit", "arabic_normalization", "persian_normalization"]
                },
                "persian_search": {
                    "type": "custom",
                    "char_filter": ["html_strip", "persian_char_normalizer"],
                    "tokenizer": "standard",
                    "filter": ["lowercase", "decimal_digit", "arabic_normalization", "persian_normalization",
                               "persian_stop_words"]
                },
                "persian_shingle": {
                    "type": "custom",
                    "char_filter": ["html_strip", "persian_char_normalizer"],
                    "tokenizer": "standard",
                    "filter": ["lowercase", "decimal_digit", "arabic_normalization", "persian_normalization",
                               "shingle_2_3"]
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "poem_id": {"type": "unsigned_long"},
            "poet_name": {"type": "keyword"},
            "poem_title": {"type": "keyword"},
            "verse_text": {
                "type": "text",
                "analyzer": "persian_no_stop",
                "search_analyzer": "persian_search",
                "index_phrases": True,
                "fields": {
                    "shingles": {"type": "text", "analyzer": "persian_shingle"}
                }
            }
        }
    }
}


def create_index(client, index_name: str, *, delete_if_exists: bool = False) -> None:
    """Creates an Elasticsearch index with Oud settings and mappings."""
    if client.indices.exists(index=index_name):
        if not delete_if_exists:
            raise ValueError(f"Index '{index_name}' already exists.")
        client.indices.delete(index=index_name)
    client.indices.create(index=index_name, body=INDEX_DEFINITION)


if __name__ == '__main__':
    from config import settings
    from elasticsearch import Elasticsearch

    client = Elasticsearch(settings.ES_HOST, api_key=settings.ES_API_KEY)
    index_name = "oud"
    create_index(client, index_name, delete_if_exists=True)
    client.close()
