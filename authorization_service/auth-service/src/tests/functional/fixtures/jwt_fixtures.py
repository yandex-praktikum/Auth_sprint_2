from datetime import UTC, datetime, timedelta

import pytest_asyncio
from jose import JWTError, jwt
from redis.asyncio import Redis

from src.schema.model import AccessTokenData
from src.tests.functional.settings import test_base_settings
from src.tests.functional.testdata.jwt_tokens import JWTtokens


@pytest_asyncio.fixture(name='get_access_token')
async def get_access_token():
    async def _get_access_token(user_id: str) -> str:
        at_payload = AccessTokenData(
            user_id=user_id,
            iat=datetime.now(UTC),
            exp=datetime.now(UTC),
            roles=[]
        )
        at_payload.exp = datetime.now(UTC) + timedelta(minutes=test_base_settings.jwt_at_expire_minutes)
        to_encode = dict(at_payload)
        encoded_jwt = jwt.encode(to_encode, test_base_settings.jwt_secret_key, test_base_settings.jwt_algorithm)
        return encoded_jwt

    return _get_access_token


@pytest_asyncio.fixture(name='prepare_jwt_tokens')
def prepare_jwt_tokens():
    async def inner(token_params: dict):
        jwt_tokens = JWTtokens()
        access_token, refresh_token = await jwt_tokens.get_token_pair(
            user_id='8ab71a54-7b99-4322-a07e-0b2a0c40ff44',
            session_id='22bd63b2-3d33-45b7-991b-d2e37662426a',
            **token_params
        )

        return access_token, refresh_token

    return inner
