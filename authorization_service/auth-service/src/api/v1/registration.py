from fastapi import APIRouter, Depends, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.api_settings import settings
from src.db.postgres import get_pg_session
from src.schema.model import UserRegisteredResp, UserRegistrationReq
from src.services.registration import (RegistrationService,
                                       get_registration_service)

router = APIRouter()


@router.post(
    "/register",
    response_model=UserRegisteredResp, 
    status_code=(status.HTTP_201_CREATED, status.HTTP_429_TOO_MANY_REQUEST),
    dependencies=[Depends(RateLimiter(times=settings.register_rate_limit_times, seconds=settings.register_rate_limit_seconds))]
)
async def register_user(
    user_data: UserRegistrationReq,
    db: AsyncSession = Depends(get_pg_session),
    registration_service: RegistrationService = Depends(get_registration_service)
) -> UserRegisteredResp:
    """
    Регистрация пользователя
    """
    result = await registration_service.register_user(db=db, user_info=user_data)
    return result
