import asyncio
from unittest.mock import AsyncMock, MagicMock

from telegram.ext import ConversationHandler, MessageHandler, filters

import const
from app import Application
from donation import Donate


def test_checkout_for_an_offered_amount_is_valid():
    assert Donate.is_valid_checkout("XTR", 10, Donate.build_payload(10))


def test_checkout_for_an_amount_not_offered_is_rejected():
    assert not Donate.is_valid_checkout("XTR", 7, Donate.build_payload(7))


def test_checkout_whose_payload_does_not_match_the_amount_is_rejected():
    assert not Donate.is_valid_checkout("XTR", 1, Donate.build_payload(100))


def test_checkout_in_another_currency_is_rejected():
    assert not Donate.is_valid_checkout("USD", 10, Donate.build_payload(10))


def test_no_invoice_is_sent_for_an_amount_not_offered():
    update = MagicMock()
    update.callback_query.data = "donate:1000000"
    update.callback_query.answer = AsyncMock()
    context = MagicMock()
    context.bot.send_invoice = AsyncMock()

    asyncio.run(Donate.donate_stars(update, context))

    context.bot.send_invoice.assert_not_awaited()
    update.callback_query.answer.assert_awaited_once_with(const.DONATE_INVALID_AMOUNT, show_alert=True)


def test_invoice_is_in_stars_for_the_chosen_amount():
    update = MagicMock()
    update.callback_query.data = "donate:50"
    update.callback_query.answer = AsyncMock()
    context = MagicMock()
    context.bot.send_invoice = AsyncMock()

    asyncio.run(Donate.donate_stars(update, context))

    invoice = context.bot.send_invoice.call_args.kwargs
    assert invoice["currency"] == "XTR"
    assert [price.amount for price in invoice["prices"]] == [50]
    assert invoice["payload"] == Donate.build_payload(50)


def test_successful_payments_are_not_swallowed_by_open_conversations():
    application = MagicMock()
    Application.add_handlers(MagicMock(application=application))
    handlers = application.add_handlers.call_args.args[0]
    payment_index = next(i for i, handler in enumerate(handlers) if isinstance(handler, MessageHandler)
                         and handler.filters is filters.SUCCESSFUL_PAYMENT)
    first_conversation_index = next(i for i, handler in enumerate(handlers)
                                    if isinstance(handler, ConversationHandler))
    assert payment_index < first_conversation_index
