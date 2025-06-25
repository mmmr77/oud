import sqlite3
from typing import Optional

from persian_tools.digits import convert_to_fa
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import ContextTypes

import const
from config import settings
from db import DataBase
from util import Util


class Favorite:
    @staticmethod
    def get_add_to_favorites_button(poem_id: int) -> InlineKeyboardButton:
        return InlineKeyboardButton(const.FAVORITE_ADD, callback_data=f'favadd:{poem_id}')

    @staticmethod
    def get_remove_favorites_button(poem_id: int) -> InlineKeyboardButton:
        return InlineKeyboardButton(const.FAVORITE_REMOVE, callback_data=f'favremove:{poem_id}')

    @staticmethod
    def create_favorites_messages(favorites: list[sqlite3.Row]) -> list[str]:
        messages = list()
        for ind, favorite in enumerate(favorites):
            number = convert_to_fa(ind + 1)
            message = f"{number}. {Util.trim_text(favorite['title'])} - {favorite['name']}\n{Util.trim_text(favorite['text'])}"
            messages.append(message)
        return messages

    @staticmethod
    async def get_offset(query: Optional[CallbackQuery]) -> int:
        if query:
            await query.answer()
            return int(query.data.split(':')[1])
        return 0

    @staticmethod
    async def add_to_favorites(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        poem_id = int(query.data.split(':')[1])
        user_id = update.callback_query.from_user.id

        if DataBase().check_is_favorite(poem_id, user_id):
            await query.answer(const.FAVORITE_ALREADY_IN_FAVORITES)
        elif DataBase().get_favorite_count(user_id) >= settings.MAX_FAVORITE:
            await query.answer(const.FAVORITE_NO_MORE_ADD_ALLOWED.format(count=settings.MAX_FAVORITE))
            return
        else:
            DataBase().add_to_favorites(poem_id, user_id)
            await query.answer(const.FAVORITE_ADDED)

        keyboard = InlineKeyboardMarkup([[Favorite.get_remove_favorites_button(poem_id)]])
        await update.effective_message.edit_reply_markup(keyboard)

    @staticmethod
    async def remove_from_favorites(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        poem_id = int(query.data.split(':')[1])
        user_id = update.callback_query.from_user.id

        if DataBase().check_is_favorite(poem_id, user_id):
            DataBase().remove_from_favorites(poem_id, user_id)
            await query.answer(const.FAVORITE_REMOVED)
        else:
            await query.answer(const.FAVORITE_NOT_IN_FAVORITES)

        keyboard = InlineKeyboardMarkup([[Favorite.get_add_to_favorites_button(poem_id)]])
        await update.effective_message.edit_reply_markup(keyboard)

    @staticmethod
    async def list_of_favorite_poems(update: Update, context: ContextTypes.DEFAULT_TYPE):
        offset = await Favorite.get_offset(update.callback_query)
        user_id = update.effective_user.id
        favorites = DataBase().get_favorite_poems(user_id, offset)
        all_favorites_count = DataBase().get_favorite_count(user_id)
        if not favorites:
            await context.bot.send_message(update.effective_chat.id, const.FAVORITE_NO_RESULT)
        else:
            messages = Favorite.create_favorites_messages(favorites)
            message_text = '\n\n'.join(messages)
            button_texts = [convert_to_fa(i + 1) for i in range(len(favorites))]
            callback_data = [f"poem:{favorite['poem_id']}" for favorite in favorites]
            buttons = Util.create_inline_buttons(4, len(favorites), button_texts, callback_data)
            last_row = []
            if offset > 0:
                last_row.append(
                    InlineKeyboardButton("قبلی", callback_data=f'favorites:{offset - settings.MAX_FAVORITE_PER_PAGE}'))
            if len(favorites) + offset < all_favorites_count:
                last_row.append(
                    InlineKeyboardButton("بعدی", callback_data=f'favorites:{offset + settings.MAX_FAVORITE_PER_PAGE}'))
            if last_row:
                buttons.append(last_row)
            keyboard = InlineKeyboardMarkup(buttons)
            if update.message:
                await context.bot.send_message(update.effective_chat.id, message_text, reply_markup=keyboard)
            else:
                await update.effective_message.edit_text(message_text)
                await update.effective_message.edit_reply_markup(keyboard)
