from datetime import datetime, UTC

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler

import const
from admin import admin
from config import settings
from db import DataBase
from util import Util


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

    @staticmethod
    async def opinion(update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = ReplyKeyboardMarkup([[const.CANCEL]], one_time_keyboard=True, resize_keyboard=True)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=const.OPINION, reply_markup=keyboard)
        return 0

    @staticmethod
    async def opinion_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_first_name = update.message.from_user.first_name
        user_id = update.message.from_user.id
        username = Util.create_username_with_at(update.message.from_user.username)
        message_text = update.message.text
        creation_datetime = datetime.now(UTC)
        DataBase().insert_opinion(user_id, message_text, creation_datetime)

        await context.bot.send_message(chat_id=update.effective_chat.id, text=const.OPINION_SUBMIT,
                                       reply_markup=ReplyKeyboardRemove())
        await context.bot.send_message(chat_id=settings.ADMIN_CHAT_ID, text=const.OPINION_TO_ADMIN.format(
            user=f'[{user_first_name}](tg://user?id={user_id})', username=username), parse_mode=ParseMode.MARKDOWN)
        await update.message.forward(settings.ADMIN_CHAT_ID)
        return ConversationHandler.END

    @staticmethod
    async def opinion_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(chat_id=update.effective_chat.id, text=const.OPINION_CANCEL,
                                       reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    @staticmethod
    @admin
    async def sendtoall(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(update.effective_chat.id, text=const.ADMIN_SEND_TO_ALL)
        return 0
