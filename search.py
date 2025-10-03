import hashlib
from typing import Optional, Callable

from persian_tools import digits
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, ReplyKeyboardMarkup, \
    ReplyKeyboardRemove
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler

import const
from config import settings
from db import DataBase
from elastic_db import ElasticSearchDB
from poet import Poet
from redis_db import RedisDB
from util import Util


class Search:
    @staticmethod
    async def get_offset_and_search_query(query: Optional[CallbackQuery], message):
        if query:
            await query.answer()
            parts = query.data.split(':')
            offset = int(parts[2])
            search_identifier = parts[1]
            search_text = RedisDB().get(search_identifier).decode('utf-8')
            return offset, search_text
        return 0, message["search_query"]

    @staticmethod
    async def search_poems(update: Update, context: ContextTypes.DEFAULT_TYPE):
        return await Search.search(update, context, ElasticSearchDB().perform_search, 'srch')

    @staticmethod
    async def search_poet(update: Update, context: ContextTypes.DEFAULT_TYPE):
        search_text = context.user_data["search_query"]
        context.user_data.clear()
        if len(search_text) < 3 or len(search_text) > 100:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=const.SEARCH_CHARACTERS_NOT_VALID,
                                           reply_markup=ReplyKeyboardRemove())
            return
        await Poet.poets_menu(update, context, search_text)
        return ConversationHandler.END

    @staticmethod
    async def search_destination(update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data["search_query"] = update.message.text
        keyboard = ReplyKeyboardMarkup([[const.SEARCH_VERSE], [const.SEARCH_POET], [const.SEARCH_POEM_TITLE],
                                        [const.CANCEL]], one_time_keyboard=True, resize_keyboard=True)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=const.SEARCH_DESTINATION,
                                       reply_markup=keyboard)
        return 0

    @staticmethod
    async def search_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
        return await Search.search(update, context, DataBase().search_title, 'st',
                                   DataBase().search_title_count)

    @staticmethod
    async def search(update: Update, context: ContextTypes.DEFAULT_TYPE, search_func: Callable, callback_key: str,
                     count_func: Callable = None):
        offset, search_text = await Search.get_offset_and_search_query(update.callback_query, context.user_data)
        context.user_data.clear()
        if len(search_text) < 3 or len(search_text) > 100:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=const.SEARCH_CHARACTERS_NOT_VALID)
            return ConversationHandler.END

        if count_func:
            search_results = search_func(search_text, offset)
            total_search_count = count_func(search_text)
        else:
            search_results, total_search_count = search_func(search_text, offset)
        if not search_results:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=const.SEARCH_NO_RESULT)
            return ConversationHandler.END

        message = Util.trim_search_results(search_results, offset)
        search_results_in_message = len(message)
        message_text = '\n\n'.join([result[2] for result in message])

        buttons = list()
        for i in range(0, len(message), 4):
            row = list()
            for result in message[i:i + 4]:
                button = InlineKeyboardButton(digits.convert_to_fa(result[0]), callback_data=f'poem:{result[1]}')
                row.append(button)
            buttons.append(row)
        if search_results_in_message + offset < total_search_count and offset < settings.SEARCH_RESULT_PER_PAGE * 2:
            digest_hex = hashlib.sha224(search_text.encode("utf-8")).hexdigest()
            RedisDB().store(digest_hex, search_text)
            next_callback_data = f'{callback_key}:{digest_hex}:{offset + search_results_in_message}'
            buttons.append([InlineKeyboardButton("بعدی", callback_data=next_callback_data)])
        menu = InlineKeyboardMarkup(buttons)

        if offset == 0:
            count_text = const.SEARCH_RESULT_COUNT.format(count=digits.convert_to_fa(total_search_count))
            if total_search_count > settings.SEARCH_RESULT_PER_PAGE * 3:
                count_text += const.SEARCH_SHOWING_TOP_RESULTS
            await context.bot.send_message(update.effective_chat.id, reply_markup=ReplyKeyboardRemove(),
                                           text=count_text)
            await context.bot.send_message(update.effective_chat.id, text=message_text, reply_markup=menu,
                                           parse_mode=ParseMode.HTML)
        else:
            await update.effective_message.edit_text(message_text, parse_mode=ParseMode.HTML)
            await update.effective_message.edit_reply_markup(menu)

        return ConversationHandler.END

    @staticmethod
    async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(chat_id=update.effective_chat.id, text=const.SEARCH_CANCEL,
                                       reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
