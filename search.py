from persian_tools import digits
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import const
from db import DataBase
from util import Util


class Search:
    @staticmethod
    async def get_offset_and_search_query(query, message):
        if query:
            await query.answer()
            return int(query.data.split(':')[2]), query.data.split(':')[1]
        return 0, message.text

    @staticmethod
    async def search_poems(update: Update, context: ContextTypes.DEFAULT_TYPE):
        offset, search_text = await Search.get_offset_and_search_query(update.callback_query, update.message)
        search_results: list = DataBase().search_poem(search_text, offset)
        total_search_count = DataBase().search_count(search_text)
        if not search_results:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=const.NO_RESULT)
        else:
            message = Util.trim_search_results(search_results, offset)
            search_results_in_message = len(message)
            message_text = '\n\n'.join(map(lambda x: x[2], message))
            buttons = list()
            for i in range(0, len(message), 4):
                row = list()
                for result in message[i:i+4]:
                    button = InlineKeyboardButton(digits.convert_to_fa(result[0]), callback_data=f'poem:{result[1]}')
                    row.append(button)
                buttons.append(row)

            if search_results_in_message + offset < total_search_count:
                buttons.append([InlineKeyboardButton("بعدی", callback_data=f'search:{search_text}:{offset + search_results_in_message}')])

            menu = InlineKeyboardMarkup(buttons)

            if offset == 0:
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text=const.SEARCH_RESULT_COUNT.format(count=digits.convert_to_fa(total_search_count)))
                await context.bot.send_message(chat_id=update.effective_chat.id, text=message_text, reply_markup=menu)
            else:
                await update.effective_message.edit_text(message_text)
                await update.effective_message.edit_reply_markup(menu)
