from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
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
            parse_mode=ParseMode.HTML,
            reply_markup=menu
        )

    @staticmethod
    async def poet_details(poet_id):
        poet = DataBase().get_poet(poet_id)
        categories = DataBase().get_poet_categories(poet_id)


