import asyncio

import backoff
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import create_async_engine

from tests.functional.settings import test_base_settings as settings


@backoff.on_exception(backoff.expo, Exception, max_time=300, max_tries=10)
async def wait_for_redis() -> None:
    print("Pinging Redis...")
    client = Redis(host=settings.redis_host, port=settings.redis_port)
    try:
        await client.ping()
        print("Redis is up!")
    finally:
        await client.close()


@backoff.on_exception(backoff.expo, Exception, max_time=300, max_tries=10)
async def wait_for_postgres() -> None:
    print("Pinging Postgres...")
    dsn = f'postgresql+asyncpg://{settings.pg_user}:{settings.pg_password}@{settings.pg_host}:{settings.pg_port}/{settings.pg_db}'
    engine = create_async_engine(dsn, echo=True, future=True)

    async with engine.begin() as conn:
        await conn.get_raw_connection()
        print("postgres is up!")


async def main():
    await asyncio.gather(
        wait_for_redis(),
        wait_for_postgres()
    )

if __name__ == '__main__':
    print("Waiting for Redis to start...")
    print("Waiting for Postgres to start...")
    asyncio.run(main())
