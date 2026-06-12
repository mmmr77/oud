import asyncio
import functools
import logging

from telegram import Update
from telegram.error import Forbidden, RetryAfter, TelegramError
from telegram.ext import ContextTypes, ConversationHandler

import const
from config import settings
from db import DataBase


def admin(func):
    @functools.wraps(func)
    async def wrapper_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message.from_user.id == settings.ADMIN_CHAT_ID:
            result = await func(update, context)
            return result
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=const.INVALID_COMMAND)
            return ConversationHandler.END
    return wrapper_admin


class Admin:
    @staticmethod
    async def _deliver(context: ContextTypes.DEFAULT_TYPE, target_id: int, from_chat_id: int, message_id: int) -> str:
        """Copies the broadcast message to a single user.

        Returns 'sent', 'blocked' (the user blocked the bot), or 'failed' (any other Telegram error).
        """
        for attempt in range(2):
            try:
                await context.bot.copy_message(target_id, from_chat_id, message_id)
                return 'sent'
            except Forbidden:
                return 'blocked'
            except RetryAfter as e:
                if attempt == 0:
                    await asyncio.sleep(e.retry_after)
                    continue
                logging.warning(f"Broadcast to {target_id} still rate-limited after retry.")
                return 'failed'
            except TelegramError as e:
                logging.warning(f"Broadcast to {target_id} failed: {e}")
                return 'failed'
        return 'failed'

    @staticmethod
    @admin
    async def send_to_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Copies the admin's message to every user.

        Per-user failures are counted and skipped. A delivery summary is sent to the admin at the end.
        """
        counts = {'sent': 0, 'blocked': 0, 'failed': 0}
        offset = 0
        while True:
            users = DataBase().get_all_users(offset=offset)
            if not users:
                break
            for user in users:
                status = await Admin._deliver(context, user['id'], update.effective_chat.id, update.message.message_id)
                counts[status] += 1
            offset += len(users)
            await asyncio.sleep(1)

        summary = const.ADMIN_SEND_TO_ALL_SUMMARY.format(sent=counts['sent'], blocked=counts['blocked'],
                                                         failed=counts['failed'])
        await context.bot.send_message(update.effective_chat.id, summary)
        return ConversationHandler.END
