import datetime
import uuid
from typing import List

from pydantic import UUID4, BaseModel, EmailStr, Field, field_validator


class UserRegistrationReq(BaseModel):
    email: EmailStr
    password: str


class UserResetEmailReq(BaseModel):
    email: EmailStr


class UserResetPasswordReq(BaseModel):
    password: str


class UserLoginReq(BaseModel):
    email: EmailStr
    password: str


# TODO: review schema, use version in auth-service/docs/openapi_auth_api_doc.yaml
class UserRegisteredResp(BaseModel):
    result: str
    user_id: str
    email: str
    is_active: bool


class ResetCredentialsResp(BaseModel):
    result: str = 'success'
    user_id: str
    field: str
    value: str | None = None


class ResetPasswordResp(BaseModel):
    result: str = 'success'
    user_id: str
    field: str = 'password'


class UserAccountInfoResp(BaseModel):
    id: UUID4
    email: str


class UserLoginHistory(BaseModel):
    timestamp: datetime.datetime | None = None
    ip_address: str | None = None
    location: str | None = None
    user_agent: str | None = None


class UserLoginHistoryResp(BaseModel):
    page: int
    total_pages: int
    total_entries: int
    per_page: int
    data: List[UserLoginHistory]


class UserRoles(BaseModel):
    id: UUID4
    name: str


class UserRolesResp(BaseModel):
    user_id: str
    user_name: str
    roles: List[UserRoles] | List


class UserPermissionsResp(BaseModel):
    result: str
    data: str
    user_id: str
    roles: str


class UserAddRoleResp(BaseModel):
    result: str
    user_id: str
    roles: List[dict]


class PermissionInfoResp(BaseModel):
    permission_id: str
    name: str


class PermissionsListResp(BaseModel):
    data: List[PermissionInfoResp]


class PermissionCreateResp(PermissionInfoResp):
    ...


class PermissionCreateReq(BaseModel):
    name: str

      
class RoleInfoResp(BaseModel):
    role_id: str
    name: str
    permissions: List[PermissionInfoResp]


class AccessTokenData(BaseModel):
    user_id: str
    iat: datetime.datetime
    exp: datetime.datetime
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
    iat: datetime.datetime
    exp: datetime.datetime
    roles: list | None
    session_id: str

    @field_validator('iat', mode='after')
    def iat_validate(cls, iat):
        return iat.replace(tzinfo=None)

    @field_validator('exp', mode='after')
    def exp_validate(cls, exp):
        return exp.replace(tzinfo=None)


class RolesListResp(BaseModel):
    data: List[RoleInfoResp]


class RoleCreateResp(RoleInfoResp):
    ...


class RoleCreateReq(BaseModel):
    name: str
