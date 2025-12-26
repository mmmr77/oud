import json

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes

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
    async def get_recitation_by_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Sends the selected recitation to the user."""
        query = update.callback_query
        await query.answer()
        recitation_id = int(query.data.split(':')[1])
        recitation = DataBase().get_recitation(recitation_id)
        await context.bot.send_audio(query.from_user.id, recitation["telegram_file_id"], performer=recitation["artist"],
                                     title=recitation["title"])
