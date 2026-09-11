from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.constants import ParseMode


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
