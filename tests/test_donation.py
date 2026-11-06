import asyncio
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

from telegram.error import BadRequest
from telegram.ext import ConversationHandler, MessageHandler, filters

import const
import donation
from app import Application
from config import settings
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


def test_admin_notice_includes_the_refund_command(monkeypatch):
    context = run_successful_payment(monkeypatch, MagicMock())
    admin_notice = context.bot.send_message.call_args_list[1].args[1]
    assert "<code>/refund charge-1</code>" in admin_notice


def run_refund(monkeypatch, database: MagicMock, args: list[str], from_admin: bool = True) -> MagicMock:
    monkeypatch.setattr(donation, "DataBase", lambda: database)
    update = MagicMock()
    update.message.from_user.id = settings.ADMIN_CHAT_ID if from_admin else settings.ADMIN_CHAT_ID + 1
    update.effective_chat.id = 1
    context = MagicMock()
    context.args = args
    context.bot.send_message = AsyncMock()
    context.bot.refund_star_payment = AsyncMock()
    asyncio.run(Donate.refund(update, context))
    return context


def test_refund_refunds_the_donor_and_marks_the_donation(monkeypatch):
    database = MagicMock()
    database.get_donation.return_value = {"user_id": 42, "amount": 10, "refunded_at": None}
    context = run_refund(monkeypatch, database, ["charge-1"])
    context.bot.refund_star_payment.assert_awaited_once_with(42, "charge-1")
    assert database.mark_donation_refunded.call_args.args[0] == "charge-1"


def test_refund_is_admin_only(monkeypatch):
    database = MagicMock()
    context = run_refund(monkeypatch, database, ["charge-1"], from_admin=False)
    context.bot.refund_star_payment.assert_not_awaited()
    database.get_donation.assert_not_called()


def test_refund_of_an_unknown_charge_is_reported(monkeypatch):
    database = MagicMock()
    database.get_donation.return_value = None
    context = run_refund(monkeypatch, database, ["unknown"])
    context.bot.refund_star_payment.assert_not_awaited()
    assert context.bot.send_message.call_args.args[1] == const.REFUND_NOT_FOUND


def test_a_donation_is_not_refunded_twice(monkeypatch):
    database = MagicMock()
    database.get_donation.return_value = {"user_id": 42, "amount": 10, "refunded_at": datetime.now(UTC)}
    context = run_refund(monkeypatch, database, ["charge-1"])
    context.bot.refund_star_payment.assert_not_awaited()
    assert context.bot.send_message.call_args.args[1] == const.REFUND_ALREADY_REFUNDED


def test_a_failed_refund_is_reported_and_not_marked(monkeypatch):
    database = MagicMock()
    database.get_donation.return_value = {"user_id": 42, "amount": 10, "refunded_at": None}
    monkeypatch.setattr(donation, "DataBase", lambda: database)
    update = MagicMock()
    update.message.from_user.id = settings.ADMIN_CHAT_ID
    context = MagicMock()
    context.args = ["charge-1"]
    context.bot.send_message = AsyncMock()
    context.bot.refund_star_payment = AsyncMock(side_effect=BadRequest("CHARGE_ALREADY_REFUNDED"))
    asyncio.run(Donate.refund(update, context))
    database.mark_donation_refunded.assert_not_called()
    assert context.bot.send_message.call_args.args[1] == const.REFUND_FAILED.format(error="CHARGE_ALREADY_REFUNDED")


def test_refund_without_a_charge_id_shows_the_usage(monkeypatch):
    context = run_refund(monkeypatch, MagicMock(), [])
    assert context.bot.send_message.call_args.args[1] == const.REFUND_USAGE
