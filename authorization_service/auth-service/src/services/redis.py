from functools import lru_cache

import backoff
import requests
from fastapi import Depends
from redis.asyncio import Redis

from src.db.redis_db import get_redis

BACKOFF_SETTINGS = {
    'wait_gen': backoff.expo,
    'exception': (requests.exceptions.ConnectionError, requests.exceptions.HTTPError, requests.exceptions.Timeout),
    'max_time': 300,
    'max_tries': 10
}


class RedisService:
    """
    A class to combine all the Redis operations in the one place.
    """

    def __init__(self, redis: Redis):
        self.redis = redis

    @staticmethod
    async def get_redis_key(user_id: str, session_id: str) -> str:
        """
        Generate key value for refresh_token to save it Redis.
        """
        return f'{user_id}:{session_id}'

    @backoff.on_exception(**BACKOFF_SETTINGS)
    async def save_refresh_token(self, user_id: str, session_id: str, expire_time_sec: int) -> None:
        """
        Save refresh_token in Redis.
        """
        key = await self.get_redis_key(user_id, session_id)
        await self.redis.setex(
            name=key,
            value='rt',
            time=expire_time_sec
        )

    @backoff.on_exception(**BACKOFF_SETTINGS)
    async def del_refresh_token(self, user_id: str, session_id: str) -> None:
        """
        Set exp time now for refresh_token in Redis.
        """
        key = await self.get_redis_key(user_id, session_id)
        await self.redis.expire(name=key, time=0)

    @backoff.on_exception(**BACKOFF_SETTINGS)
    async def get_value_by_key(self, key: str) -> str:
        """
        Get value from Redis by key.
        """

        result = await self.redis.get(name=key)

        return result


@lru_cache()
def get_redis_service(
    redis: Redis = Depends(get_redis),
) -> RedisService:
    """Provider of RedisService.

    :param redis: An async Redis exemplar which represents async connection to Redis.
    :return: A Singleton of RedisService.
    """
    return RedisService(redis)
