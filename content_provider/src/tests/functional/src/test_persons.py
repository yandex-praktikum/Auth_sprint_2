import random
import string
import uuid
from http import HTTPStatus

import pytest
from tests.functional.settings import test_settings


ES_INDEX = 'persons'
data_len = random.randint(1, 50)
data = [{
        'id': str(uuid.uuid4()),
        'full_name': ''.join(random.choices(string.ascii_letters, k=5)),
        'roles': ''.join(random.choices(string.ascii_letters, k=5)),
        'films': [{
                    "filmwork_id": str(uuid.uuid4()),
                    "roles": [''.join(random.choices(string.ascii_letters, k=5))],
                    'title': ''.join(random.choices(string.ascii_letters, k=5)),
                    'imdb_rating': random.uniform(0, 10)
                } for _ in range(data_len)]
        } for _ in range(data_len)]
base_url = f'http://{test_settings.FASTAPI_HOST}:{test_settings.FASTAPI_PORT}/api/v1/{ES_INDEX}/'


@pytest.mark.asyncio
async def test_get_by_id(es_write_data, get_data_from_api):
    await es_write_data([data[0]], ES_INDEX)

    url = base_url + f'{data[0]["id"]}'
    body, headers, status = await get_data_from_api(url)

    assert status == HTTPStatus.OK
    assert body["uuid"] == data[0]["id"]


@pytest.mark.asyncio
async def test_get_by_id_not_found(es_write_data, get_data_from_api):
    await es_write_data([data[0]], ES_INDEX)

    url = base_url + f'{str(uuid.uuid4())}'
    body, headers, status = await get_data_from_api(url)

    assert status == HTTPStatus.NOT_FOUND
    assert body["detail"] == 'person not found'


@pytest.mark.asyncio
async def test_get_by_id_from_cache(redis_client, es_write_data, get_data_from_api, es_delete_data):
    await es_write_data([data[0]], ES_INDEX)

    url = base_url + f'{data[0]["id"]}'
    await get_data_from_api(url)
    await es_delete_data(ES_INDEX)
    body, headers, status = await get_data_from_api(url)

    assert status == HTTPStatus.OK
    assert body["uuid"] == data[0]["id"]


@pytest.mark.asyncio
async def test_search(es_write_data, get_data_from_api, es_delete_data):
    phrase = 'Krill'
    es_data = [{
        'id': str(uuid.uuid4()),
        'full_name': 'Kirill',
        'roles': 'actor',
        'films': [{
            "filmwork_id": str(uuid.uuid4()),
            "roles": [
                'some_role'
            ],
            'title': 'some_title',
            'imdb_rating': 4.7
        }]
    },
        {
            'id': str(uuid.uuid4()),
            'full_name': 'Stepan',
            'roles': 'actor',
            'films': [{
                "filmwork_id": str(uuid.uuid4()),
                "roles": [
                    'some_role'
                ],
                'title': 'some_title',
                'imdb_rating': 4.9
            }]
        }
    ]
    await es_write_data(es_data, ES_INDEX)

    url = base_url + f'search?phrase={phrase}'
    body, headers, status = await get_data_from_api(url)

    assert status == HTTPStatus.OK
    assert len(body) == 1


@pytest.mark.asyncio
async def test_films_by_person(es_write_data, get_data_from_api, es_delete_data):
    await es_write_data([data[0]], ES_INDEX)

    url = base_url + f'{data[0]["id"]}/films'
    body, headers, status = await get_data_from_api(url)

    assert status == HTTPStatus.OK
    assert len(body["items"]) == len(data[0]['films'])
