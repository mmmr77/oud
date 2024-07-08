from telegram import Update
from telegram.ext import ContextTypes

from db import DataBase


class Search:
    @staticmethod
    async def search_poems(update: Update, context: ContextTypes.DEFAULT_TYPE):
        search_text = update.message.text
        search_results = DataBase().search_poem(search_text)
        response = '\n\n'.join(map(lambda x: x[2], search_results))
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
