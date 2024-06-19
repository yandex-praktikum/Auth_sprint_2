from redis.asyncio import Redis

from core.config import settings

redis: Redis | None = Redis(host=settings.redis_host, port=settings.redis_port)


# Функция понадобится при внедрении зависимостей
async def get_redis() -> Redis:
    return redis
