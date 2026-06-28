from unittest.mock import Mock

from recitation_uploader import ganjoor
from recitation_uploader.models import Recitation


def _raw(id_):
    return {
        "id": id_,
        "poemId": id_ * 10,
        "audioTitle": "t",
        "mp3Url": "u",
        "audioArtist": "a",
        "audioOrder": 1,
        "recitationType": 0,
    }


def _ok(json_data):
    resp = Mock()
    resp.json.return_value = json_data
    resp.raise_for_status.return_value = None
    return resp


def _failing():
    resp = Mock()
    resp.raise_for_status.side_effect = Exception("boom")
    return resp


def test_fetch_stops_on_empty_page():
    session = Mock()
    session.get.side_effect = [_ok([_raw(1), _raw(2)]), _ok([])]
    result = ganjoor.fetch_all_recitation_metadata(session)
    assert [r.id for r in result] == [1, 2]


def test_fetch_skips_failed_page_and_continues():
    session = Mock()
    session.get.side_effect = [_ok([_raw(1)]), _failing(), _ok([_raw(3)]), _ok([])]
    result = ganjoor.fetch_all_recitation_metadata(session)
    assert [r.id for r in result] == [1, 3]


def test_fetch_stops_after_consecutive_failures():
    session = Mock()
    session.get.return_value = _failing()
    result = ganjoor.fetch_all_recitation_metadata(session)
    assert result == []
    assert session.get.call_count == ganjoor.MAX_CONSECUTIVE_PAGE_FAILURES


def test_fetch_skips_malformed_item():
    session = Mock()
    bad = {"id": 9}  # missing required fields
    session.get.side_effect = [_ok([_raw(1), bad]), _ok([])]
    result = ganjoor.fetch_all_recitation_metadata(session)
    assert [r.id for r in result] == [1]


def test_download_audio_returns_none_on_404():
    session = Mock()
    session.get.return_value = Mock(status_code=404)
    rec = Recitation(1, 10, "t", "u", "a", 1, 0)
    assert ganjoor.download_audio(session, rec) is None


def test_download_audio_returns_content_on_success():
    session = Mock()
    resp = Mock(status_code=200, content=b"audio")
    resp.raise_for_status.return_value = None
    session.get.return_value = resp
    rec = Recitation(1, 10, "t", "u", "a", 1, 0)
    assert ganjoor.download_audio(session, rec) == b"audio"
