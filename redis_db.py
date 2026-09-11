import logging
from typing import cast

import redis

from config import settings
from singleton import Singleton


class RedisDB(metaclass=Singleton):
    def __init__(self) -> None:
        """Establishes a connection to the Redis database."""
        try:
            self.client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT,
                                      password=settings.REDIS_PASSWORD, decode_responses=True)
            if self.client.ping():
                logging.info("Successfully connected to Redis.")
            else:
                raise RuntimeError("Could not connect to Redis.")
        except Exception as e:
            raise RuntimeError(f"An error occurred while connecting to Redis: {e}") from e
        self.key_prefix = "q:"

    def __del__(self) -> None:
        self.client.close()

    def store(self, key: str, value: str) -> None:
        self.client.set(self.key_prefix + key, value, ex=3 * 30 * 24 * 60 * 60)

    def get(self, key: str) -> str | None:
        # redis-py types get() as ResponseT (Awaitable[Any] | Any) since one class serves sync and async;
        # our client is synchronous with decode_responses=True, so it returns str | None.
        return cast("str | None", self.client.get(self.key_prefix + key))
