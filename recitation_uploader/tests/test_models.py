import pytest

from recitation_uploader.models import Recitation

API_ITEM = {
    "id": 5,
    "poemId": 42,
    "audioTitle": "title",
    "mp3Url": "https://example.com/a.mp3",
    "audioArtist": "artist",
    "audioOrder": 1,
    "recitationType": 0,
    "ignoredExtra": "x",
}


def test_from_api_parses_known_fields():
    rec = Recitation.from_api(API_ITEM)
    assert rec.id == 5
    assert rec.poem_id == 42
    assert rec.audio_title == "title"
    assert rec.mp3_url == "https://example.com/a.mp3"
    assert rec.audio_artist == "artist"
    assert rec.audio_order == 1
    assert rec.recitation_type == 0


def test_from_api_raises_on_missing_field():
    incomplete = {k: v for k, v in API_ITEM.items() if k != "mp3Url"}
    with pytest.raises(KeyError):
        Recitation.from_api(incomplete)
