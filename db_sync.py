from pathlib import Path
from urllib.parse import quote_plus

from alembic.config import Config

from alembic import command
from config import settings


def upgrade_database_changes() -> None:
    config = Config(str(Path(__file__).with_name("alembic.ini")))
    user = quote_plus(str(settings.DB_USER))
    password = quote_plus(str(settings.DB_PASSWORD))
    host = settings.DB_HOST
    port = settings.DB_PORT
    database = settings.DB_NAME
    config.set_main_option("sqlalchemy.url", f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}")

    command.upgrade(config, "head")
