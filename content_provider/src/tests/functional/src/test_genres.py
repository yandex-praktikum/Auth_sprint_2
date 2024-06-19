import random
import string
import uuid
from http import HTTPStatus

import pytest
from tests.functional.settings import test_settings

ES_INDEX = 'genres'
data_len = random.randint(1, 100)
data = [{
        'id': str(uuid.uuid4()),
        'name': ''.join(random.choices(string.ascii_letters, k=5)),
        } for _ in range(data_len)]
base_url = f'http://{test_settings.FASTAPI_HOST}:{test_settings.FASTAPI_PORT}/api/v1/{ES_INDEX}/'


@pytest.mark.asyncio
async def test_list(es_write_data, get_list_data_from_api):
    await es_write_data(data, ES_INDEX)

    url = base_url + f'?size={data_len}'
    body, headers, status = await get_list_data_from_api(url)

    assert status == HTTPStatus.OK
    assert len(body['items']) == data_len


@pytest.mark.asyncio
async def test_get_by_id(es_write_data, get_data_from_api):
    await es_write_data([data[0]], ES_INDEX)

    url = base_url + f'{data[0]["id"]}'
    body, headers, status = await get_data_from_api(url)

    assert status == HTTPStatus.OK
    assert body['id'] == data[0]['id']


@pytest.mark.asyncio
async def test_get_by_id_not_found(es_write_data, get_data_from_api):
    await es_write_data([data[0]], ES_INDEX)

    url = base_url + f'{str(uuid.uuid4())}'
    body, headers, status = await get_data_from_api(url)

    assert status == HTTPStatus.NOT_FOUND
    assert body['detail'] == 'genre not found'


@pytest.mark.asyncio
async def test_get_by_id_from_cache(redis_client, es_write_data, get_data_from_api, es_delete_data):
    await es_write_data([data[0]], ES_INDEX)

    url = base_url + f'{data[0]["id"]}'
    await get_data_from_api(url)
    await es_delete_data(ES_INDEX)
    body, headers, status = await get_data_from_api(url)

    assert status == HTTPStatus.OK
    assert body['id'] == data[0]['id']
    assert body['name'] == data[0]['name']
