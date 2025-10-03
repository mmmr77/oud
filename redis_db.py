from config import settings
import redis

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class RedisDB(metaclass=Singleton):
    def __init__(self) -> None:
        """Establishes a connection to the Redis database."""
        try:
            self.client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT,
                                      password=settings.REDIS_PASSWORD)
            if self.client.ping():
                print("Successfully connected to Redis.")
            else:
                raise "Could not connect to Redis."
        except Exception as e:
            raise f"An error occurred while connecting to Redis: {e}"
        self.key_prefix = "q:"

    def __del__(self) -> None:
        self.client.close()

    def store(self, key, value) -> None:
        self.client.set(self.key_prefix + key, value)

    def get(self, key):
        return self.client.get(self.key_prefix + key)
