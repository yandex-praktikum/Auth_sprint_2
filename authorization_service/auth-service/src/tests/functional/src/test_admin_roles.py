from http import HTTPStatus

import pytest

from src.models.db_entity import Permission, Role, RolePermission, User
from src.tests.functional.fixtures.client_fixtures import (
    api_make_get_request, api_post)
from src.tests.functional.testdata.jwt_tokens import JWTtokens
from src.tests.functional.testdata.pg_db_data_input import su_user_data

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


async def test_add_permission(
        pg_clear_tables_data,
        pg_insert_table_data,
        su_user_data,
        prepare_jwt_tokens,
        api_post):

    await pg_clear_tables_data()
    jwt = JWTtokens()

    try:
        data = await su_user_data()
        await pg_insert_table_data(table_name=User, data=data)
        access_token, refresh_token = await jwt.get_token_pair(
            user_id=data.get('id'),
            session_id='22bd63b2-3d33-45b7-991b-d2e37662426a'
        )
        status, body, _ = await api_post(
            body={'name': 'permission.1'},
            endpoint='/api/v1/admin/permissions',
            headers={'cookie': f'auth-app-access-key={access_token}'}
        )

        assert status == HTTPStatus.CREATED
    finally:
        await pg_clear_tables_data()


async def test_get_permissions(
        client_session,
        pg_insert_table_data,
        pg_clear_tables_data,
        api_make_get_request, su_user_data):

    await pg_clear_tables_data()
    jwt = JWTtokens()
    permission_name = "permission.ABC"

    try:
        data = await su_user_data()
        await pg_insert_table_data(table_name=User, data=data)
        await pg_insert_table_data(table_name=Permission, data={"name": permission_name})
        access_token, refresh_token = await jwt.get_token_pair(
            user_id=data.get('id'),
            session_id='22bd63b2-3d33-45b7-991b-d2e37662426a'
        )
        status, body = await api_make_get_request(
            endpoint='/api/v1/admin/permissions',
            headers={'cookie': f'auth-app-access-key={access_token}'}
        )

        assert status == HTTPStatus.OK
        assert body['data'][0]['name'] == permission_name
    finally:
        await pg_clear_tables_data()


async def test_add_role(
        pg_clear_tables_data,
        pg_insert_table_data,
        su_user_data,
        prepare_jwt_tokens,
        api_post):

    await pg_clear_tables_data()
    jwt = JWTtokens()

    try:
        data = await su_user_data()
        await pg_insert_table_data(table_name=User, data=data)
        access_token, refresh_token = await jwt.get_token_pair(
            user_id=data.get('id'),
            session_id='22bd63b2-3d33-45b7-991b-d2e37662426a'
        )
        status, _, _ = await api_post(
            body={'name': 'role.1'},
            endpoint='/api/v1/admin/roles',
            headers={'cookie': f'auth-app-access-key={access_token}'}
        )

        assert status == HTTPStatus.CREATED
    finally:
        await pg_clear_tables_data()


async def test_get_roles(
        client_session,
        pg_insert_table_data,
        pg_clear_tables_data,
        api_make_get_request, su_user_data):

    await pg_clear_tables_data()
    jwt = JWTtokens()
    role_name = 'role.ABC'

    try:
        data = await su_user_data()
        await pg_insert_table_data(table_name=User, data=data)
        await pg_insert_table_data(table_name=Role, data={"name": role_name})
        access_token, refresh_token = await jwt.get_token_pair(
            user_id=data.get('id'),
            session_id='22bd63b2-3d33-45b7-991b-d2e37662426a'
        )
        status, body = await api_make_get_request(
            endpoint='/api/v1/admin/roles',
            headers={'cookie': f'auth-app-access-key={access_token}'}
        )

        assert status == HTTPStatus.OK
        assert body['data'][0]['name'] == role_name
    finally:
        await pg_clear_tables_data()
