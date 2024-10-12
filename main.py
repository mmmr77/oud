import logging

from app import Application
from config import settings
from db_init import init_database

if __name__ == '__main__':

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    if settings.DEBUG:
        token = settings.TEST_TOKEN
    else:
        token = settings.TOKEN

    init_database()

    application = Application(token)
    application.start_app()
