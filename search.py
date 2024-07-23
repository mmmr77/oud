from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import const
from db import DataBase


class Search:
    @staticmethod
    async def search_poems(update: Update, context: ContextTypes.DEFAULT_TYPE):
        search_text = update.message.text
        search_results = DataBase().search_poem(search_text)
        if not search_results:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=const.NO_RESULT)
        else:
            text_response = list()
            for i, result in enumerate(search_results):
                text_response.append(str(i+1) + '. ' + result[1] + ' - ' + result[3] + '\n' + result[2])
            text_response = '\n\n'.join(text_response)

            buttons = list()
            for i in range(0, len(search_results), 4):
                row = list()
                for j, result in enumerate(search_results[i:i+4]):
                    button = InlineKeyboardButton(str(i+j+1), callback_data=f'poem:{result[0]}')
                    row.append(button)
                buttons.append(row)
            menu = InlineKeyboardMarkup(buttons)

            await context.bot.send_message(chat_id=update.effective_chat.id, text=text_response, reply_markup=menu)
