import logging
import uuid
from datetime import datetime, timedelta

from jose import jwt
from pydantic import BaseModel, field_validator

from src.tests.functional.settings import test_base_settings as settings


class AccessTokenData(BaseModel):
    user_id: str
    iat: datetime
    exp: datetime
    roles: list | None

    # The following two functions are necessary
    # to remove Timezone info from the timestamps
    # since pydantic automatically adds it.
    @field_validator('iat', mode='after')
    def iat_validate(cls, iat):
        return iat.replace(tzinfo=None)

    @field_validator('exp', mode='after')
    def exp_validate(cls, exp):
        return exp.replace(tzinfo=None)


class RefreshTokenData(BaseModel):
    user_id: str
    iat: datetime
    exp: datetime
    roles: list | None
    session_id: str

    @field_validator('iat', mode='after')
    def iat_validate(cls, iat):
        return iat.replace(tzinfo=None)

    @field_validator('exp', mode='after')
    def exp_validate(cls, exp):
        return exp.replace(tzinfo=None)


class JWTtokens:
    secret_key = settings.jwt_secret_key
    algorithm = 'HS256'
    access_token_expire = 30
    refresh_token_expire = 1440

    async def get_token_pair(
            self,
            user_id: str,
            session_id: str,
            roles: list = None,
            secret_key: str = None,
            access_token_expire: int = None,
            refresh_token_expire: int = None) -> (str, str):
        """
        Returns a pair of jwt tokens
        """

        at_payload = await self.get_access_token_payload(user_id=user_id, roles=roles)
        rt_payload = await self.get_refresh_token_payload(user_id=user_id, roles=roles, session_id=session_id)

        if not access_token_expire:
            access_token_expire = self.access_token_expire

        if not refresh_token_expire:
            refresh_token_expire = self.refresh_token_expire

        if not secret_key:
            secret_key = self.secret_key

        access_token = await self.generate_token(at_payload, token_expire=access_token_expire, secret_key=secret_key)
        refresh_token = await self.generate_token(rt_payload, token_expire=refresh_token_expire, secret_key=secret_key)

        return access_token, refresh_token

    async def generate_token(
            self,
            token_payload: [AccessTokenData or RefreshTokenData],
            token_expire: int,
            secret_key: str) -> str:
        """
        Generates a jwt token
        """

        token_payload.exp = datetime.utcnow() + timedelta(minutes=token_expire)

        to_encode = dict(token_payload)

        logging.info('Issued token: %s', to_encode)
        encoded_jwt = jwt.encode(to_encode, secret_key, self.algorithm)

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
