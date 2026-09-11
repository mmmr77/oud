from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.constants import ParseMode

from config import settings


class InlineSearch:
    @staticmethod
    def build_result(result: dict) -> InlineQueryResultArticle:
        title = f"{result['title']} - {result['name']}"
        description = result['text'].replace('<b>', '').replace('</b>', '')
        return InlineQueryResultArticle(
            id=str(result['id']),
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
