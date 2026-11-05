from util import Util


def test_couplets_are_separated_by_a_blank_line():
    poem_text = [
        {"text": "الا یا ایها الساقی ادر کاسا و ناولها", "position": 0},
        {"text": "که عشق آسان نمود اول ولی افتاد مشکل‌ها", "position": 1},
        {"text": "به بوی نافه‌ای کاخر صبا زان طره بگشاید", "position": 0},
        {"text": "ز تاب جعد مشکینش چه خون افتاد در دل‌ها", "position": 1},
    ]
    assert "".join(Util.break_long_verses(poem_text)) == (
        "الا یا ایها الساقی ادر کاسا و ناولها\n"
        "که عشق آسان نمود اول ولی افتاد مشکل‌ها\n\n"
        "به بوی نافه‌ای کاخر صبا زان طره بگشاید\n"
        "ز تاب جعد مشکینش چه خون افتاد در دل‌ها\n"
    )


def test_band_couplet_of_a_tarjiband_is_separated_like_a_couplet():
    poem_text = [
        {"text": "a", "position": 0}, {"text": "b", "position": 1},
        {"text": "c", "position": 2}, {"text": "d", "position": 3},
        {"text": "e", "position": 0}, {"text": "f", "position": 1},
    ]
    assert "".join(Util.break_long_verses(poem_text)) == "a\nb\n\nc\nd\n\ne\nf\n"


def test_free_verse_lines_get_no_extra_spacing():
    poem_text = [{"text": "a", "position": 4}, {"text": "b", "position": 4}, {"text": "", "position": 4},
                 {"text": "c", "position": 4}]
    assert "".join(Util.break_long_verses(poem_text)) == "a\nb\n\nc\n"


def test_prose_paragraphs_are_kept_together_but_set_apart_from_verses():
    poem_text = [
        {"text": "p1", "position": -1}, {"text": "p2", "position": -1},
        {"text": "a", "position": 0}, {"text": "b", "position": 1},
        {"text": "p3", "position": -1},
    ]
    assert "".join(Util.break_long_verses(poem_text)) == "p1\np2\n\na\nb\n\np3\n"


def test_heading_stays_attached_to_the_following_couplet():
    poem_text = [{"text": "h", "position": 2}, {"text": "a", "position": 0}, {"text": "b", "position": 1}]
    assert "".join(Util.break_long_verses(poem_text)) == "h\na\nb\n"


def test_verses_without_position_are_joined_by_newlines():
    poem_text = [{"text": "a"}, {"text": "b"}]
    assert Util.break_long_verses(poem_text) == ["a\n", "b\n"]


def test_long_verse_is_split_and_keeps_its_separator():
    long_text = ("الف" * 99 + ".") * 20
    poem_text = [{"text": long_text, "position": 1}, {"text": "x", "position": 0}]
    parts = Util.break_long_verses(poem_text)
    assert len(parts) == 3
    assert parts[0].endswith(".\n") and parts[1].endswith("\n\n")
    assert "".join(parts).replace("\n", "") == long_text + "x"


def test_format_poem_escapes_html_in_poem_data():
    message = Util.format_poem("a < b & c", "https://ganjoor.net/x?a=1&b=2", "<title>", "poet & co", "oud_bot")
    assert "a &lt; b &amp; c" in message
    assert '<a href="https://ganjoor.net/x?a=1&amp;b=2">&lt;title&gt;</a>' in message
    assert "poet &amp; co" in message


def test_search_results_are_escaped_but_keep_the_highlight_tags():
    results = [{"id": 1, "title": "A & B", "name": "<poet>", "text": "x < y <b>عشق</b> &"}]
    message = Util.trim_search_results(results, 0)
    assert message[0][2].endswith("A &amp; B - &lt;poet&gt;\nx &lt; y <b>عشق</b> &amp;")
