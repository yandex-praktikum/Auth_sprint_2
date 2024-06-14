from math import ceil
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import UUID4
from sqlalchemy import asc, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.authentication import (check_access_token,
                                       get_current_active_user)
from src.db.postgres import get_pg_session
from src.models.db_entity import User
from src.schema.model import (AccessTokenData, ResetCredentialsResp,
                              ResetPasswordResp, UserAccountInfoResp,
                              UserLoginHistoryResp, UserResetEmailReq,
                              UserResetPasswordReq)
from src.services.base import BaseService, get_base_service
from src.services.pagination import Pagination, SortEnum, pagination_params

router = APIRouter()


async def check_user_id(user_id: UUID4, access_token_dict: dict) -> None:
    """
    Checks if user_id from access token and path parameter match.
    """
    access_token = AccessTokenData(**access_token_dict)
    if access_token.user_id != str(user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)


@router.get('/account/{user_id}',
            status_code=status.HTTP_200_OK,
            response_model=UserAccountInfoResp,
            description='Details regarding user account')
async def get_user_account_info(
        user_id: UUID4,
        db_user: User = Depends(get_current_active_user),
        access_token_dic: dict = Depends(check_access_token)):
    """
    Returns details regarding user account.
    """

    await check_user_id(user_id, access_token_dic)

    # This is where pydantic magic shines:
    # DB model 'db_user' automatically transorms into
    # response_model=UserAccountInfoResp
    return db_user


@router.get('/account/{user_id}/history',
            status_code=status.HTTP_200_OK,
            response_model=UserLoginHistoryResp,
            description='Details regarding user login history')
async def get_user_login_history_info(
        pagination: Annotated[Pagination, Depends(pagination_params)],
        user_id: UUID4,
        db: AsyncSession = Depends(get_pg_session),
        base_service: BaseService = Depends(get_base_service),
        db_user: User = Depends(get_current_active_user),
        access_token_dic: dict = Depends(check_access_token)) -> UserLoginHistoryResp:
    """
    Returns paginated details regarding user login history.
    """
    await check_user_id(user_id, access_token_dic)

    offset = pagination.get_offset()
    order = desc if pagination.order == SortEnum.DESC else asc

    login_history, count = await base_service.get_user_login_history(
        db, db_user.id, limit=pagination.per_page, offset=offset, order=order)

    return UserLoginHistoryResp(
        page=pagination.page,
        total_pages=ceil(count / pagination.per_page),
        total_entries=count,
        per_page=pagination.per_page,
        data=login_history)


@router.put('/account/{user_id}/reset-email',
            status_code=status.HTTP_200_OK,
            response_model=ResetCredentialsResp,
            description='Reset email')
async def update_user_email(
        user_id: UUID4,
        user_data: UserResetEmailReq,
        db: AsyncSession = Depends(get_pg_session),
        base_service: BaseService = Depends(get_base_service),
        db_user: User = Depends(get_current_active_user),
        access_token_dic: dict = Depends(check_access_token)) -> ResetCredentialsResp:
    """
    Updates user email in the DB.
    """
    await check_user_id(user_id, access_token_dic)

    if await base_service.check_email_exists(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='user with received email already exists')

    result = await base_service.update_user_email(db, user_data.email, db_user.id)

    return result


@router.put('/account/{user_id}/reset-password',
            status_code=status.HTTP_200_OK,
            response_model=ResetPasswordResp,
            description='Reset password')
async def update_user_password(
        user_id: UUID4,
        user_data: UserResetPasswordReq,
        db: AsyncSession = Depends(get_pg_session),
        base_service: BaseService = Depends(get_base_service),
        db_user: User = Depends(get_current_active_user),
        access_token_dic: dict = Depends(check_access_token)) -> ResetPasswordResp:
    """
    Updates user password in the DB.
    """
    await check_user_id(user_id, access_token_dic)

    result = await base_service.update_user_password(db, user_data.password, db_user.id)

    return result
