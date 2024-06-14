import asyncio

import pytest_asyncio

pytest_plugins = [
    "src.tests.functional.fixtures.redis_fixtures",
    "src.tests.functional.fixtures.client_fixtures",
    "src.tests.functional.fixtures.pg_fixtures",
    "src.tests.functional.fixtures.jwt_fixtures"
]


@pytest_asyncio.fixture(scope='session')
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
