from persian_tools import digits
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import const
from db import DataBase
from util import Util


class Search:
    @staticmethod
    async def search_poems(update: Update, context: ContextTypes.DEFAULT_TYPE):
        search_text = update.message.text
        search_results: list = DataBase().search_poem(search_text)
        if not search_results:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=const.NO_RESULT)
        else:
            messages = Util.classify_search_results(search_results)
            for message in messages:
                message_text = '\n\n'.join(map(lambda x: x[2], message))
                buttons = list()
                for i in range(0, len(message), 4):
                    row = list()
                    for j, result in enumerate(message[i:i+4]):
                        button = InlineKeyboardButton(digits.convert_to_fa(result[0]), callback_data=f'poem:{result[1]}')
                        row.append(button)
                    buttons.append(row)
                menu = InlineKeyboardMarkup(buttons)

                await context.bot.send_message(chat_id=update.effective_chat.id, text=message_text, reply_markup=menu)
