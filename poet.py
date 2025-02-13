from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

import const
from db import DataBase


class Poet:
    @staticmethod
    async def poets_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        poets = DataBase().get_poets()
        buttons = list()
        for i in range(0, len(poets), 3):
            row = list()
            for poet in poets[i:i + 3]:
                poet_id = poet[0]
                poet_name = poet[1]
                poet_category_id = poet[2]
                button = InlineKeyboardButton(poet_name, callback_data=f'poet:{poet_id}:{poet_category_id}')
                row.append(button)
            buttons.append(row)
        menu = InlineKeyboardMarkup(buttons)

        await context.bot.send_message(
            update.message.from_user.id,
            const.POETS,
            reply_markup=menu
        )

    @staticmethod
    async def poet_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        poet_id = int(query.data.split(':')[1])
        category_id = int(query.data.split(':')[2])
        parent_category_id = DataBase().get_parent_category_id(category_id)
        poet = DataBase().get_poet(poet_id)

        categories = DataBase().get_poet_categories(poet_id, category_id)
        if not categories:
            buttons = [[InlineKeyboardButton(f"ورود به شعرهای این دسته", callback_data=f'category:{category_id}:0')]]
        else:
            buttons = list()
            for category in categories:
                button = [InlineKeyboardButton(category[2], callback_data=f'poet:{poet_id}:{category[0]}')]
                buttons.append(button)

            poems = DataBase().get_category_poems(category_id)
            for poem in poems:
                button = [InlineKeyboardButton(poem[2], callback_data=f'poem:{poem[0]}')]
                buttons.append(button)
        if category_id != poet[2]:
            buttons.append([InlineKeyboardButton("بازگشت", callback_data=f'poet:{poet_id}:{parent_category_id}')])
        menu = InlineKeyboardMarkup(buttons)

        if update.effective_message.text == const.POETS.strip():
            text = const.POET.format(poet=poet[1], description=poet[3])
            await context.bot.send_message(query.from_user.id, text, reply_markup=menu)
        else:
            await update.effective_message.edit_reply_markup(menu)
