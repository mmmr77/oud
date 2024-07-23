import logging
import os

from dotenv import load_dotenv

import setting
from app import Application
from db_init import init_database

if __name__ == '__main__':
    load_dotenv()

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    if setting.DEBUG:
        token = os.environ.get("TEST_TOKEN")
    else:
        token = os.environ.get("TOKEN")

    init_database()

    application = Application(token)
    application.start_app()
