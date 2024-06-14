from http import HTTPStatus

import pytest

from src.tests.functional.fixtures.client_fixtures import api_make_post_request
from src.tests.functional.fixtures.jwt_fixtures import prepare_jwt_tokens
from src.tests.functional.fixtures.pg_fixtures import (User,
                                                       pg_clear_tables_data,
                                                       pg_insert_table_data)
from src.tests.functional.testdata.cookies import prepare_cookies
from src.tests.functional.testdata.jwt_tokens import JWTtokens
from src.tests.functional.testdata.pg_db_data_input import \
    user_login_data  # noqa: F401

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize('query_data, expected_status', [
    ({'username': 'admin@mail.com', 'password': '123qwe'}, HTTPStatus.OK),
    ({'username': 'admin@mail.com', 'password': 'lalalala'}, HTTPStatus.UNAUTHORIZED),
    ({'username': 'admin@mail.com', 'password': ''}, HTTPStatus.UNPROCESSABLE_ENTITY),
    ({'username': 'billy@mail.com', 'password': '123qwe'}, HTTPStatus.UNAUTHORIZED),
    ({'username': 'admin@mail.com'}, HTTPStatus.UNPROCESSABLE_ENTITY),
    ({'password': '123qwe'}, HTTPStatus.UNPROCESSABLE_ENTITY),

])
async def test_login_endpoint(
        pg_clear_tables_data,
        user_login_data,
        pg_insert_table_data,
        api_make_post_request, query_data, expected_status):
    """
    Test for /api/v1/login endpoint.
    Adding one valid user into the DB and then trying to log in
    with different credentials.
    Cookie logic is not tested there.
    """
    await pg_clear_tables_data()
    try:
        data = await user_login_data()
        await pg_insert_table_data(table_name=User, data=data)

        status, _, _ = await api_make_post_request(
            query_data=query_data,
            endpoint='/api/v1/login',
            )

        assert status == expected_status
    finally:
        await pg_clear_tables_data()


@pytest.mark.parametrize('query_data, expected_status', [
    ({'username': 'admin@mail.com', 'password': '123qwe'}, HTTPStatus.OK),

])
async def test_response_cookies_login_endpoint(
        pg_clear_tables_data,
        user_login_data,
        pg_insert_table_data,
        api_make_post_request, query_data, expected_status):
    """
    Test for /api/v1/login endpoint.
    Adding one valid user into the DB and then trying to log in.
    Checking if we received necessary Cookie in the response.
    """
    await pg_clear_tables_data()
    try:
        data = await user_login_data()
        await pg_insert_table_data(table_name=User, data=data)

        status, _, headers = await api_make_post_request(
            query_data=query_data,
            endpoint='/api/v1/login',
            )

        assert status == expected_status

        set_cookies = headers.getall('Set-Cookie')
        # Cheking if there are two Set-Cookie headers in the response
        assert len(set_cookies) == 2
        for cookie in set_cookies:
            # Cheking if Set-Cookie headers contain apropriate token names
            assert 'auth-app-access-key' in cookie or 'auth-app-refresh-key' in cookie
            # Cheking if Cookie configured as HttpOnly.
            assert 'HttpOnly' in cookie

    finally:
        await pg_clear_tables_data()


async def test_response_cookies_logout_endpoint(
        pg_clear_tables_data,
        pg_insert_table_data,
        api_make_post_request):
    """
    Test for /api/v1/logout endpoint.
    Adding one valid user into the DB and then trying to log out.
    Checking if we received necessary Cookie in the response.
    """

    jwt = JWTtokens()

    access_token, refresh_token = await jwt.get_token_pair(
        user_id='8ab71a54-7b99-4322-a07e-0b2a0c40ff44',
        session_id='22bd63b2-3d33-45b7-991b-d2e37662426a'
    )

    status, _, headers = await api_make_post_request(
        query_data={},
        endpoint='/api/v1/logout',
        headers={'Cookie': f'auth-app-access-key={access_token} ; auth-app-refresh-key={refresh_token}'}
        )

    assert status == HTTPStatus.NO_CONTENT

    set_cookies = headers.getall('Set-Cookie')
    # Cheking if there are two Set-Cookie headers in the response
    assert len(set_cookies) == 2
    for cookie in set_cookies:
        # Cheking if Set-Cookie headers contain apropriate token names
        assert 'auth-app-access-key' in cookie or 'auth-app-refresh-key' in cookie
        # Cheking if Cookie configured to expire.
        assert 'expires' in cookie


@pytest.mark.parametrize('cookies_params, tokens_params, expected_status', [
    ({}, {}, HTTPStatus.NO_CONTENT),
    ({'at_mode': 'no_token'}, {}, HTTPStatus.UNPROCESSABLE_ENTITY),
    ({'rt_mode': 'no_token'}, {}, HTTPStatus.UNPROCESSABLE_ENTITY),
    ({'at_mode': 'empty_token'}, {}, HTTPStatus.UNAUTHORIZED),
    ({'rt_mode': 'empty_token'}, {}, HTTPStatus.UNAUTHORIZED),
    ({}, {'secret_key': 'someincorrectsecretkey'}, HTTPStatus.UNAUTHORIZED),
    ({}, {'access_token_expire': -15}, HTTPStatus.UNAUTHORIZED),
    ({}, {'refresh_token_expire': -15}, HTTPStatus.UNAUTHORIZED),
])
async def test_logout_endpoint_access(
        prepare_jwt_tokens,
        prepare_cookies,
        cookies_params,
        tokens_params,
        api_make_post_request,
        expected_status):
    """
    Test for /api/v1/logout endpoint.
    Checking endpoint behaviour when received incorrect request.
    """

    access_token, refresh_token = await prepare_jwt_tokens(tokens_params)
    cookies = await prepare_cookies(access_token, refresh_token, **cookies_params)

    status, _, _ = await api_make_post_request(
        query_data={},
        endpoint='/api/v1/logout',
        headers=cookies
        )

    assert status == expected_status


@pytest.mark.parametrize('cookies_params, tokens_params, expected_status', [
    ({}, {}, HTTPStatus.UNAUTHORIZED),  # Here we expect to get 401 since refresh_token is absent in redis.
    ({'rt_mode': 'no_token'}, {}, HTTPStatus.UNPROCESSABLE_ENTITY),
    ({'rt_mode': 'empty_token'}, {}, HTTPStatus.UNAUTHORIZED),
    ({}, {'secret_key': 'someincorrectsecretkey'}, HTTPStatus.UNAUTHORIZED),
    ({}, {'refresh_token_expire': -15}, HTTPStatus.UNAUTHORIZED),
])
async def test_token_refresh_endpoint_access(
        prepare_jwt_tokens,
        prepare_cookies,
        cookies_params,
        tokens_params,
        api_make_post_request,
        expected_status):
    """
    Test for /api/v1/token-refresh endpoint.
    Checking endpoint behaviour when received incorrect request.
    """

    access_token, refresh_token = await prepare_jwt_tokens(tokens_params)
    cookies = await prepare_cookies(access_token, refresh_token, **cookies_params)

    status, _, _ = await api_make_post_request(
        query_data={},
        endpoint='/api/v1/token-refresh',
        headers=cookies
        )

    assert status == expected_status
