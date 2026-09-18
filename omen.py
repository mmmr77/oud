from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ChatType, ParseMode
from telegram.ext import ContextTypes

import const
from db import DataBase
from poem import Poem


class Omen:
    @staticmethod
    async def show_hafez_omen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Displays a random poem from Qazaliat-e-Hafez along with its interpretation to the user."""
        assert update.callback_query is not None
        assert update.effective_user is not None and update.effective_message is not None
        assert update.effective_chat is not None
        await update.callback_query.answer()
        poet_name = 'حافظ'
        category_name = 'غزلیات'
        poem_id = DataBase().get_random_poem(poet_name, category_name)
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        is_private_chat = update.effective_chat.type == ChatType.PRIVATE
        origin_message_id = update.effective_message.id

        await Poem.get_poem_by_id(poem_id, user_id, chat_id, is_private_chat, context, origin_message_id)
        interpretation = DataBase().get_omen(poem_id)
        await context.bot.send_message(chat_id, const.OMEN_RESULT.format(interpretation=interpretation,
                                                                         username=context.bot.username))

    @staticmethod
    async def show_omen_introduction(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Displays the omen introduction message to the user."""
        assert update.effective_chat is not None
        if update.effective_chat.type != ChatType.PRIVATE:
            await context.bot.send_message(update.effective_chat.id, const.PRIVATE_CHAT_ONLY)
            return
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('نمایش فال', callback_data='omen')]])
        await context.bot.send_message(update.effective_chat.id, const.OMEN_INTRO, reply_markup=keyboard,
                                       parse_mode=ParseMode.HTML)
