import asyncio
import logging

from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.tl.types import DocumentAttributeAudio

from config import settings

from .models import Recitation

logger = logging.getLogger(__name__)

SESSION_NAME = "my_account"
FLOOD_SLEEP_THRESHOLD = 60  # let Telethon auto-sleep floods up to this many seconds
FLOOD_RETRY_BUFFER_SECONDS = 5  # extra slack added to a reported flood wait
MAX_FLOOD_RETRIES = 5


class RecitationUploader:
    """Holds one Telethon user-account client for the duration of a run."""

    def __init__(self) -> None:
        self._client = TelegramClient(SESSION_NAME, settings.API_ID, settings.API_HASH)
        self._client.flood_sleep_threshold = FLOOD_SLEEP_THRESHOLD

    async def __aenter__(self) -> "RecitationUploader":
        # Connect without start(): start() would block on interactive login if the session is
        # missing/expired, which must never happen in a headless container. Guard explicitly.
        await self._client.connect()
        if not await self._client.is_user_authorized():
            await self._client.disconnect()
            raise RuntimeError("Telethon session is not authorized; provide a valid my_account.session")
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self._client.disconnect()

    @staticmethod
    async def _with_flood_retry(send):
        for attempt in range(1, MAX_FLOOD_RETRIES + 1):
            try:
                return await send()
            except FloodWaitError as error:
                wait = error.seconds + FLOOD_RETRY_BUFFER_SECONDS
                logger.warning(
                    "flood wait %ds (attempt %d/%d)", wait, attempt, MAX_FLOOD_RETRIES
                )
                if attempt < MAX_FLOOD_RETRIES:
                    await asyncio.sleep(wait)
        raise RuntimeError(f"exceeded {MAX_FLOOD_RETRIES} flood-wait retries")

    async def upload_audio(self, audio: bytes, file_name: str, recitation: Recitation) -> None:
        async def _send():
            uploaded = await self._client.upload_file(audio, file_name=file_name)
            await self._client.send_file(
                settings.OUD_FILES_CHANNEL_ID,
                uploaded,
                caption=str(recitation.id),
                attributes=[
                    DocumentAttributeAudio(
                        0, performer=recitation.audio_artist, title=recitation.audio_title
                    )
                ],
            )

        await self._with_flood_retry(_send)
