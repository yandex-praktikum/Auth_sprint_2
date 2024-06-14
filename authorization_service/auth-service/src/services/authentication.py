import logging
import uuid
from datetime import datetime
from functools import lru_cache

from fastapi import Depends
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from src.db.redis_db import get_redis
from src.models.db_entity import LoginHistory, User
from src.schema.model import RefreshTokenData
from src.services.jwt_token import JWTService, get_jwt_service
from src.services.redis import RedisService, get_redis_service

from .helper import AsyncCache


class AuthenticationService:
    def __init__(self, cache: AsyncCache, redis_service: RedisService, jwt_service: JWTService):
        self.cache = cache
        self.redis_service: RedisService = redis_service
        self.jwt_service: JWTService = jwt_service

    @staticmethod
    async def authenticate_user(db: AsyncSession, email: str, password: str) -> [User | None]:
        """
        Searching for a user in the DB
        """
        statement = select(User).where(User.email == email)
        statement_result = await db.execute(statement=statement)
        user = statement_result.scalar_one_or_none()
        if not user:
            return None
        if not await user.check_password(password):
            return None
        return user

    @staticmethod
    async def save_login_history(db: AsyncSession, user_id: str, ip_address: str, location: str, user_agent: str) -> None:
        """
        Save user login info in the DB
        """
        statement = (
            insert(LoginHistory).
            values(
                user_id=user_id,
                timestamp=datetime.utcnow(),
                ip_address=ip_address,
                location=location,
                user_agent=user_agent)
        )
        await db.execute(statement=statement)
        await db.commit()

        return

    @staticmethod
    async def generate_session_id() -> str:
        return str(uuid.uuid4())

    async def logout_user(self, token_input_dict: dict) -> None:

        logging.debug('Refresh token: %s', token_input_dict)

        token = RefreshTokenData(**token_input_dict)

        await self.redis_service.del_refresh_token(user_id=token.user_id, session_id=token.session_id)

        return

    async def get_tokens(self, user_id: str, user_roles: list | None) -> (str, str):

        session_id = await self.generate_session_id()
        access_token, refresh_token = await self.jwt_service.get_token_pair(
            user_id=user_id,
            session_id=session_id,
            roles=user_roles)

        try:
            await self.redis_service.save_refresh_token(
                user_id=user_id,
                session_id=session_id,
                expire_time_sec=JWTService.refresh_token_expire * 60
            )
        except Exception as excp:
            logging.error('Unable to save refresh_token %s:%s to Redis. %s', user_id, session_id, excp)

        return access_token, refresh_token

    async def refresh_tokens(self, rt_input_dict: dict) -> (str, str):

        logging.debug('Received "refresh_token": %s', rt_input_dict)

        token = RefreshTokenData(**rt_input_dict)
        redis_key = await self.redis_service.get_redis_key(user_id=token.user_id, session_id=token.session_id)

        redis_refresh_token = await self.redis_service.redis.get(name=redis_key)
        # For now, we use refresh token white list.
        if not redis_refresh_token:
            return None, None

        await self.redis_service.redis.expire(name=redis_key, time=0)

        access_token, refresh_token = await self.get_tokens(user_id=token.user_id, user_roles=token.roles)

        return access_token, refresh_token


@lru_cache()
def get_authentication_service(
        cache: AsyncCache = Depends(get_redis),
        redis_service: RedisService = Depends(get_redis_service),
        jwt_service: JWTService = Depends(get_jwt_service)
) -> AuthenticationService:
    return AuthenticationService(cache, redis_service, jwt_service)
