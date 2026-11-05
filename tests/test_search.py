import asyncio
from unittest.mock import AsyncMock, MagicMock

from telegram.ext import ConversationHandler

import const
import search
from search import Search


def make_context(user_data: dict) -> MagicMock:
    context = MagicMock()
    context.user_data = user_data
    context.bot.send_message = AsyncMock()
    return context


def test_search_poet_without_a_pending_query_asks_to_retry():
    context = make_context({})
    state = asyncio.run(Search.search_poet(MagicMock(), context))
    assert state == ConversationHandler.END
    assert context.bot.send_message.call_args.kwargs["text"] == const.SEARCH_RETRY


def test_paging_earlier_results_keeps_the_pending_search_query(monkeypatch):
    # Paging old results while choosing a destination for a new search must not wipe the new search's query.
    redis = MagicMock()
    redis.get.return_value = "عشق"
    monkeypatch.setattr(search, "RedisDB", lambda: redis)
    update = MagicMock()
    update.callback_query.data = "st:abc:8"
    update.callback_query.answer = AsyncMock()
    update.effective_message.edit_text = AsyncMock()
    update.effective_message.edit_reply_markup = AsyncMock()
    context = make_context({"search_query": "حافظ"})
    search_func = MagicMock(return_value=[{"id": 1, "title": "غزل", "name": "حافظ"}])

    asyncio.run(Search.search(update, context, search_func, "st", MagicMock(return_value=20)))

    search_func.assert_called_once_with("عشق", 8)
    assert context.user_data == {"search_query": "حافظ"}


def test_search_poet_with_an_invalid_query_length_ends_the_conversation():
    context = make_context({"search_query": "ab"})
    state = asyncio.run(Search.search_poet(MagicMock(), context))
    assert state == ConversationHandler.END
    assert context.bot.send_message.call_args.kwargs["text"] == const.SEARCH_CHARACTERS_NOT_VALID
