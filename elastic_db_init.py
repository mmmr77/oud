INDEX_DEFINITION = {
    "settings": {
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
                        "\\u200C => \\u0020",
                        "\\u06F0 => 0", "\\u06F1 => 1", "\\u06F2 => 2", "\\u06F3 => 3", "\\u06F4 => 4",
                        "\\u06F5 => 5", "\\u06F6 => 6", "\\u06F7 => 7", "\\u06F8 => 8", "\\u06F9 => 9",
                        "\\u0660 => 0", "\\u0661 => 1", "\\u0662 => 2", "\\u0663 => 3", "\\u0664 => 4",
                        "\\u0665 => 5", "\\u0666 => 6", "\\u0667 => 7", "\\u0668 => 8", "\\u0669 => 9"
                    ]
                }
            },
            "filter": {
                "persian_stop_words": {
                    "type": "stop",
                    "stopwords": [
                        "و", "در", "به", "از", "که", "این", "آن", "با", "است", "را", "برای",
                        "یک", "خود", "تا", "کرد", "کند", "گفت", "شود", "بود", "شد", "ما",
                        "من", "تو", "او", "ما", "شما", "ایشان", "هر", "همه", "هیچ", "چه",
                        "چون", "هم", "نیز", "اما", "ولی", "اگر", "یا", "نه", "پس", "باید",
                        "شاید", "دیگر", "بر", "بی", "جز", "द्वारा", "مثل", "مانند", "روی",
                        "زیر", "بالای", "کنار", "میان", "پیش", "پس", "بعد", "قبل", "چنین",
                        "چنان", "همین", "همان", "جایی", "کسی", "چیزی", "وقتی", "هنوز",
                        "بسیار", "خیلی", "فقط", "الان", "اکنون", "امروز", "دیروز", "فردا",
                        "اول", "دوم", "سوم", "آخر", "یکی", "دو", "سه", "چهار", "پنج", "شش",
                        "هفت", "هشت", "نه", "ده", "صد", "هزار", "میلیون", "میلیارد",
                        "!", "\"", "#", "(", ")", "*", ",", "-", ".", "/", ":", "[", "]",
                        "«", "»", "،", "؛", "؟"
                    ]
                },
                "persian_stemmer": {
                    "type": "stemmer",
                    "language": "persian"
                }
            },
            "analyzer": {
                "persian_custom_analyzer": {
                    "type": "custom",
                    "char_filter": ["html_strip", "persian_char_normalizer"],
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "decimal_digit",
                        "arabic_normalization",
                        "persian_normalization",
                        "persian_stop_words",
                        "persian_stemmer"
                    ]
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
                "analyzer": "persian_custom_analyzer"
            }
        }
    }
}


def create_index(client, index):
    """Creates the Elasticsearch index with the defined settings and mappings."""
    try:
        if client.indices.exists(index=index):
            print(f"Index '{index}' already exists. Deleting it.")
            client.indices.delete(index=index)

        print(f"Creating index '{index}'...")
        client.indices.create(index=index, body=INDEX_DEFINITION)
        print("Index created successfully.")
    except Exception as e:
        print(f"An error occurred during index creation: {e}")


def index_sample_document(client, index):
    """Indexes a sample Persian poem document."""
    doc = {
        "poem_id": 1001,
        "poet_name": "حافظ",
        "poem_title": "غزل شماره ۱",
        "verse_text": "الا یا ایها الساقی ادر کأسا و ناولها که عشق آسان نمود اول ولی افتاد مشکل‌ها"
    }
    try:
        print("\nIndexing a sample document...")
        response = client.index(index=index, id=doc["poem_id"], document=doc)
        if response.get('result') == 'created':
            print("Document indexed successfully.")
            # Refresh the index to make the document searchable
            client.indices.refresh(index=index)
        else:
            print(f"Failed to index document. Response: {response}")
    except Exception as e:
        print(f"An error occurred during indexing: {e}")
