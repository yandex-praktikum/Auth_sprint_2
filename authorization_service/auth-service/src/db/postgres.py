from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import DeclarativeBase

from src.core.api_settings import settings


# Base class for all further models
class Base(DeclarativeBase):
    pass


# Add DB engine
dsn = f'postgresql+asyncpg://{settings.pg_user}:{settings.pg_password}@{settings.pg_host}:{settings.pg_port}/{settings.pg_db}'
engine = create_async_engine(dsn, echo=True, future=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_pg_session() -> AsyncSession:
    async with async_session() as session:
        yield session
