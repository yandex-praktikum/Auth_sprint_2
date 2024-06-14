from functools import lru_cache
from typing import Generic, List, Type, TypeVar, Union

from fastapi import Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import and_, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import delete, insert, select

from src.db.redis_db import get_redis
from src.models.db_entity import Permission, Role, RolePermission
from src.schema.model import (PermissionCreateReq, PermissionCreateResp,
                              PermissionInfoResp, PermissionsListResp,
                              RoleCreateReq, RoleCreateResp, RoleInfoResp,
                              RolesListResp)

from .helper import AsyncCache

T = TypeVar('T')


class AdminRolesService(Generic[T]):
    def __init__(self):
        ...

    async def create_permission(self, db: AsyncSession, permission_data: PermissionCreateReq) -> PermissionInfoResp:
        permission_exists = await self._check_entity_exists(entity_type=Permission, db=db, name=permission_data.name)
        if permission_exists:
             raise HTTPException(
                 status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                 detail="Пермишн уже существует"
             )
        result = await self.add_permission(db, permission_data)
        return result

    async def add_permission(
        self, 
        db: AsyncSession,
        permission_data: PermissionCreateReq
    ) -> PermissionCreateResp:
        permission = Permission(name = permission_data.name)
        db.add(permission)
        await db.commit()
        await db.refresh(permission)
        return PermissionCreateResp(
            permission_id=str(permission.id),
            name=permission.name
        )

    async def get_all_permissions(self, db: AsyncSession) -> PermissionsListResp:
        statement = select(Permission)
        statement_result = await db.execute(statement=statement)
        permissions = statement_result.scalars()
        return PermissionsListResp(
            data=[
                PermissionInfoResp(
                    permission_id=str(permission.id),
                    name=permission.name
                ) for permission in permissions
            ]
        )

    async def create_role(self, db: AsyncSession, role_data: RoleCreateReq) -> RoleInfoResp:
        role_exists = await self._check_entity_exists(entity_type=Role, db=db, name=role_data.name)
        if role_exists:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Роль уже существует"
             )
        result = await self.add_role(db, role_data)
        return result

    @staticmethod
    async def add_role(db: AsyncSession, role_data: RoleCreateReq) -> RoleCreateResp:

        role = Role(name=role_data.name)
        db.add(role)
        await db.commit()
        await db.refresh(role)
        return RoleCreateResp(
            role_id=str(role.id),
            name=role.name,
            permissions=[]
        )

    async def get_all_roles(self, db: AsyncSession) -> RolesListResp:
        statement = select(Role)
        statement_result = await db.execute(statement=statement)
        roles = statement_result.scalars()
        roles_data = []
        for role in roles:
            statement_role_permission = select(RolePermission).where(RolePermission.role_id == role.id)
            statement_role_permission_result = await db.execute(statement_role_permission)
            role_permissions = statement_role_permission_result.scalars()

            roles_data.append(
                RoleInfoResp(
                    role_id = str(role.id),
                    name=role.name,
                    permissions=[
                        PermissionInfoResp(
                            permission_id=str(rp.permission_id),
                            name=(
                                await self._get_entity_by_id(entity_type=Permission, db=db, entity_id=rp.permission_id)
                            ).name
                        ) for rp in role_permissions
                    ]

                )
            )
        return RolesListResp(data=roles_data)

    async def get_permissions_by_role(self, db: AsyncSession, role_name: str):
        role = await self._get_entity_by_name(entity_type=Role, db=db, entity_name=role_name)
        statement_get_role_permissions = select(RolePermission).where(RolePermission.role_id == role.id)
        statement_get_role_permissions_result = await db.execute(statement_get_role_permissions)
        permission_roles = statement_get_role_permissions_result.scalars()
        p_id_list = [permission_role.permission_id for permission_role in permission_roles]
        statement_get_permissions = select(Permission).where(Permission.id.in_(p_id_list))
        statement_get_permissions_result = await db.execute(statement_get_permissions)
        permissions = statement_get_permissions_result.scalars()
        permissions_data = []
        for permission in permissions:
            permissions_data.append(
                PermissionInfoResp(
                    permission_id=str(permission.id),
                    name=permission.name
                )
            )
        return PermissionsListResp(data=permissions_data)

    async def update_role_permissions(
        self, db: AsyncSession, role_name: str, permissions=List[str]
    ) -> RoleInfoResp:
        role = await self._get_entity_by_name(entity_type=Role, db=db, entity_name=role_name)
        statement_get_permissions = await db.execute(select(Permission).where(Permission.name.in_(permissions)))
        permission_objects = statement_get_permissions.scalars().all()
        await db.execute(delete(RolePermission).where(RolePermission.role_id == role.id))
        role_permission_objects = [
            RolePermission(
                role_id=role.id, 
                permission_id=permission.id
            ) for permission in permission_objects
        ]
        db.add_all(role_permission_objects)
        await db.commit()
        await db.refresh(role)
        return RoleInfoResp(
            role_id=str(role.id),
            name=role.name,
            permissions=[
                PermissionInfoResp(
                    permission_id=str(permission.id),
                    name=permission.name
                ) for permission in permission_objects
            ]
        )

    async def delete_permission(self, permission_name, db: AsyncSession) -> None:
        permission = await self._get_entity_by_name(
            entity_type=Permission, 
            db=db, 
            entity_name=permission_name
        )
        rp_objects = (
            await db.execute(
                select(RolePermission).where(RolePermission.permission_id == permission.id)
            )
        ).scalars()
        for rp in rp_objects:
            await db.delete(rp)
        await db.commit()
        await db.delete(permission)
        await db.commit()

    async def delete_role(self, role_name, db: AsyncSession) -> None:
        role = await self._get_entity_by_name(
            entity_type=Role, 
            db=db, 
            entity_name=role_name
        )
        rp_objects = (
            await db.execute(
                select(RolePermission).where(RolePermission.role_id == role.id)
            )
        ).scalars()
        for rp in rp_objects:
            await db.delete(rp)
        await db.commit()
        await db.delete(role)
        await db.commit()

    async def _check_entity_exists(self, entity_type: Type[T], db: AsyncSession, name: str) -> bool:
        statement = select(entity_type).where(entity_type.name == name)
        statement_result = await db.execute(statement=statement)
        entity = statement_result.scalar_one_or_none()
        return entity is not None

    async def _get_entity_by_name(
        self,
        entity_type: Type[T],
        db: AsyncSession, 
        entity_name: str
    ) -> T:
        statement = select(entity_type).where(entity_type.name == entity_name)
        statement_result = await db.execute(statement)
        entity = statement_result.scalar_one_or_none()
        if entity is None:
            raise HTTPException(
                 status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                 detail=f"Объект {entity_type.__name__} не найден."
             )
        return entity
    
    async def _get_entity_by_id(self, entity_type: Type[T], db: AsyncSession, entity_id: str) -> BaseModel:
        statement = select(entity_type).where(entity_type.id == entity_id)
        statement_result = await db.execute(statement)
        entity = statement_result.scalar_one()
        return entity


@lru_cache()
def get_admin_roles_service() -> AdminRolesService:
    return AdminRolesService[Union[Role, Permission]]()
