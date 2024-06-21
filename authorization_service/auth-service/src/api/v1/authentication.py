from urllib.parse import urljoin
import logging
from typing import Annotated, Dict
import httpx


from fastapi import (APIRouter, Cookie, Depends, HTTPException, Request,
                     Response, status, Body)
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.postgres import get_pg_session
from src.models.db_entity import User
from src.schema.cookie import AccessTokenCookie, RefreshTokenCookie
from src.schema.model import AccessTokenData, UserLoginReq
from src.services.authentication import (AuthenticationService,
                                         get_authentication_service)
from src.services.base import BaseService, get_base_service
from src.services.jwt_token import JWTService, get_jwt_service
from src.core.api_settings import settings

router = APIRouter()


async def check_access_token(
        input_token: str = Cookie(alias=AccessTokenCookie.name),
        jwt_service: JWTService = Depends(get_jwt_service)) -> dict:
    """
    Function to check access jwt token from the Cookie.
    """
    if not input_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='unauthorised')

    result = await jwt_service.verify_token(token=input_token)

    if not result:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='unauthorised')

    return result


async def get_user(
        db: Annotated[AsyncSession, Depends(get_pg_session)],
        base_service: Annotated[BaseService, Depends(get_base_service)],
        access_token_dict: Annotated[Dict, Depends(check_access_token)]
        ) -> User:
    """
    Checks if user_id, received in JWT token exists in DB.
    Depends on func 'check_access_token'.
    Returns User DB model.
    """

    access_token = AccessTokenData(**access_token_dict)

    db_user = await base_service.get_user_by_uuid(db, user_id=access_token.user_id)

    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return db_user


async def get_current_active_user(user: Annotated[User, Depends(get_user)]) -> User:
    """
    Checks if received from DB user is active.
    Depends on func 'get_user'.
    """
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return user


async def get_superuser(user: Annotated[User, Depends(get_current_active_user)]) -> User:
    """
    Checks if received from DB user is superuser.
    Depends on func 'get_current_active_user'.
    """
    if not user.is_superuser:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return user


async def check_refresh_token(
        input_token: str = Cookie(alias=RefreshTokenCookie.name),
        jwt_service: JWTService = Depends(get_jwt_service)) -> dict:
    """
    Function to check access jwt token from the Cookie
    """
    if not input_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='unauthorised')

    result = await jwt_service.verify_token(token=input_token)

    if not result:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='unauthorised')

    return result


@router.post('/login', status_code=status.HTTP_200_OK)
async def login_user_for_access_token_cookie(
    request: Request,
    response: Response,
    form_data: Annotated[UserLoginReq, Body()],
    db: AsyncSession = Depends(get_pg_session),
    base_service: BaseService = Depends(get_base_service),
    authentication_service: AuthenticationService = Depends(get_authentication_service)
):
    """
    User login endpoint
    """
    try:
        user = await authentication_service.authenticate_user(db, form_data.email, form_data.password)
    except Exception as excp:
        logging.error('Unable to get user %s. The following error occured: %s', form_data.email, excp)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='internal server error')

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='wrong credentials')

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='user is inactive')

    try:
        user_roles_list = await base_service.get_user_roles(db, user.id)
        user_roles = [jsonable_encoder(role) for role in user_roles_list]

    except Exception as excp:
        logging.error('Unable to get roles for user %s. The following error occured: %s', form_data.email, excp)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='internal server error')

    access_token, refresh_token = await authentication_service.get_tokens(user_id=str(user.id), user_roles=user_roles)

    # In production, when you have https certificate, add secure=True to the methods below.
    response.set_cookie(key=AccessTokenCookie.name, value=access_token, httponly=True)
    response.set_cookie(key=RefreshTokenCookie.name, value=refresh_token, httponly=True)

    try:
        await authentication_service.save_login_history(
            db,
            user_id=str(user.id),
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent'),
            location=request.headers.get('location')
        )
    except Exception as excp:
        logging.error('DB. Unable to save user login history: %s', excp)

    response.headers["Authorization"] = f"Bearer {access_token}"
    # callback_url = "/api/v1/draft_content"
    # full_callback = urljoin(str(request.base_url), callback_url)
    # return RedirectResponse(url=full_callback, status_code=302)


@router.get('/produce_tokens', status_code=status.HTTP_200_OK)
async def produce_tokens(
    request: Request,
    response: Response,
    code: str,
    state: str,
    db: AsyncSession = Depends(get_pg_session),
    authentication_service: AuthenticationService = Depends(get_authentication_service)
):
    external_auth_service_url = "https://oauth.yandex.ru/token"
    data = {
        "client_id": settings.yauth_client_id,
        "grant_type": "authorization_code",
        "code": code,
        "client_secret": settings.yauth_secret_key,
    }
    headers = {
        "Content-type": "application/x-www-form-urlencoded"
    }

    async with httpx.AsyncClient() as client:
        auth_response = await client.post(external_auth_service_url, data=data, headers=headers)
        auth_response_json = auth_response.json()
        external_access_token = auth_response_json["access_token"]
        external_refresh_token = auth_response_json["refresh_token"]
    
    external_get_user_info_service_url = "https://login.yandex.ru/info"
    headers = {
        "Authorization": "OAuth " + external_access_token
    }

    async with httpx.AsyncClient() as client:   
        auth_response = await client.get(external_get_user_info_service_url, headers=headers)
        auth_response_json = auth_response.json()
        user_id = auth_response_json["default_email"]
        user_roles = []

    access_token, refresh_token = await authentication_service.get_tokens(user_id=str(user_id), user_roles=user_roles)

    # In production, when you have https certificate, add secure=True to the methods below.
    response.set_cookie(key=AccessTokenCookie.name, value=access_token, httponly=True)
    response.set_cookie(key=RefreshTokenCookie.name, value=refresh_token, httponly=True)

    try:
        await authentication_service.save_login_history(
            db,
            user_id=str(user_id),
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent'),
            location=request.headers.get('location')
        )
    except Exception as excp:
        logging.error('DB. Unable to save user login history: %s', excp)

    response.headers["Authorization"] = f"Bearer {access_token}"

    return (user_id, user_roles)


@router.get('/login_external', status_code=status.HTTP_200_OK)
async def login_user_external_for_access_token_cookie(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_pg_session)
):
    """
    External user login endpoint
    """

    external_auth_service_url = "https://oauth.yandex.ru/authorize"
    redirect_uri = urljoin(str(request.base_url), "/api/v1/produce_tokens")
        
    params = {
        "response_type": "code",
        "client_id": settings.yauth_client_id,
        "redirect_uri": redirect_uri,
        "scope": "login:email",
        "state": "some_random_text"
    }

    async with httpx.AsyncClient() as client:
        auth_response = await client.get(external_auth_service_url, params=params)
        return (auth_response.request.method, str(auth_response.request.url))

@router.post('/logout', status_code=status.HTTP_204_NO_CONTENT)
async def logout_user(
    response: Response,
    access_token: dict = Depends(check_access_token),
    token_input_dict: dict = Depends(check_refresh_token),
    authentication_service: AuthenticationService = Depends(get_authentication_service)
):
    """
    User logout endpoint
    """

    try:
        await authentication_service.logout_user(token_input_dict)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='internal server error')

    response.delete_cookie(key=AccessTokenCookie.name)
    response.delete_cookie(key=RefreshTokenCookie.name)

    return


@router.post('/token-refresh', status_code=status.HTTP_200_OK)
async def refresh_user_tokens_cookie_pair(
    response: Response,
    token_input_dict: dict = Depends(check_refresh_token),
    authentication_service: AuthenticationService = Depends(get_authentication_service)
):
    """
    User jwt token pair refresh endpoint
    """

    access_token, refresh_token = await authentication_service.refresh_tokens(token_input_dict)

    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='unauthorised')

    response.set_cookie(key=AccessTokenCookie.name, value=access_token, httponly=True)
    response.set_cookie(key=RefreshTokenCookie.name, value=refresh_token, httponly=True)

    return
