import logging

from requests import Session

from .models import Recitation

logger = logging.getLogger(__name__)

PUBLISHED_RECITATIONS_URL = (
    "https://api.ganjoor.net/api/audio/published?PageNumber={page}&poetId=0&catId=0"
)
MAX_CONSECUTIVE_PAGE_FAILURES = 3


def _fetch_page(session: Session, page: int) -> list[dict]:
    response = session.get(
        PUBLISHED_RECITATIONS_URL.format(page=page),
        headers={"Accept": "application/json"},
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


def fetch_all_recitation_metadata(session: Session) -> list[Recitation]:
    recitations: list[Recitation] = []
    page = 1
    consecutive_failures = 0
    fetched_pages = 0
    skipped_pages = 0

    while True:
        try:
            raw_items = _fetch_page(session, page)
        except Exception:
            logger.warning("failed to fetch metadata page %d; skipping", page, exc_info=True)
            skipped_pages += 1
            consecutive_failures += 1
            if consecutive_failures >= MAX_CONSECUTIVE_PAGE_FAILURES:
                logger.error(
                    "aborting metadata fetch after %d consecutive page failures",
                    consecutive_failures,
                )
                break
            page += 1
            continue

        consecutive_failures = 0
        if not raw_items:
            break

        for item in raw_items:
            try:
                recitations.append(Recitation.from_api(item))
            except (KeyError, TypeError):
                logger.warning("skipping malformed metadata item: %r", item, exc_info=True)

        fetched_pages += 1
        page += 1

    summary_log = logger.warning if skipped_pages else logger.info
    summary_log(
        "metadata fetch complete: %d recitation(s) from %d page(s), %d page(s) skipped",
        len(recitations),
        fetched_pages,
        skipped_pages,
    )
    return recitations


def download_audio(session: Session, recitation: Recitation) -> bytes | None:
    response = session.get(recitation.mp3_url, timeout=60)
    if response.status_code == 404:
        logger.warning("recitation %d audio not found (404): %s", recitation.id, recitation.mp3_url)
        return None
    response.raise_for_status()
    logger.info("downloaded audio for recitation %d", recitation.id)
    return response.content
