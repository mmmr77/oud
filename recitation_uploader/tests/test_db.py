from unittest.mock import patch

from db import DataBase


@patch.object(DataBase, "_fetch_all")
def test_get_recitation_status_splits_on_file_id(mock_fetch_all):
    mock_fetch_all.return_value = [
        {"id": 1, "telegram_file_id": "abc"},
        {"id": 2, "telegram_file_id": None},
        {"id": 3, "telegram_file_id": "def"},
    ]

    done, incomplete = DataBase().get_recitation_status()

    assert done == {1, 3}
    assert incomplete == {2}


@patch.object(DataBase, "_fetch_all")
def test_get_existing_poem_ids_returns_set(mock_fetch_all):
    mock_fetch_all.return_value = [{"id": 10}, {"id": 11}]

    assert DataBase().get_existing_poem_ids() == {10, 11}
