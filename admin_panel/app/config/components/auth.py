import os

AUTH_USER_MODEL = "users.User"
AUTHENTICATION_BACKENDS = ["users.auth.CustomBackend"]
AUTH_API_LOGIN_URL = os.environ.get("AUTH_API_LOGIN_URL")
ACCESS_TOKEN_COOKIE_NAME = "auth-app-access-key"  # noqa: S105
REFRESH_TOKEN_COOKIE_NAME = "auth-app-refresh-key"  # noqa: S105
AUTH_API_USER_INFO_URL = os.environ.get("AUTH_API_USER_INFO_URL")
AUTH_API_TIMEOUT = 2
