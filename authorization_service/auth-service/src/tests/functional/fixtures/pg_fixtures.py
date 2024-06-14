import backoff
import pytest_asyncio
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

from src.models.db_entity import Base, Permission, Role, RolePermission, User
from src.tests.functional.settings import test_base_settings as settings

dsn = f'postgresql+asyncpg://{settings.pg_user}:{settings.pg_password}@{settings.pg_host}:{settings.pg_port}/{settings.pg_db}'
engine = create_async_engine(dsn, echo=False, future=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(name='pg_insert_table_data')
def pg_insert_table_data():
    @backoff.on_exception(backoff.expo, Exception, max_time=30, jitter=backoff.random_jitter)
    async def inner(table_name, data: dict):
        async with engine.begin() as conn:

            statement = (
                insert(table_name).
                values(**data)
            )
            await conn.execute(statement=statement)
            await conn.commit()

    return inner


@pytest_asyncio.fixture(name='pg_clear_tables_data')
def pg_clear_tables_data():
    @backoff.on_exception(backoff.expo, Exception, max_time=30, jitter=backoff.random_jitter)
    async def inner():
        """Function to clean DB tables"""
        async with engine.begin() as conn:
            for table in reversed(Base.metadata.sorted_tables):
                await conn.execute(table.delete())
            await conn.commit()

    return inner
