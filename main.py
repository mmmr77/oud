import logging

import sentry_sdk

from app import Application
from config import settings
from db_sync import upgrade_database_changes
from elastic_sync import sync_on_startup

if __name__ == '__main__':

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    sentry_sdk.init(
        dsn=f"https://{settings.SENTRY_TOKEN}@{settings.SENTRY_HOST}/{settings.SENTRY_ID}",
        traces_sample_rate=1.0,
    )

    if settings.DEBUG:
        token = settings.TEST_TOKEN
    else:
        token = settings.TOKEN

    upgrade_database_changes()
    sync_on_startup()

    application = Application(token)
    application.start_app()
