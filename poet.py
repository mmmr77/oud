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
            for poet in poets[i:i+3]:
                button = InlineKeyboardButton(poet[1], callback_data=f'poet:{poet[0]}')
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
        poet_id = query.data.split(':')[1]

        poet = DataBase().get_poet(poet_id)
        categories = DataBase().get_poet_categories(poet_id)
        text = const.POET.format(poet=poet[1], description=poet[3])
        buttons = list()
        for category in categories:
            button = [InlineKeyboardButton(category[2], callback_data=f'category:{category[0]}:0')]
            buttons.append(button)
        menu = InlineKeyboardMarkup(buttons)
        await context.bot.send_message(
            query.from_user.id,
            text,
            reply_markup=menu
        )
