import functools
import json

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import settings
from db import DataBase
from util import Util

RECITATION_TYPE = {0: 'ساده', 1: 'تفسیر'}


def oud_files(func):
    @functools.wraps(func)
    async def wrapper_oud_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_chat.id == settings.OUD_FILES_CHANNEL_ID:
            await func(update, context)

    return wrapper_oud_files


class Recitation:
    @staticmethod
    @oud_files
    async def add_recitation_file_id_to_db(update: Update, context: ContextTypes.DEFAULT_TYPE):
        file_id = update.channel_post.audio.file_id
        recitation_id = int(update.channel_post.caption)
        DataBase().add_recitation_file_id(file_id, recitation_id)

    @staticmethod
    @oud_files
    async def add_recitation_data_to_db(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    def get_recitations(poem_id: int):
        recitations = DataBase().get_recitations(poem_id)
        artists_and_recitation_type = list(map(lambda x: x[1] + f" ({RECITATION_TYPE.get(x[2], RECITATION_TYPE[0])})", recitations))
        ids = list(map(lambda x: f'recitation:{x[0]}', recitations))
        if recitations:
            keyboard = InlineKeyboardMarkup(Util.create_inline_buttons(2, len(recitations), artists_and_recitation_type, ids))
            return len(recitations), keyboard
        else:
            return 0, None

    @staticmethod
    async def get_recitation_by_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        recitation_id = int(query.data.split(':')[1])
        recitation = DataBase().get_recitation(recitation_id)
        await context.bot.send_audio(query.from_user.id, recitation[0], performer=recitation[2], title=recitation[1])
