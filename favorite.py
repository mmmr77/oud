from typing import Optional

from persian_tools.digits import convert_to_fa
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, CopyTextButton
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
    def create_favorites_messages(favorites: list[dict], offset: int) -> list[str]:
        """Creates formatted message strings for a list of favorite poems."""
        messages = list()
        for ind, favorite in enumerate(favorites):
            number = convert_to_fa(ind + offset + 1)
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
        """Adds the poem to the user's favorite poems."""
        query = update.callback_query
        poem_id = int(query.data.split(':')[1])
        user = update.callback_query.from_user
        Util.ensure_user_exists(user)
        user_id = user.id

        if DataBase().check_is_favorite(poem_id, user_id):
            await query.answer(const.FAVORITE_ALREADY_IN_FAVORITES)
        elif DataBase().get_favorite_count(user_id) >= settings.MAX_FAVORITE:
            await query.answer(const.FAVORITE_NO_MORE_ADD_ALLOWED.format(count=settings.MAX_FAVORITE))
            return
        else:
            DataBase().add_to_favorites(poem_id, user_id)
            await query.answer(const.FAVORITE_ADDED)

        keyboard = InlineKeyboardMarkup(
            [[Favorite.get_remove_favorites_button(poem_id)],
             [InlineKeyboardButton('پیوند اشتراک اثر',
                                   copy_text=CopyTextButton(f"https://t.me/{context.bot.username}?start={poem_id}"))]])
        await update.effective_message.edit_reply_markup(keyboard)

    @staticmethod
    async def remove_from_favorites(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Removes the poem from the user's favorite poems."""
        query = update.callback_query
        poem_id = int(query.data.split(':')[1])
        user = update.callback_query.from_user
        Util.ensure_user_exists(user)
        user_id = user.id

        if DataBase().check_is_favorite(poem_id, user_id):
            DataBase().remove_from_favorites(poem_id, user_id)
            await query.answer(const.FAVORITE_REMOVED)
        else:
            await query.answer(const.FAVORITE_NOT_IN_FAVORITES)

        keyboard = InlineKeyboardMarkup(
            [[Favorite.get_add_to_favorites_button(poem_id)],
             [InlineKeyboardButton('پیوند اشتراک اثر',
                                   copy_text=CopyTextButton(f"https://t.me/{context.bot.username}?start={poem_id}"))]])
        await update.effective_message.edit_reply_markup(keyboard)

    @staticmethod
    async def list_of_favorite_poems(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Displays the list of favorite poems of the user.

        This method can be called in two ways:
        1) The user sends the /favorites command.
        2) In the list of favorite poems, the user taps on previous/next buttons.
        """
        offset = await Favorite.get_offset(update.callback_query)
        user = update.effective_user
        Util.ensure_user_exists(user)
        user_id = user.id
        favorites = DataBase().get_favorite_poems(user_id, offset)
        if not favorites:
            await context.bot.send_message(update.effective_chat.id, const.FAVORITE_NO_RESULT)
        else:
            all_favorites_count = DataBase().get_favorite_count(user_id)
            messages = Favorite.create_favorites_messages(favorites, offset)
            message_text = '\n\n'.join(messages)

            # Create numbered buttons for each favorite poem.
            button_texts = [convert_to_fa(i + offset + 1) for i in range(len(favorites))]
            callback_data = [f"poem:{favorite['poem_id']}" for favorite in favorites]
            buttons = Util.create_inline_buttons(4, len(favorites), button_texts, callback_data)

            # Add pagination buttons if needed.
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

            # Send new message if called from command, otherwise edit existing message.
            if update.message:
                await context.bot.send_message(update.effective_chat.id, message_text, reply_markup=keyboard)
            else:
                await update.effective_message.edit_text(message_text)
                await update.effective_message.edit_reply_markup(keyboard)
