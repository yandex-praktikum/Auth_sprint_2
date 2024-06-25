from fastapi.routing import APIRouter

from src.api.v1 import (admin_roles, admin_user_permissions, authentication,
                        personal_account, registration)

router = APIRouter()
router.include_router(registration.router, tags=['Registration'])
router.include_router(authentication.router, tags=['Authentication'])
router.include_router(personal_account.router, tags=['Personal account'])
router.include_router(admin_roles.router, tags=['Administrate roles'])
router.include_router(admin_user_permissions.router, tags=['Administrate user permissions'])
