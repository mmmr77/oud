from telegram.constants import ParseMode

from config import settings
from inline_search import InlineSearch
from util import Util


def test_build_result_sends_full_poem_as_message_content_with_view_button():
    result = {
        "id": 42,
        "title": "غزل شماره ۱",
        "name": "حافظ",
        "text": "الا یا ایها <b>الساقی</b> ادر کاسا",
        "score": 12.5,
    }
    poem_text = [
        {"text": "الا یا ایها الساقی ادر کاسا"},
        {"text": "که عشق آسان نمود اول ولی افتاد مشکل‌ها"},
    ]
    poem_info = {"title": "غزل شماره ۱", "url": "https://ganjoor.net/hafez/ghazal/sh1", "name": "حافظ"}
    bot_username = "oud_bot"

    article = InlineSearch.build_result(result, position=3, poem_text=poem_text, poem_info=poem_info,
                                        bot_username=bot_username)

    expected_messages = Util.break_long_poems(Util.break_long_verses(poem_text), poem_info, bot_username)
    assert len(expected_messages) == 1  # sanity: this poem fits in a single message

    assert article.id == "42:3"
    assert article.title == "غزل شماره ۱ - حافظ"
    assert article.description == "الا یا ایها الساقی ادر کاسا"
    assert article.input_message_content.message_text == expected_messages[0]
    assert article.input_message_content.parse_mode == ParseMode.HTML
    assert article.reply_markup.inline_keyboard[0][0].text == "مشاهده اثر کامل"
    assert article.reply_markup.inline_keyboard[0][0].url == "https://t.me/oud_bot?start=42"


def test_build_result_truncates_a_poem_too_long_for_one_message():
    result = {"id": 7, "title": "قصیده", "name": "سعدی", "text": "بیت جستجو شده"}
    long_verse = "الف" * 500
    poem_text = [{"text": long_verse} for _ in range(20)]
    poem_info = {"title": "قصیده", "url": "https://ganjoor.net/saadi/ghazal/sh7", "name": "سعدی"}
    bot_username = "oud_bot"

    article = InlineSearch.build_result(result, position=0, poem_text=poem_text, poem_info=poem_info,
                                        bot_username=bot_username)

    expected_messages = Util.break_long_poems(Util.break_long_verses(poem_text), poem_info, bot_username)
    assert len(expected_messages) > 1  # sanity: this poem needs more than one message

    assert article.input_message_content.message_text == expected_messages[0]
    assert len(article.input_message_content.message_text) <= 4096
    assert article.reply_markup.inline_keyboard[0][0].url == "https://t.me/oud_bot?start=7"


def test_next_offset_advances_when_more_results_exist_under_the_depth_cap():
    next_offset = InlineSearch.compute_next_offset(offset=0, results_in_page=8, total_search_count=100)
    assert next_offset == "8"


def test_next_offset_advances_on_the_last_page_under_the_cap():
    next_offset = InlineSearch.compute_next_offset(offset=8, results_in_page=8, total_search_count=100)
    assert next_offset == "16"


def test_next_offset_empty_when_no_more_results_exist():
    next_offset = InlineSearch.compute_next_offset(offset=8, results_in_page=4, total_search_count=12)
    assert next_offset == ""


def test_next_offset_empty_once_depth_cap_reached_even_with_more_results():
    depth_cap = settings.SEARCH_RESULT_PER_PAGE * 2  # 16: matches search.py's chat-search cap
    next_offset = InlineSearch.compute_next_offset(offset=depth_cap, results_in_page=8, total_search_count=1000)
    assert next_offset == ""
