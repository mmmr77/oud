import asyncio
from unittest.mock import AsyncMock, MagicMock

from telegram import Chat, Message, MessageEntity, Update, User
from telegram.ext import ConversationHandler

import const
from admin import Admin
from app import Application


def make_update(text: str) -> Update:
    user = User(1, "admin", False)
    # Telegram marks commands with a bot_command entity, which filters.COMMAND relies on.
    entities = [MessageEntity(MessageEntity.BOT_COMMAND, 0, len(text))] if text.startswith('/') else []
    message = Message(1, None, Chat(1, Chat.PRIVATE), from_user=user, text=text, entities=entities)
    return Update(1, message=message)


def get_send_to_all_handler() -> ConversationHandler:
    application = MagicMock()
    Application.add_handlers(MagicMock(application=application))
    handlers = application.add_handlers.call_args.args[0]
    return next(handler for handler in handlers if isinstance(handler, ConversationHandler)
                and handler.entry_points[0].commands == frozenset({'sendtoall'}))


def test_cancel_and_commands_are_not_broadcast():
    broadcast_handler = get_send_to_all_handler().states[0][0]
    assert not broadcast_handler.check_update(make_update(const.CANCEL))
    assert not broadcast_handler.check_update(make_update("/poets"))
    assert broadcast_handler.check_update(make_update("سلام"))


def test_cancel_is_a_fallback_of_the_broadcast_conversation():
    fallback = get_send_to_all_handler().fallbacks[0]
    assert fallback.check_update(make_update(const.CANCEL))


def test_cancel_ends_the_broadcast_conversation():
    context = MagicMock()
    context.bot.send_message = AsyncMock()
    state = asyncio.run(Admin.cancel(MagicMock(), context))
    assert state == ConversationHandler.END
    assert context.bot.send_message.call_args.args[1] == const.ADMIN_SEND_TO_ALL_CANCEL
