from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

import const
from admin import admin
from poem import Poem
from util import Util


class Command:
    @staticmethod
    async def general_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles simple commands.

        A simple command is a command that requires no processing, and we just send the desired response to the user.
        """
        response = Command.get_general_commands_response(update.message.text[1:])
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode=ParseMode.HTML)

    @staticmethod
    def get_general_commands_response(command: str):
        """Retrieves the desired general command response from the const file."""
        command_upper = command.upper()
        if command_upper in const.__all__:
            return eval(f'const.{command_upper}')
        else:
            return const.INVALID_COMMAND

    @staticmethod
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles the start command.

        Displays the welcome message to the user. If it is the first time the user is using the bot, we save the user
        information. If the command contains a number as its parameter, we also display the poem related to that number.
        """
        user_id = update.message.from_user.id
        Util.ensure_user_exists(update.message.from_user)

        await context.bot.send_message(chat_id=update.effective_chat.id, text=const.START)

        if context.args and len(context.args) == 1 and context.args[0].isnumeric():
            poem_id = int(context.args[0])
            await Poem.get_poem_by_id(poem_id, user_id, context, update.effective_message.id)

    @staticmethod
    @admin
    async def sendtoall(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Sends the broadcast introduction message to the admin user."""
        await context.bot.send_message(update.effective_chat.id, text=const.SEND_YOUR_MESSAGE)
        return 0
