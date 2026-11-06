import asyncio
from unittest.mock import AsyncMock, MagicMock

from telegram.ext import ConversationHandler, MessageHandler, filters

import const
import donation
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


def run_successful_payment(monkeypatch, database: MagicMock) -> MagicMock:
    monkeypatch.setattr(donation, "DataBase", lambda: database)
    update = MagicMock()
    update.effective_user.id = 42
    update.effective_user.first_name = "Ali"
    update.effective_user.username = None
    update.effective_chat.id = 42
    payment = update.message.successful_payment
    payment.total_amount = 10
    payment.currency = "XTR"
    payment.telegram_payment_charge_id = "charge-1"
    context = MagicMock()
    context.bot.send_message = AsyncMock()
    asyncio.run(Donate.donate_stars_successful(update, context))
    return context


def test_successful_payment_is_recorded_with_its_charge_id(monkeypatch):
    database = MagicMock()
    context = run_successful_payment(monkeypatch, database)
    args = database.insert_donation.call_args.args
    assert args[:4] == (42, 10, "XTR", "charge-1")
    assert context.bot.send_message.call_args_list[0].args == (42, const.DONATE_THANKS)


def test_user_is_thanked_even_if_recording_the_donation_fails(monkeypatch):
    database = MagicMock()
    database.insert_donation.side_effect = RuntimeError("database is down")
    context = run_successful_payment(monkeypatch, database)
    assert context.bot.send_message.call_args_list[0].args == (42, const.DONATE_THANKS)
