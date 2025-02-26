import functools
import time

from telegram import Update
from telegram.error import Forbidden, RetryAfter
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
    @admin
    async def send_to_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
        offset: int = 0
        user_ids = 1
        while user_ids:
            user_ids = DataBase().get_all_users(offset=offset)
            for user_id in user_ids:
                try:
                    await context.bot.send_message(user_id[0], text=update.message.text)
                except Forbidden:
                    print(user_id)
                except RetryAfter as e:
                    time.sleep(e.retry_after)
                    await context.bot.send_message(user_id[0], text=update.message.text)
            offset += settings.USER_FETCH_COUNT
            time.sleep(1)
        await context.bot.send_message(update.effective_chat.id, const.ADMIN_SUCCESSFUL_SEND_TO_ALL)
        return ConversationHandler.END
