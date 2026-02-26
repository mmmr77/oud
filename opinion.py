from datetime import datetime, UTC

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler
from telegram.helpers import mention_html

import const
from admin import admin
from config import settings
from db import DataBase
from util import Util


class Opinion:
    @staticmethod
    async def opinion(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Displays the opinion introduction message to the user."""
        keyboard = ReplyKeyboardMarkup([[const.CANCEL]], one_time_keyboard=True, resize_keyboard=True)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=const.OPINION, reply_markup=keyboard)
        return 0

    @staticmethod
    async def opinion_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Saves the opinion sent by the user and forwards it to the admin."""
        user_first_name = update.message.from_user.first_name
        user_id = update.message.from_user.id
        Util.ensure_user_exists(update.message.from_user)
        message_id = update.message.id
        username = Util.create_username_with_at(update.message.from_user.username)
        message_text = update.message.text
        creation_datetime = datetime.now(UTC)
        DataBase().insert_opinion(user_id, message_text, creation_datetime)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=const.OPINION_SUBMIT,
                                       reply_markup=ReplyKeyboardRemove())

        # Sends the opinion to the admin.
        text = const.OPINION_TO_ADMIN.format(
            user=mention_html(user_id, user_first_name), username=username, user_id=user_id, message_id=message_id)
        await context.bot.send_message(chat_id=settings.ADMIN_CHAT_ID, text=text, parse_mode=ParseMode.HTML)
        await update.message.forward(settings.ADMIN_CHAT_ID)
        return ConversationHandler.END

    @staticmethod
    async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancels the opinion conversation."""
        await context.bot.send_message(chat_id=update.effective_chat.id, text=const.OPINION_CANCEL,
                                       reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    @staticmethod
    @admin
    async def save_user_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Starts the reply-to-opinion conversation by saving the opinion sender info."""
        keyboard = ReplyKeyboardMarkup([[const.CANCEL]], one_time_keyboard=True, resize_keyboard=True)
        _, user_id, message_id = update.message.text.split('_')
        context.user_data["user_id"] = user_id
        context.user_data["message_id"] = message_id
        await context.bot.send_message(update.effective_user.id, const.SEND_YOUR_MESSAGE, reply_markup=keyboard)
        return 0

    @staticmethod
    @admin
    async def reply_to_opinion(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Sends the response to the opinion from the admin to the user who sent the opinion.

        The response can be text, voice, document, or sticker.
        """
        user_id = context.user_data["user_id"]
        message_id = context.user_data["message_id"]
        context.user_data.clear()
        if update.message.text:
            await context.bot.send_message(user_id, update.message.text, reply_to_message_id=message_id)
        if update.message.voice:
            await context.bot.send_voice(user_id, update.message.voice, reply_to_message_id=message_id)
        if update.message.document:
            await context.bot.send_document(user_id, update.message.document, reply_to_message_id=message_id)
        if update.message.sticker:
            await context.bot.send_sticker(user_id, update.message.sticker, reply_to_message_id=message_id)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=const.OPINION_SUBMIT,
                                       reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
