from recitation_uploader.http_client import build_session


def test_build_session_configures_retry():
    session = build_session(total_retries=7, backoff_factor=2.0)
    retry = session.get_adapter("https://example.com").max_retries
    assert retry.total == 7
    assert retry.backoff_factor == 2.0
    assert 503 in retry.status_forcelist
    assert 504 in retry.status_forcelist


def test_build_session_mounts_both_schemes():
    session = build_session()
    assert session.get_adapter("http://example.com").max_retries.total == 5
    assert session.get_adapter("https://example.com").max_retries.total == 5
