import asyncio
import logging

from telegram import InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.constants import ParseMode
from telegram.error import TelegramError
from telegram.ext import ContextTypes

from config import settings
from elastic_db import ElasticSearchDB

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

        results = [InlineSearch.build_result(result, offset + i) for i, result in enumerate(search_results)]
        next_offset = InlineSearch.compute_next_offset(offset, len(search_results), total_search_count)

        await InlineSearch._answer(update, results, next_offset=next_offset)

    @staticmethod
    async def _answer(update: Update, results: list, next_offset: str = "") -> None:
        assert update.inline_query is not None
        try:
            await update.inline_query.answer(results, next_offset=next_offset,
                                             cache_time=CACHE_TIME_SECONDS, is_personal=False)
        except TelegramError:
            logger.warning("Failed to answer inline query.")

    @staticmethod
    def build_result(result: dict, position: int) -> InlineQueryResultArticle:
        title = f"{result['title']} - {result['name']}"
        description = result['text'].replace('<b>', '').replace('</b>', '')
        return InlineQueryResultArticle(
            id=f"{result['id']}:{position}",
            title=title,
            description=description,
            input_message_content=InputTextMessageContent(result['text'], parse_mode=ParseMode.HTML),
        )

    @staticmethod
    def compute_next_offset(offset: int, results_in_page: int, total_search_count: int) -> str:
        more_results_exist = offset + results_in_page < total_search_count
        under_depth_cap = offset < settings.SEARCH_RESULT_PER_PAGE * 2
        if more_results_exist and under_depth_cap:
            return str(offset + results_in_page)
        return ""
