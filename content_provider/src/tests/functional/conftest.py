import json

import aiohttp
import pytest
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from redis.asyncio import Redis
from tests.functional.settings import test_settings
from tests.functional.testdata.es_mapping import (schema_genres, schema_movies,
                                                  schema_persons)


@pytest.fixture
async def es_client():
    elastic_url = f'http://{test_settings.ELASTIC_HOST}:{test_settings.ELASTIC_PORT}'
    client = AsyncElasticsearch(hosts=elastic_url)
    for es_index, schema in [('movies', schema_movies),
                             ('genres', schema_genres),
                             ('persons', schema_persons)]:
        if await client.indices.exists(index=es_index):
            await client.indices.delete(index=es_index)
        await client.indices.create(index=es_index, **schema)
    yield client
    await client.close()


@pytest.fixture
async def http_session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


def get_es_bulk_query(es_data, es_index):
    bulk_query: list[dict] = []
    for row in es_data:
        data = {'_index': es_index, '_id': row['id']}
        data.update({'_source': row})
        bulk_query.append(data)
    return bulk_query


@pytest.fixture
def es_write_data(es_client: AsyncElasticsearch):
    async def inner(data: list[dict], es_index: str):
        bulk_query = get_es_bulk_query(data, es_index)
        updated, errors = await async_bulk(client=es_client,
                                           actions=bulk_query,
                                           refresh="wait_for")
        if errors:
            raise Exception('Ошибка записи данных в Elasticsearch')
    return inner


@pytest.fixture
def es_delete_data(es_client: AsyncElasticsearch):
    async def inner(es_index: str):
        await es_client.delete_by_query(index=es_index, body={"query": {"match_all": {}}})
    return inner


@pytest.fixture
def get_data_from_api(http_session):
    async def inner(url: str):
        async with http_session.get(url) as response:
            body = await response.json()
            headers = response.headers
            status = response.status
        return body, headers, status
    return inner


@pytest.fixture
def get_list_data_from_api(http_session):
    async def inner(url: str):
        async with http_session.get(url) as response:
            body = await response.read()
            headers = response.headers
            status = response.status
            res = json.loads(body.decode())
        return res, headers, status
    return inner


@pytest.fixture()
async def redis_client():
    redis_client = Redis(host=test_settings.REDIS_HOST, port=test_settings.REDIS_PORT)
    yield redis_client
    await redis_client.flushall()
    await redis_client.aclose()
