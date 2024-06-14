from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.postgres import get_pg_session
from src.schema.model import UserRegisteredResp, UserRegistrationReq
from src.services.registration import (RegistrationService,
                                       get_registration_service)

router = APIRouter()


@router.post(
    "/register",
    response_model=UserRegisteredResp, 
    status_code=status.HTTP_201_CREATED
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
