import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from src.api.v1 import (admin_roles, admin_user_permissions, authentication,
                        personal_account, registration)
from src.core.api_settings import settings
from src.core.logger import setup_logging
from src.db import redis_db
from src.models.db_entity import create_database, purge_database

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup events
    logging.info('Config: %s', vars(settings))
    redis_db.redis = Redis(host=settings.redis_host, port=settings.redis_port)
    # Creating and filling DB
    await create_database()
    yield
    # On shutdown events
    # await purge_database()
    await redis_db.redis.close()

app = FastAPI(
    lifespan=lifespan,
    title=settings.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    description='Auth API endpoints',
    version='1.0.0'
)

app.include_router(registration.router, prefix="/api/v1", tags=['Registration'])
app.include_router(authentication.router, prefix="/api/v1", tags=['Authentication'])
app.include_router(personal_account.router, prefix="/api/v1", tags=['Personal account'])
app.include_router(admin_roles.router, prefix="/api/v1", tags=['Administrate roles'])
app.include_router(admin_user_permissions.router, prefix="/api/v1", tags=['Administrate user permissions'])


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8001,
    )
