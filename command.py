from datetime import datetime, UTC

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

import const
from admin import admin
from db import DataBase
from poem import Poem


class Command:
    @staticmethod
    async def general_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        response = Command.get_general_commands_response(update.message.text[1:])
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode=ParseMode.HTML)

    @staticmethod
    def get_general_commands_response(command: str):
        command_upper = command.upper()
        if command_upper in const.__all__:
            return eval(f'const.{command_upper}')
        else:
            return const.INVALID_COMMAND

    @staticmethod
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.message.from_user.id
        user = DataBase().find_user_by_id(user_id)
        if not user:
            first_name = update.message.from_user.first_name
            last_name = update.message.from_user.last_name
            username = update.message.from_user.username
            creation_datetime = datetime.now(UTC)
            DataBase().insert_user(user_id, first_name, last_name, username, creation_datetime)

        await context.bot.send_message(chat_id=update.effective_chat.id, text=const.START)

        if context.args and len(context.args) == 1 and context.args[0].isnumeric():
            poem_id = int(context.args[0])
            await Poem.get_poem_by_id(poem_id, user_id, context, update.effective_message.id)

    @staticmethod
    @admin
    async def sendtoall(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(update.effective_chat.id, text=const.SEND_YOUR_MESSAGE)
        return 0
