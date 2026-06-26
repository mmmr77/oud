import json

from persian_tools.digits import convert_to_fa
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

import const
from db import DataBase
from util import Util

RECITATION_TYPE = {0: 'ساده', 1: 'تفسیر'}


class Recitation:
    @staticmethod
    async def add_recitation_data_to_db(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        """Adds recitation metadata to the database.

        When information about a recitation is uploaded to the files channel, we save that information to the database.
        """
        text = update.channel_post.text
        recitation_info = json.loads(text)
        poem_id = recitation_info["poemId"]
        id_ = recitation_info["id"]
        audio_title = recitation_info["audioTitle"]
        mp3_url = recitation_info["mp3Url"]
        audio_artist = recitation_info["audioArtist"]
        audio_order = recitation_info["audioOrder"]
        recitation_type = recitation_info["recitationType"]
        DataBase().insert_recitation_data(poem_id, id_, audio_title, mp3_url, audio_artist, audio_order,
                                          recitation_type)

    @staticmethod
    async def add_recitation_file_id_to_db(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        """Saves the recitation file ID to the database.

        After recitation metadata is uploaded to the files channel, the recitation file itself is uploaded to the
        channel. We save the file ID of the recitation to the database.
        """
        file_id = update.channel_post.audio.file_id
        recitation_id = int(update.channel_post.caption)
        DataBase().add_recitation_file_id(file_id, recitation_id)

    @staticmethod
    def get_recitations(poem_id: int) -> tuple[int, InlineKeyboardMarkup | None]:
        """Retrieves recitations for a poem.

        After displaying the poem to the user, we display the available recitations for that poem.
        """
        recitations = DataBase().get_recitations(poem_id)
        if recitations:
            artists_and_recitation_type = list(
                map(lambda x: x["artist"] + f' ({RECITATION_TYPE.get(x["recitation_type"], RECITATION_TYPE[0])})',
                    recitations))
            ids = list(map(lambda x: f'recitation:{x["id"]}', recitations))
            keyboard = InlineKeyboardMarkup(
                Util.create_inline_buttons(2, len(recitations), artists_and_recitation_type, ids))
            return len(recitations), keyboard
        else:
            return 0, None

    @staticmethod
    def get_recitations_button(poem_id: int, count: int) -> InlineKeyboardButton:
        """Builds the button that reveals the list of recitations for a poem."""
        return InlineKeyboardButton(convert_to_fa(const.RECITATION_BUTTON.format(count=count)),
                                    callback_data=f'recitations:{poem_id}')

    @staticmethod
    async def show_recitations(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Sends the list of available recitations when the user taps the recitations button.

        The list message replies to the poem message the button belongs to.
        """
        query = update.callback_query
        await query.answer()
        poem_id = int(query.data.split(':')[1])
        count, keyboard = Recitation.get_recitations(poem_id)
        if count > 0:
            await context.bot.send_message(query.from_user.id,
                                           convert_to_fa(const.RECITATION_COUNT.format(count=count)),
                                           reply_markup=keyboard,
                                           reply_to_message_id=update.effective_message.id)

    @staticmethod
    async def get_recitation_by_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Sends the selected recitation to the user."""
        query = update.callback_query
        await query.answer()
        recitation_id = int(query.data.split(':')[1])
        recitation = DataBase().get_recitation(recitation_id)
        await context.bot.send_audio(query.from_user.id, recitation["telegram_file_id"], performer=recitation["artist"],
                                     title=recitation["title"])
