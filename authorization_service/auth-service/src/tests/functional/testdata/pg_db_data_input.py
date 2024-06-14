import uuid
from typing import Iterable

import pytest
import pytest_asyncio


@pytest_asyncio.fixture(name='user_login_data')
def user_login_data():
    async def inner():
        """
        Finction to prepare data for inserting into users DB table.
        :return:
        """
        user_row = {
            'id': '8ab71a54-7b99-4322-a07e-0b2a0c40ff44',
            'email': 'admin@mail.com',
            'hashed_password': 'scrypt:32768:8:1$jnCGw8KZfrFUNu6l$e6df0e686ad689c5012b7c7e8f135c37b85fec84cc056c6b8ceaffdaf51454d4524cd69e18e9dc67a122cb5eacab6ab37f6f89437fe5d358b07dcad0b6033830',
            'is_active': True,
            'is_superuser': False,
            'is_verified': False,


        }

        return user_row

    return inner


@pytest_asyncio.fixture(name='su_user_data')
def su_user_data():
    async def inner():
        """
        Finction to prepare data for inserting into users DB table.
        :return:
        """
        user_row = {
            'id': '11b71a54-7b99-4322-a07e-0b2a0c40aa11',
            'email': 'su_user@mail.com',
            'hashed_password': 'scrypt:32768:8:1$jnCGw8KZfrFUNu6l$e6df0e686ad689c5012b7c7e8f135c37b85fec84cc056c6b8ceaffdaf51454d4524cd69e18e9dc67a122cb5eacab6ab37f6f89437fe5d358b07dcad0b6033830',
            'is_active': True,
            'is_superuser': True,
            'is_verified': False,

        }

        return user_row

    return inner
