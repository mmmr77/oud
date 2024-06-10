from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from command import Command


class Application:
    def __init__(self, token: str):
        self.application = ApplicationBuilder().token(token).build()
        self.add_handlers()

    def start_app(self):
        self.application.run_polling()

    def add_handlers(self):
        commands_handler = MessageHandler(filters.COMMAND, self.command_handler)
        self.application.add_handler(commands_handler)

    async def command_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        response = Command.get_command_response(update.message.text[1:])
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)