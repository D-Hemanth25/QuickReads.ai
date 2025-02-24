from redis import Redis
from .config import get_settings

settings = get_settings()

class RedisManager():
    _client: Redis = None

    @classmethod
    def get_client(cls) -> Redis:
        if cls._client is None:
            cls._client = Redis.from_url(
                settings.redis_url,
                decode_responses=True,
                socket_timeout=5,
                retry_on_timeout=True
            )
        return cls._client
    
    @classmethod
    def close(cls):
        if cls._client is not None:
            cls._client.close()
            cls._client = None
