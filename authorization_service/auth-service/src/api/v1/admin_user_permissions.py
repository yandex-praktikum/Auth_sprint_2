import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import UUID4
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.authentication import get_superuser
from src.db.postgres import get_pg_session
from src.models.db_entity import User
from src.schema.model import UserRolesResp
from src.services.base import BaseService, get_base_service

router = APIRouter()


@router.get('/admin/users/{user_id}/roles',
            status_code=status.HTTP_200_OK,
            response_model=UserRolesResp,
            description='Details regarding user permissions')
async def get_user_roles_list(
        user_id: UUID4,
        db: AsyncSession = Depends(get_pg_session),
        base_service: BaseService = Depends(get_base_service),
        su_user: User = Depends(get_superuser)):
    """
    Endpoint to get info regarding user roles.
    """
    user = await base_service.get_user_by_uuid(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='user not found')

    user_roles = await base_service.get_user_roles(db, user_id)

    return UserRolesResp(
        user_id=str(user.id),
        user_name=user.email,
        roles=user_roles
    )


@router.put('/admin/users/{user_id}/roles/{role_id}',
            status_code=status.HTTP_200_OK,
            response_model=UserRolesResp,
            description='Add a role to a user')
async def add_role_to_user(
        user_id: UUID4,
        role_id: UUID4,
        db: AsyncSession = Depends(get_pg_session),
        base_service: BaseService = Depends(get_base_service),
        su_user: User = Depends(get_superuser)):
    """
    Endpoint to add a role to a user.
    """
    user = await base_service.get_user_by_uuid(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='user not found')

    role = await base_service.get_role_by_uuid(db, role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='role does not exist')

    try:
        user_roles = await base_service.assigne_role_to_user(db, user.id, role.id)
    except IntegrityError:
        logging.error('Role id:%s already assigned to user id:%s', role.id, user.id)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='role alredy assingned')

    return UserRolesResp(
        user_id=str(user.id),
        user_name=user.email,
        roles=user_roles
    )


@router.delete('/admin/users/{user_id}/roles/{role_id}',
               status_code=status.HTTP_200_OK,
               response_model=UserRolesResp,
               description='Delete a role from a user')
async def delete_role_from_user(
        user_id: UUID4,
        role_id: UUID4,
        db: AsyncSession = Depends(get_pg_session),
        base_service: BaseService = Depends(get_base_service),
        su_user: User = Depends(get_superuser)):
    """
    Endpoint to remove a role from a user.
    """
    user = await base_service.get_user_by_uuid(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='user not found')

    role = await base_service.get_role_by_uuid(db, role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='role does not exist')

    user_roles = await base_service.remove_role_from_user(db, user.id, role.id)

    return UserRolesResp(
        user_id=str(user.id),
        user_name=user.email,
        roles=user_roles
    )
