from telegram.constants import ParseMode

from config import settings
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


def test_next_offset_advances_when_more_results_exist_under_the_depth_cap():
    next_offset = InlineSearch.compute_next_offset(offset=0, results_in_page=8, total_search_count=100)
    assert next_offset == "8"


def test_next_offset_empty_when_no_more_results_exist():
    next_offset = InlineSearch.compute_next_offset(offset=8, results_in_page=4, total_search_count=12)
    assert next_offset == ""


def test_next_offset_empty_once_depth_cap_reached_even_with_more_results():
    depth_cap = settings.SEARCH_RESULT_PER_PAGE * 2  # 16: matches search.py's chat-search cap
    next_offset = InlineSearch.compute_next_offset(offset=depth_cap, results_in_page=8, total_search_count=1000)
    assert next_offset == ""
