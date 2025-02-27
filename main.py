import logging

import sentry_sdk

from app import Application
from config import settings
from db_init import init_database

if __name__ == '__main__':

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    sentry_sdk.init(
        dsn=f"https://{settings.SENTRY_TOKEN}@{settings.SENTRY_HOST}/8059",
        traces_sample_rate=1.0,
    )

    if settings.DEBUG:
        token = settings.TEST_TOKEN
    else:
        token = settings.TOKEN

    init_database()

    application = Application(token)
    application.start_app()
