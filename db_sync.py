from pathlib import Path
from urllib.parse import quote_plus

import psycopg2
from alembic.config import Config

from alembic import command
from config import settings


def _build_alembic_config() -> Config:
    config = Config(str(Path(__file__).with_name("alembic.ini")))
    user = quote_plus(str(settings.DB_USER))
    password = quote_plus(str(settings.DB_PASSWORD))
    host = settings.DB_HOST
    port = settings.DB_PORT
    database = settings.DB_NAME
    config.set_main_option("sqlalchemy.url", f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}")
    return config


def upgrade_database_changes() -> None:
    MIGRATION_LOCK_KEY = 734021771912345678

    connection = psycopg2.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        database=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT pg_advisory_lock(%s)", (MIGRATION_LOCK_KEY,))

        command.upgrade(_build_alembic_config(), "head")
    finally:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_unlock(%s)", (MIGRATION_LOCK_KEY,))
        finally:
            connection.close()
