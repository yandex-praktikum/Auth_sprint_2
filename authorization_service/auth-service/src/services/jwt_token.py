import logging
import uuid
from datetime import datetime, timedelta
from functools import lru_cache

from fastapi import Depends
from jose import JWTError, jwt

from src.core.api_settings import settings
from src.db.redis_db import get_redis
from src.schema.model import AccessTokenData, RefreshTokenData

from .helper import AsyncCache


class JWTService:
    def __init__(self, cache: AsyncCache):
        self.cache = cache

    secret_key = settings.jwt_secret_key
    algorithm = settings.jwt_algorithm
    access_token_expire = settings.jwt_at_expire_minutes
    refresh_token_expire = settings.jwt_rt_expire_minutes

    async def get_token_pair(self, user_id: str, session_id: str, roles: list = None, ) -> (str, str):
        """
        Returns a pair of jwt tokens
        """
        at_payload = await self.get_access_token_payload(user_id=user_id, roles=roles)
        rt_payload = await self.get_refresh_token_payload(user_id=user_id, roles=roles, session_id=session_id)
        access_token = await self.generate_token(at_payload, token_expire=self.access_token_expire)
        refresh_token = await self.generate_token(rt_payload, token_expire=self.refresh_token_expire)

        return access_token, refresh_token

    async def generate_token(self, token_payload: [AccessTokenData or RefreshTokenData], token_expire: int) -> str:
        """
        Generates a jwt token
        """

        token_payload.exp = datetime.utcnow() + timedelta(minutes=token_expire)
        to_encode = dict(token_payload)

        logging.info('Issued token: %s', to_encode)
        encoded_jwt = jwt.encode(to_encode, self.secret_key, self.algorithm)

        return encoded_jwt

    @staticmethod
    async def get_access_token_payload(user_id: str, roles: list = None) -> AccessTokenData:
        return AccessTokenData(
            user_id=user_id,
            iat=datetime.utcnow(),
            exp=datetime.utcnow(),
            roles=roles
        )

    @staticmethod
    async def get_refresh_token_payload(user_id: str, session_id: uuid, roles: list = None) -> RefreshTokenData:
        return RefreshTokenData(
            user_id=user_id,
            iat=datetime.utcnow(),
            exp=datetime.utcnow(),
            roles=roles,
            session_id=session_id
        )

    async def verify_token(self, token: str) -> dict:
        """
        Verifies received jwt token and returnd decoded payload
        """
        try:
            payload = jwt.decode(token, self.secret_key, self.algorithm)
            # We do not check token expiration time since it happens during
            # token decoding.

            user_id: str = payload.get('user_id')

            if user_id is None:
                logging.error('Unable to find "user_id" in the "access_token". Received payload: %s', payload)
                return {}

        except JWTError as excp:
            logging.error('The following error occured during access token decoding: %s', excp)
            return {}

        return payload


@lru_cache()
def get_jwt_service(cache: AsyncCache = Depends(get_redis),) -> JWTService:
    return JWTService(cache=cache)

