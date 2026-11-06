import html
import logging
from datetime import UTC, datetime

from persian_tools.digits import convert_to_fa
from telegram import InlineKeyboardMarkup, LabeledPrice, Update
from telegram.constants import ParseMode
from telegram.error import TelegramError
from telegram.ext import ContextTypes
from telegram.helpers import mention_html

import const
from admin import admin
from config import settings
from db import DataBase
from util import Util

logger = logging.getLogger(__name__)

# Telegram Stars amounts offered by the donate buttons; nothing else is invoiced or accepted at checkout.
DONATION_AMOUNTS = (1, 5, 10, 20, 50, 100)
STARS_CURRENCY = "XTR"


class Donate:
    @staticmethod
    def build_payload(amount: int) -> str:
        return f"donation:{amount}"

    @staticmethod
    def is_valid_checkout(currency: str, total_amount: int, payload: str) -> bool:
        """Checks that a checkout is for one of the offered amounts and matches the invoice the bot sent."""
        return (currency == STARS_CURRENCY and total_amount in DONATION_AMOUNTS
                and payload == Donate.build_payload(total_amount))

    @staticmethod
    async def donate_intro(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        assert update.effective_chat is not None
        donation_titles = [convert_to_fa(const.DONATE_BUTTON.format(amount=amount)) for amount in DONATION_AMOUNTS]
        donation_callbacks = [f"donate:{amount}" for amount in DONATION_AMOUNTS]
        buttons = Util.create_inline_buttons(2, len(DONATION_AMOUNTS), donation_titles, donation_callbacks)
        keyboard = InlineKeyboardMarkup(buttons)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=const.DONATE, parse_mode=ParseMode.HTML,
                                       reply_markup=keyboard, disable_web_page_preview=True)

    @staticmethod
    async def donate_stars(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        assert query is not None and query.data is not None and update.effective_chat is not None
        amount = int(query.data.split(':')[1])
        # Callback data comes from the client, so an amount the bot never offered is rejected.
        if amount not in DONATION_AMOUNTS:
            await query.answer(const.DONATE_INVALID_AMOUNT, show_alert=True)
            return
        await query.answer()
        prices = [LabeledPrice(label=convert_to_fa(const.DONATE_BUTTON.format(amount=amount)), amount=amount)]
        await context.bot.send_invoice(
            chat_id=update.effective_chat.id,
            title=const.DONATE_INVOICE_TITLE,
            description=const.DONATE_INVOICE_DESCRIPTION,
            payload=Donate.build_payload(amount),
            provider_token="",
            currency=STARS_CURRENCY,
            prices=prices,
        )

    @staticmethod
    async def donate_stars_pre_checkout(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.pre_checkout_query
        assert query is not None
        if Donate.is_valid_checkout(query.currency, query.total_amount, query.invoice_payload):
            await query.answer(ok=True)
        else:
            await query.answer(ok=False, error_message=const.DONATE_INVALID_AMOUNT)

    @staticmethod
    async def donate_stars_successful(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Records the donation, thanks the user and notifies the admin."""
        assert update.message is not None and update.message.successful_payment is not None
        assert update.effective_user is not None and update.effective_chat is not None
        payment = update.message.successful_payment
        user = update.effective_user
        # The user has already paid, so a failure to record the donation must not stop the thanks; the charge id is
        # logged so the donation can still be refunded or recorded by hand.
        try:
            DataBase().insert_donation(user.id, payment.total_amount, payment.currency,
                                       payment.telegram_payment_charge_id, datetime.now(UTC))
        except Exception:
            logger.exception("Failed to record donation %s of user %d", payment.telegram_payment_charge_id, user.id)
        await context.bot.send_message(update.effective_chat.id, const.DONATE_THANKS)

        text = const.DONATION_TO_ADMIN.format(amount=convert_to_fa(payment.total_amount),
                                              user=mention_html(user.id, user.first_name),
                                              username=Util.create_username_with_at(user.username),
                                              charge_id=html.escape(payment.telegram_payment_charge_id))
        await context.bot.send_message(settings.ADMIN_CHAT_ID, text, parse_mode=ParseMode.HTML)

    @staticmethod
    @admin
    async def refund(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Refunds a donation, given its telegram_payment_charge_id (included in the admin's donation notice)."""
        assert update.effective_chat is not None
        chat_id = update.effective_chat.id
        if not context.args or len(context.args) != 1:
            await context.bot.send_message(chat_id, const.REFUND_USAGE)
            return
        charge_id = context.args[0]
        donation = DataBase().get_donation(charge_id)
        if donation is None:
            await context.bot.send_message(chat_id, const.REFUND_NOT_FOUND)
            return
        if donation["refunded_at"] is not None:
            await context.bot.send_message(chat_id, const.REFUND_ALREADY_REFUNDED)
            return
        try:
            await context.bot.refund_star_payment(donation["user_id"], charge_id)
        except TelegramError as e:
            await context.bot.send_message(chat_id, const.REFUND_FAILED.format(error=e.message))
            return
        DataBase().mark_donation_refunded(charge_id, datetime.now(UTC))
        await context.bot.send_message(chat_id, const.REFUND_DONE.format(amount=convert_to_fa(donation["amount"]),
                                                                         user_id=donation["user_id"]))
