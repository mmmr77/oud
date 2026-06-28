import asyncio
import logging

from telegram.ext import ContextTypes

from config import settings
from db import DataBase

from . import ganjoor
from .client import RecitationUploader
from .http_client import build_session
from .selection import Action, build_plan

logger = logging.getLogger(__name__)


async def run_upload_job(_: ContextTypes.DEFAULT_TYPE) -> None:
    """Daily job: fetch recitations from Ganjoor, insert metadata, and upload audio to the files channel."""
    database = DataBase()
    with build_session() as session:
        recitations = await asyncio.to_thread(ganjoor.fetch_all_recitation_metadata, session)
        known_poem_ids = await asyncio.to_thread(database.get_existing_poem_ids)
        done_ids, incomplete_ids = await asyncio.to_thread(database.get_recitation_status)
        logger.info(
            "metadata=%d known_poems=%d done=%d incomplete=%d",
            len(recitations), len(known_poem_ids), len(done_ids), len(incomplete_ids),
        )

        plan = build_plan(recitations, done_ids, incomplete_ids, known_poem_ids, settings.MAX_UPLOADS_PER_RUN)
        logger.info("planned %d item(s) this run", len(plan))

        succeeded = failed = skipped = 0
        try:
            async with RecitationUploader() as uploader:
                for item in plan:
                    recitation = item.recitation
                    file_name = f"{recitation.id}-{recitation.poem_id}.mp3"
                    try:
                        # Download first: a 404 must never create a metadata-only orphan row.
                        audio = await asyncio.to_thread(ganjoor.download_audio, session, recitation)
                        if audio is None:
                            skipped += 1
                            continue
                        if item.action == Action.NEW:
                            await asyncio.to_thread(
                                database.insert_recitation_data,
                                recitation.poem_id, recitation.id, recitation.audio_title,
                                recitation.mp3_url, recitation.audio_artist, recitation.audio_order,
                                recitation.recitation_type,
                            )
                        await uploader.upload_audio(audio, file_name, recitation)
                        succeeded += 1
                        logger.info("uploaded recitation %d (%s)", recitation.id, item.action.value)
                    except Exception:
                        failed += 1
                        logger.exception("failed to process recitation %d", recitation.id)
        except RuntimeError:
            logger.exception("recitation upload aborted")
            return

    logger.info(
        "run complete: planned=%d succeeded=%d failed=%d skipped=%d",
        len(plan), succeeded, failed, skipped,
    )
