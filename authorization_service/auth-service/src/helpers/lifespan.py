import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from redis.asyncio import Redis
from fastapi_limiter import FastAPILimiter

from src.db import redis_db
from src.models.db_entity import create_database, purge_database
from src.helpers.jaeger import configure_tracer


@asynccontextmanager
async def lifespan(app: FastAPI):
    from src.core.api_settings import settings

    # On startup events
    logging.info('Config: %s', vars(settings))
    redis_db.redis = Redis(host=settings.redis_host, port=settings.redis_port)
    await FastAPILimiter.init(redis_db.redis)

    # Creating and filling DB
    if settings.jaeger_enable_tracer:
        configure_tracer(
            settings.jaeger_host,
            settings.jaeger_port,
            settings.service_name,
        )
    await create_database()
    yield
    # On shutdown events
    # await purge_database()
    await redis_db.redis.close()
