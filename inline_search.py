import asyncio
import logging

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Update,
)
from telegram.constants import ParseMode
from telegram.error import TelegramError
from telegram.ext import ContextTypes

from config import settings
from db import DataBase
from elastic_db import ElasticSearchDB
from util import Util

logger = logging.getLogger(__name__)

MIN_QUERY_LENGTH = 3
CACHE_TIME_SECONDS = 30


class InlineSearch:
    @staticmethod
    async def handle_inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        assert update.inline_query is not None
        search_text = update.inline_query.query.strip()

        if len(search_text) < MIN_QUERY_LENGTH:
            await InlineSearch._answer(update, [])
            return

        offset = int(update.inline_query.offset) if update.inline_query.offset else 0

        try:
            search_results, total_search_count = await asyncio.to_thread(
                ElasticSearchDB().perform_search, search_text, offset)
        except RuntimeError:
            logger.exception("Inline search failed for query %r", search_text)
            await InlineSearch._answer(update, [])
            return

        built_results = await asyncio.gather(*[
            InlineSearch._build_result_for_hit(hit, offset + i, context.bot.username)
            for i, hit in enumerate(search_results)
        ])
        results = [result for result in built_results if result is not None]
        next_offset = InlineSearch.compute_next_offset(offset, len(search_results), total_search_count)

        await InlineSearch._answer(update, results, next_offset=next_offset)

    @staticmethod
    async def _build_result_for_hit(result: dict, position: int,
                                    bot_username: str) -> InlineQueryResultArticle | None:
        poem_text, poem_info = await asyncio.gather(
            asyncio.to_thread(DataBase().get_poem_text, result['id']),
            asyncio.to_thread(DataBase().get_poem_info, result['id']),
        )
        if not poem_text or poem_info is None:
            return None
        return InlineSearch.build_result(result, position, poem_text, poem_info, bot_username)

    @staticmethod
    async def _answer(update: Update, results: list, next_offset: str = "") -> None:
        assert update.inline_query is not None
        try:
            await update.inline_query.answer(results, next_offset=next_offset,
                                             cache_time=CACHE_TIME_SECONDS, is_personal=False)
        except TelegramError:
            logger.warning("Failed to answer inline query.")

    @staticmethod
    def build_result(result: dict, position: int, poem_text: list[dict], poem_info: dict,
                     bot_username: str) -> InlineQueryResultArticle:
        title = f"{result['title']} - {result['name']}"
        description = result['text'].replace('<b>', '').replace('</b>', '')
        messages = Util.break_long_poems(Util.break_long_verses(poem_text), poem_info, bot_username)
        button = InlineKeyboardButton('مشاهده در ربات', url=f"https://t.me/{bot_username}?start={result['id']}")
        return InlineQueryResultArticle(
            id=f"{result['id']}:{position}",
            title=title,
            description=description,
            input_message_content=InputTextMessageContent(messages[0], parse_mode=ParseMode.HTML),
            reply_markup=InlineKeyboardMarkup([[button]]),
        )

    @staticmethod
    def compute_next_offset(offset: int, results_in_page: int, total_search_count: int) -> str:
        if offset + results_in_page < total_search_count and offset < settings.SEARCH_RESULT_PER_PAGE * 2:
            return str(offset + results_in_page)
        return ""
