import logging
from datetime import UTC, datetime, timedelta

from prometheus_client import Gauge, start_http_server
from telegram import Update
from telegram.ext import ContextTypes

from config import settings
from db import DataBase

logger = logging.getLogger(__name__)

ACTIVE_USERS_GAUGE = Gauge(
    "oud_active_users",
    "Number of active users in rolling windows",
    ["window"],
)


async def record_user_activity(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    chat = update.effective_chat
    if user is None or chat is None or user.is_bot or chat.type != "private":
        return

    seen_at = datetime.now(UTC)
    try:
        DataBase().upsert_user_activity(
            user_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            seen_at=seen_at,
        )
    except Exception:
        logger.exception("Failed to record user activity", extra={"user_id": user.id})


async def refresh_active_user_metrics(_: ContextTypes.DEFAULT_TYPE) -> None:
    now = datetime.now(UTC)
    windows = {
        "24h": now - timedelta(hours=24),
        "7d": now - timedelta(days=7),
        "30d": now - timedelta(days=30),
    }

    try:
        for window, since_dt in windows.items():
            ACTIVE_USERS_GAUGE.labels(window=window).set(DataBase().count_active_users_since(since_dt))
    except Exception:
        logger.exception("Failed to refresh active user metrics")


def start_metrics_server() -> None:
    start_http_server(port=settings.METRICS_PORT, addr="0.0.0.0")
    logger.info(
        "Prometheus metrics server started.",
        extra={"port": settings.METRICS_PORT},
    )
