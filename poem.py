from persian_tools.digits import convert_to_fa
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

import const
from config import settings
from db import DataBase
from favorite import Favorite
from recitation import Recitation
from util import Util


class Poem:
    @staticmethod
    async def get_poem_by_id(poem_id: int, user_id: int, context: ContextTypes.DEFAULT_TYPE):
        poem_text = DataBase().get_poem_text(poem_id)
        new_poem_text = Util.break_long_verses(poem_text)
        poem_info = DataBase().get_poem_info(poem_id)
        messages = Util.break_long_poems(new_poem_text, poem_info)

        is_favorite = DataBase().check_is_favorite(poem_id, user_id)
        if is_favorite:
            keyboard = Favorite.get_remove_favorites_keyboard(poem_id)
        else:
            keyboard = Favorite.get_add_to_favorites_keyboard(poem_id)

        for message in messages[:-1]:
            await context.bot.send_message(user_id, message, parse_mode=ParseMode.HTML)
        await context.bot.send_message(user_id, messages[-1], parse_mode=ParseMode.HTML, reply_markup=keyboard)

        recitation_count, keyboard = Recitation.get_recitations(poem_id)
        if recitation_count > 0:
            await context.bot.send_message(user_id,
                                           convert_to_fa(const.RECITATION_COUNT.format(count=recitation_count)),
                                           reply_markup=keyboard)

    @staticmethod
    async def show_poem_by_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        poem_id = int(query.data.split(':')[1])
        user_id = query.from_user.id

        await Poem.get_poem_by_id(poem_id, user_id, context)

    @staticmethod
    async def category_poems(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        category_id = int(query.data.split(':')[1])
        offset = int(query.data.split(':')[2])

        poems: list = DataBase().get_category_poems(category_id, offset)
        buttons = list()
        for i in range(0, len(poems), 2):
            row = list()
            for poem in poems[i: i + 2]:
                button = InlineKeyboardButton(Util.trim_text(poem[2], 80), callback_data=f'poem:{poem[0]}')
                row.append(button)
            buttons.append(row)

        last_row = []
        if offset != 0:
            last_row.append(
                InlineKeyboardButton("قبلی", callback_data=f'category:{category_id}:{offset - settings.POEM_PER_PAGE}'))
        if len(poems) == settings.POEM_PER_PAGE:
            last_row.append(
                InlineKeyboardButton("بعدی", callback_data=f'category:{category_id}:{offset + settings.POEM_PER_PAGE}'))
        if last_row:
            buttons.append(last_row)
        menu = InlineKeyboardMarkup(buttons)
        if update.effective_message.text == const.POEMS.strip():
            await update.effective_message.edit_reply_markup(menu)
        else:
            await context.bot.send_message(query.from_user.id, const.POEMS, reply_markup=menu)
