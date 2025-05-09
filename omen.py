from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

import const
from db import DataBase
from poem import Poem


class Omen:
    @staticmethod
    async def show_hafez_omen(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.callback_query.answer()
        poet_name = 'حافظ'
        category_name = 'غزلیات'
        poem_id = DataBase().get_random_poem(poet_name, category_name)
        user_id = update.effective_user.id
        origin_message_id = update.effective_message.id

        await Poem.get_poem_by_id(poem_id, user_id, context, origin_message_id)
        interpretation = DataBase().get_omen(poem_id)
        await context.bot.send_message(user_id, const.OMEN_RESULT.format(interpretation=interpretation))

    @staticmethod
    async def show_omen_introduction(update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('نمایش فال', callback_data='omen')]])
        await context.bot.send_message(update.effective_user.id, const.OMEN_INTRO, reply_markup=keyboard,
                                       parse_mode=ParseMode.HTML)
