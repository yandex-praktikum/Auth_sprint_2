from fastapi import FastAPI

import logging.config
from contextlib import asynccontextmanager

from core.logger import LOGGING
from db import elastic, redis
from helpers.jaeger import configure_tracer


@asynccontextmanager
async def lifespan(app: FastAPI):
    from core.config import settings

    await elastic.es.info()
    await redis.redis.initialize()
    logging.config.dictConfig(LOGGING)
    if settings.jaeger_enable_tracer:
        configure_tracer(
            settings.jaeger_host,
            settings.jaeger_port,
            settings.service_name,
        )
    yield
    await redis.redis.close()
    await elastic.es.close()
