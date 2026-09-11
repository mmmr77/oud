from telegram.constants import ParseMode

from inline_search import InlineSearch


def test_build_result_maps_poem_fields_and_strips_highlight_tags_from_description():
    result = {
        "id": 42,
        "title": "غزل شماره ۱",
        "name": "حافظ",
        "text": "الا یا ایها <b>الساقی</b> ادر کاسا",
        "score": 12.5,
    }

    article = InlineSearch.build_result(result)

    assert article.id == "42"
    assert article.title == "غزل شماره ۱ - حافظ"
    assert article.description == "الا یا ایها الساقی ادر کاسا"
    assert article.input_message_content.message_text == "الا یا ایها <b>الساقی</b> ادر کاسا"
    assert article.input_message_content.parse_mode == ParseMode.HTML
