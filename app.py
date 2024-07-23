from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler, CallbackQueryHandler
from command import Command
from poem import Poem
from poet import Poet
from search import Search


class Application:
    def __init__(self, token: str):
        self.application = ApplicationBuilder().token(token).build()
        self.add_handlers()

    def start_app(self):
        self.application.run_polling()

    def add_handlers(self):
        start_handler = CommandHandler('start', Command.start)
        self.application.add_handler(start_handler)

        poets_handler = CommandHandler('poets', Poet.poets_menu)
        self.application.add_handler(poets_handler)

        poet_details_handler = CallbackQueryHandler(Poet.poet_details, r'^poet:\d+$')
        self.application.add_handler(poet_details_handler)

        category_handler = CallbackQueryHandler(Poem.category_poems, r'^category:\d+:\d+$')
        self.application.add_handler(category_handler)

        poem_handler = CallbackQueryHandler(Poem.show_poem_by_id, r'^poem:\d+$')
        self.application.add_handler(poem_handler)

        commands_handler = MessageHandler(filters.COMMAND, self.command_handler)
        self.application.add_handler(commands_handler)

        search_handler = MessageHandler(filters.TEXT, Search.search_poems)
        self.application.add_handler(search_handler)

    async def command_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        response = Command.get_general_commands_response(update.message.text[1:])
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode=ParseMode.HTML)
