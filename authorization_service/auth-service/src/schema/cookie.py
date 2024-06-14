from dataclasses import dataclass


@dataclass(frozen=True)
class AccessTokenCookie:
    name = 'auth-app-access-key'
    value: str


@dataclass(frozen=True)
class RefreshTokenCookie:
    name = 'auth-app-refresh-key'
    value: str
