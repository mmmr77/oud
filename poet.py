from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes

import const
from db import DataBase
from poem import Poem


class Poet:
    @staticmethod
    async def poets_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, search_text: str = None):
        poets = DataBase().get_poets(search_text)
        if not poets:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=const.SEARCH_NO_RESULT,
                                           reply_markup=ReplyKeyboardRemove())
            return
        if len(poets) == 1:
            context.user_data['poet_id'] = poets[0]['id']
            context.user_data['category_id'] = poets[0]['cat_id']
            await Poet.poet_details(update, context)
            return
        buttons = list()
        for i in range(0, len(poets), 3):
            row = list()
            for poet in poets[i:i + 3]:
                poet_id = poet['id']
                poet_name = poet['name']
                poet_category_id = poet['cat_id']
                button = InlineKeyboardButton(poet_name, callback_data=f'poet:{poet_id}:{poet_category_id}')
                row.append(button)
            buttons.append(row)
        menu = InlineKeyboardMarkup(buttons)

        await context.bot.send_message(update.message.from_user.id, const.POETS, reply_markup=menu)

    @staticmethod
    async def poet_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.callback_query:
            query = update.callback_query
            await query.answer()
            poet_id = int(query.data.split(':')[1])
            category_id = int(query.data.split(':')[2])
        else: # Has user data
            poet_id = context.user_data['poet_id']
            category_id = context.user_data['category_id']
            context.user_data.clear()
        parent_category_id = DataBase().get_parent_category_id(category_id)
        poet = DataBase().get_poet(poet_id)

        categories = DataBase().get_poet_categories(poet_id, category_id)
        buttons = list()
        if categories:
            for category in categories:
                button = [InlineKeyboardButton(category['text'], callback_data=f'poet:{poet_id}:{category["id"]}')]
                buttons.append(button)

            poems = DataBase().get_category_poems(category_id)
            for poem in poems:
                button = [InlineKeyboardButton(poem["title"], callback_data=f'poem:{poem["id"]}')]
                buttons.append(button)
        if category_id != poet['cat_id']:
            buttons.append([InlineKeyboardButton("بازگشت", callback_data=f'poet:{poet_id}:{parent_category_id}')])
        menu = InlineKeyboardMarkup(buttons)

        if update.effective_message.text == const.POETS.strip() or update.effective_message.text == const.SEARCH_POET:
            text = const.POET.format(poet=poet['name'], description=poet['description'])
            await context.bot.send_message(update.effective_user.id, text, reply_markup=menu)
        elif update.effective_message.text.startswith(const.POET.strip()[:8]) and categories:
            await update.effective_message.edit_reply_markup(menu)
        if not categories:
            context.user_data['category_id'] = category_id
            context.user_data['offset'] = 0
            await Poem.category_poems(update, context)
