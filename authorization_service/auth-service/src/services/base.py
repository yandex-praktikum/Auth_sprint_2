from functools import lru_cache
from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy import desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import delete, insert, select, update

from src.models.db_entity import LoginHistory, Role, User, UserRole
from src.schema.model import (ResetCredentialsResp,
                              ResetPasswordResp, UserLoginHistory, UserRoles)


class BaseService:

    @staticmethod
    async def get_user_by_uuid(db: AsyncSession, user_id: str) -> [User | None]:
        """
        Searching for a user in the DB by uuid.
        Returns DB User representation.
        """
        statement = select(User).where(User.id == user_id)
        statement_result = await db.execute(statement=statement)
        user = statement_result.scalar_one_or_none()
        if not user:
            return None

        return user

    @staticmethod
    async def get_role_by_uuid(db: AsyncSession, role_id: str) -> [Role | None]:
        """
        Searching for a role in the DB by uuid.
        Returns DB Role representation.
        """
        statement = select(Role).where(Role.id == role_id)
        statement_result = await db.execute(statement=statement)
        role = statement_result.scalar_one_or_none()
        if not role:
            return None
        return role

    @staticmethod
    async def get_user_roles(db: AsyncSession, user_id: str) -> [List[UserRoles] | List]:
        """
        Searching for a user roles.
        Returns DB User representation.
        """
        statement = select(Role.id, Role.name).where(UserRole.user_id == user_id, UserRole.role_id == Role.id)
        statement_result = await db.execute(statement=statement)
        user_roles = statement_result.all()
        if not user_roles:
            return []

        # Возможно, я делаю это странным образом, но не нашел другого, чтобы конвертнуть
        # объект sqlalchemy.engine.row.Row возвращаемый statement_result.all()
        # в словарик.
        return [UserRoles(**jsonable_encoder(role._mapping)) for role in user_roles]

    @staticmethod
    async def check_email_exists(db: AsyncSession, email: str) -> bool:
        statement = select(User).where(User.email == email)
        statement_result = await db.execute(statement=statement)
        user = statement_result.scalar_one_or_none()
        return user is not None

    @staticmethod
    async def get_user_login_history(
            db: AsyncSession,
            user_id: str,
            limit: int = 50,
            offset: int = 0,
            order=desc
    ) -> [List[UserLoginHistory], int]:
        """
        Searching for a user login history in DB.
        Returns amount of results depending on received pagination parameters.
        """
        statement = (
            select(LoginHistory)
            .where(LoginHistory.user_id == user_id)
            .limit(limit)
            .offset(offset)
            .order_by(order(LoginHistory.timestamp))
        )
        statement_result = await db.execute(statement=statement)
        login_history = statement_result.scalars()
        if not login_history:
            return [], 0

        # Достаем из LoginHistory количество записей с LoginHistory.user_id == user_id
        count_query = select(func.count()).select_from(
            select(LoginHistory.user_id)
            .where(LoginHistory.user_id == user_id).subquery()
        )
        count_result = await db.execute(statement=count_query)
        count = count_result.scalar_one()

        # Получили из базы список из LoginHistory (схема БД)
        # берем каждый объект списка, декодируем в dict
        # dict распаковываем в UserLoginHistory - модель которую мы отдаем пользователю.
        return [UserLoginHistory(**jsonable_encoder(login)) for login in login_history], count

    @staticmethod
    async def update_user_email(db: AsyncSession, email: str, user_id: str) -> ResetCredentialsResp:
        statement = update(User).values(email=email).where(User.id == user_id)

        await db.execute(statement=statement)
        await db.commit()

        statement = select(User.email).where(User.id == user_id)
        statement_result = await db.execute(statement=statement)

        result_email = statement_result.scalar_one_or_none()

        return ResetCredentialsResp(user_id=str(user_id), field='email', value=result_email)

    @staticmethod
    async def update_user_password(db: AsyncSession, password: str, user_id: str) -> ResetPasswordResp:
        hashed_password = await User.get_password_hashed(password)
        statement = update(User).values(hashed_password=hashed_password).where(User.id == user_id)

        await db.execute(statement=statement)
        await db.commit()

        return ResetPasswordResp(user_id=str(user_id))

    async def assigne_role_to_user(self, db: AsyncSession, user_id: str, role_id: str) -> [List[UserRoles] | List]:
        """
        Function to assign a role to a user.
        """

        statement = insert(UserRole).values(user_id=user_id, role_id=role_id)

        await db.execute(statement=statement)
        await db.commit()

        result = await self.get_user_roles(db, user_id)

        return result

    async def remove_role_from_user(self, db: AsyncSession, user_id: str, role_id: str) -> [List[UserRoles] | List]:
        """
        Function to remove a role from a user.
        """

        statement = delete(UserRole).where(UserRole.user_id == user_id, UserRole.role_id == role_id)

        await db.execute(statement=statement)
        await db.commit()

        result = await self.get_user_roles(db, user_id)

        return result


@lru_cache()
def get_base_service() -> BaseService:
    return BaseService()
