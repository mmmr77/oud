from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

import const
from db import DataBase
from setting import POEM_PER_PAGE


class Poem:
    @staticmethod
    def format_poem(poem, url, title, poet):
        return const.POEM.format(poem=poem, url=url, title=title, poet=poet)

    @staticmethod
    async def show_poem_by_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        poem_id = query.data.split(':')[1]

        poem_text = DataBase().get_poem_text(poem_id)
        poem_text = '\n'.join(map(lambda x: x[0], poem_text))
        poem_info = DataBase().get_poem_info(poem_id)

        formatted_poem = Poem.format_poem(poem_text, poem_info[1], poem_info[0], poem_info[2])
        await context.bot.send_message(query.from_user.id, formatted_poem, parse_mode=ParseMode.HTML)

    @staticmethod
    async def category_poems(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        category_id = query.data.split(':')[1]
        offset = int(query.data.split(':')[2])

        poems: list = DataBase().get_category_poems(category_id, offset)
        buttons = list()
        for i in range(0, len(poems), 2):
            row = list()
            for poem in poems[i: i + 2]:
                button = InlineKeyboardButton(poem[2], callback_data=f'poem:{poem[0]}')
                row.append(button)
            buttons.append(row)

        last_row = []
        if offset != 0:
            last_row.append(InlineKeyboardButton("قبلی", callback_data=f'category:{category_id}:{offset - POEM_PER_PAGE}'))
        if len(poems) == POEM_PER_PAGE:
            last_row.append(InlineKeyboardButton("بعدی", callback_data=f'category:{category_id}:{offset + POEM_PER_PAGE}'))
        if last_row:
            buttons.append(last_row)
        menu = InlineKeyboardMarkup(buttons)

        await context.bot.send_message(query.from_user.id, const.POEMS, reply_markup=menu)
