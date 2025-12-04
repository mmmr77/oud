import json

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from db import DataBase
from util import Util


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

    @staticmethod
    def get_songs(poem_id: int):
        songs = DataBase().get_songs(poem_id)
        artists = list(map(lambda x: x["artist"], songs))
        ids = list(map(lambda x: f'song:{x["id"]}', songs))
        if songs:
            keyboard = InlineKeyboardMarkup(Util.create_inline_buttons(2, len(songs), artists, ids))
            return len(songs), keyboard
        else:
            return 0, None

    @staticmethod
    async def get_song_by_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        song_id = int(query.data.split(':')[1])
        song = DataBase().get_song(song_id)
        await context.bot.send_audio(query.from_user.id, song["telegram_file_id"], performer=song["artist"],
                                     title=song["title"], duration=song["duration"])
