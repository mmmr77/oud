import json

from telegram import Update
from telegram.ext import ContextTypes

from db import DataBase


class Song:
    @staticmethod
    async def add_song_data_to_db(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.channel_post.text
        song_info = json.loads(text)
        poem_id = song_info.get("poem_id")
        id_ = song_info.get("id")
        audio_title = song_info.get("audio_title")
        audio_artist = song_info.get("audio_artist")
        download_url = song_info.get("download_url")
        duration = song_info.get("duration")
        source_page = song_info.get("source_page")
        DataBase().insert_song_data(poem_id, id_, audio_title, audio_artist, download_url, duration, source_page)

    @staticmethod
    async def add_song_file_id_to_db(update: Update, context: ContextTypes.DEFAULT_TYPE):
        file_id = update.channel_post.audio.file_id
        song_id = int(update.channel_post.caption)
        DataBase().add_song_file_id(file_id, song_id)
