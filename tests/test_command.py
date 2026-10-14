import asyncio
from unittest.mock import AsyncMock, MagicMock

from telegram.constants import ChatType

import const
from command import Command


def test_parse_command_name_works_without_a_mention():
    assert Command.parse_command_name("/about", "oud_bot") == "about"


def test_parse_command_name_strips_the_bot_mention():
    # Group clients append "@bot_username" to commands; private chats don't.
    assert Command.parse_command_name("/about@oud_bot", "oud_bot") == "about"


def test_parse_command_name_is_case_insensitive_about_the_mention():
    assert Command.parse_command_name("/about@Oud_Bot", "oud_bot") == "about"


def test_parse_command_name_ignores_trailing_arguments():
    assert Command.parse_command_name("/about extra text", "oud_bot") == "about"


def test_parse_command_name_returns_none_for_a_different_bots_command():
    assert Command.parse_command_name("/roll@dice_bot", "oud_bot") is None



def run_search_command(chat_type: str) -> dict:
    """Runs the search command in a chat of the given type and returns the arguments of the sent message."""
    update = MagicMock()
    update.effective_chat.type = chat_type
    context = MagicMock()
    context.bot.username = "oud_bot"
    context.bot.send_message = AsyncMock()
    asyncio.run(Command.search(update, context))
    return context.bot.send_message.call_args.kwargs


def test_search_in_private_chat_asks_for_the_search_phrase():
    sent = run_search_command(ChatType.PRIVATE)
    assert sent["text"] == const.SEARCH
    assert "reply_markup" not in sent


def test_search_in_group_points_to_inline_search():
    sent = run_search_command(ChatType.SUPERGROUP)
    assert "@oud_bot" in sent["text"]
    button = sent["reply_markup"].inline_keyboard[0][0]
    assert button.switch_inline_query_current_chat == ""
