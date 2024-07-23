from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

import const
from db import DataBase


class Command:
    @staticmethod
    def get_general_commands_response(command: str):
        command_upper = command.upper()
        if command_upper in const.__all__:
            return eval(f'const.{command_upper}')
        else:
            return const.COMMAND_NOT_FOUND

    @staticmethod
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.message.from_user.id
        user = DataBase().find_user_by_id(user_id)
        if not user:
            first_name = update.message.from_user.first_name
            last_name = update.message.from_user.last_name
            username = update.message.from_user.username
            creation_datetime = datetime.utcnow()
            DataBase().insert_user(user_id, first_name, last_name, username, creation_datetime)

        await context.bot.send_message(chat_id=update.effective_chat.id, text=const.START)
