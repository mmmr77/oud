import asyncio
from unittest.mock import AsyncMock, MagicMock

import const
import poem
from config import settings
from poem import Poem


def test_category_buttons_work_while_a_search_is_pending(monkeypatch):
    # A search the user started earlier leaves its query in user_data; it must not be mistaken for category data.
    database = MagicMock()
    database.get_category_poems.return_value = [{"id": 1, "title": "غزل"}]
    monkeypatch.setattr(poem, "DataBase", lambda: database)
    update = MagicMock()
    update.callback_query.data = "category:5:50"
    update.callback_query.answer = AsyncMock()
    update.effective_message.text = const.POEMS.strip()
    update.effective_message.edit_reply_markup = AsyncMock()
    context = MagicMock()
    context.user_data = {"search_query": "عشق"}

    asyncio.run(Poem.category_poems(update, context))

    database.get_category_poems.assert_called_once_with(5, 50, settings.POEM_PER_PAGE + 1)
    update.effective_message.edit_reply_markup.assert_awaited_once()
    assert context.user_data == {"search_query": "عشق"}
