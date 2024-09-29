import functools
import json
import os

from telegram import Update
from telegram.ext import ContextTypes

from db import DataBase


def oud_files(func):
    @functools.wraps(func)
    async def wrapper_oud_files(update, context):
        if update.effective_chat.id == int(os.environ.get("OUD_FILES_CHANNEL_ID")):
            await func(update, context)

    return wrapper_oud_files


class Recitation:
    @staticmethod
    @oud_files
    async def add_recitation_file_id_to_db(update: Update, context: ContextTypes.DEFAULT_TYPE):
        file_id = update.channel_post.audio.file_id
        recitation_id = update.channel_post.caption
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
        DataBase().insert_recitation_data(poem_id, id_, audio_title, mp3_url, audio_artist, audio_order, recitation_type)

    @staticmethod
    def get_recitation_info(poem_id):
        return DataBase().get_recitation(poem_id)
