import aiohttp
import backoff
import pytest_asyncio

from src.tests.functional.settings import test_base_settings


@pytest_asyncio.fixture(name='client_session', scope='session')
async def client_session() -> aiohttp.ClientSession:
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest_asyncio.fixture(name='api_make_get_request')
def api_make_get_request(client_session):
    @backoff.on_exception(backoff.expo, Exception, max_time=30, jitter=backoff.random_jitter)
    async def inner(endpoint: str, query_data: dict = None, headers: dict = None):
        """
        Send get request using aiohttp.
        """
        url = f'http://{test_base_settings.service_host}:{test_base_settings.service_port}'
        url += endpoint
        async with client_session.get(url, params=query_data, headers=headers) as response:
            body = await response.json()
            status = response.status
        return status, body

    return inner


@pytest_asyncio.fixture(name='api_make_post_request')
def api_make_post_request(client_session):
    @backoff.on_exception(backoff.expo, Exception, max_time=30, jitter=backoff.random_jitter)
    async def inner(query_data: dict, endpoint: str, headers: dict = None):
        """
        Send post request using aiohttp with form data body.
        """
        url = f'http://{test_base_settings.service_host}:{test_base_settings.service_port}'
        url += endpoint
        async with client_session.post(url, data=query_data, headers=headers) as response:
            body = await response.json()
            status = response.status
            rsp_headers = response.headers
        return status, body, rsp_headers

    return inner


@pytest_asyncio.fixture(name='api_post')
def api_post(client_session):
    @backoff.on_exception(backoff.expo, Exception, max_time=30, jitter=backoff.random_jitter)
    async def inner(body: dict, endpoint: str, headers: dict = None):
        """
        Send post request using aiohttp with json body.
        """
        url = f'http://{test_base_settings.service_host}:{test_base_settings.service_port}'
        url += endpoint
        async with client_session.post(url, json=body, headers=headers) as response:
            body = await response.json()
            status = response.status
            rsp_headers = response.headers
        return status, body, rsp_headers

    return inner


@pytest_asyncio.fixture(name='api_make_put_request')
def api_make_put_request(client_session):
    @backoff.on_exception(backoff.expo, Exception, max_time=30, jitter=backoff.random_jitter)
    async def inner(query_data: dict, endpoint: str, headers: dict):
        """
        :param query_data: {'query': 'The Star', 'page_number': 1, 'page_size': 50}
        :param endpoint: '/api/v1/account/{user_id}'
        :return:
        """
        url = f'http://{test_base_settings.service_host}:{test_base_settings.service_port}'
        url += endpoint
        async with client_session.put(url, params=query_data, headers=headers) as response:
            body = await response.json()
            status = response.status
        return status, body

    return inner


@pytest_asyncio.fixture(name='api_make_delete_request')
def api_make_delete_request(client_session):
    @backoff.on_exception(backoff.expo, Exception, max_time=30, jitter=backoff.random_jitter)
    async def inner(query_data: dict, endpoint: str, headers: dict):
        """
        :param query_data: {'query': 'The Star', 'page_number': 1, 'page_size': 50}
        :param endpoint: '/api/v1/account/{user_id}'
        :return:
        """
        url = f'http://{test_base_settings.service_host}:{test_base_settings.service_port}'
        url += endpoint
        async with client_session.delete(url, params=query_data, headers=headers) as response:
            body = await response.json()
            status = response.status
        return status, body

    return inner
