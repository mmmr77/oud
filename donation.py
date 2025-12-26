from uuid import uuid4

from telegram import Update, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import const
from util import Util

# TODO: improve text messages.

class Donate:
    @staticmethod
    async def donate_intro(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        donation_titles = ["1 Star", "5 Stars", "10 Stars", "20 Stars", "50 Stars", "100 Stars"]
        donation_callbacks = ["donate:1", "donate:5", "donate:10", "donate:20", "donate:50", "donate:100"]
        buttons = Util.create_inline_buttons(2, 6, donation_titles, donation_callbacks)
        keyboard = InlineKeyboardMarkup(buttons)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=const.DONATE, parse_mode=ParseMode.HTML,
                                       reply_markup=keyboard, disable_web_page_preview=True)

    @staticmethod
    async def donate_stars(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()
        amount = int(query.data.split(':')[1])
        prices = [LabeledPrice(label=f"{amount} Stars", amount=amount)]
        await context.bot.send_invoice(
            chat_id=update.effective_chat.id,
            title="حمایت از ربات عود",
            description="حمایت با ستاره‌های تلگرام",
            payload=str(uuid4()),
            provider_token="",
            currency="XTR",
            prices=prices,
        )

    @staticmethod
    async def donate_stars_pre_checkout(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.pre_checkout_query
        await query.answer(ok=True)

    @staticmethod
    async def donate_stars_sucessful(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        # TODO: Store in database.
        context.bot.send_message(update.effective_user.id, "ممنون از حمایت‌تان!")
