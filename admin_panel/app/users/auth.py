import http
import json
from logging import getLogger

import backoff
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from jose import jwt
from requests.exceptions import ConnectionError, HTTPError, Timeout

from .roles import Roles

User = get_user_model()
logger = getLogger(__name__)

BACKOFF_SETTINGS = {
    "wait_gen": backoff.expo,
    "exception": (ConnectionError, HTTPError, Timeout),
    "max_tries": 3,
    "jitter": backoff.full_jitter
}


class CustomBackend(BaseBackend):
    @backoff.on_exception(**BACKOFF_SETTINGS)
    def _send_request_to_login(self, payload: dict):
        url = settings.AUTH_API_LOGIN_URL
        response = requests.post(url, data=json.dumps(payload), timeout=settings.AUTH_API_TIMEOUT)
        return response

    @backoff.on_exception(**BACKOFF_SETTINGS)
    def _send_request_to_profile(self, user_id: str, cookies: dict):
        url = f"{settings.AUTH_API_USER_INFO_URL}/{user_id}"
        response = requests.get(url, cookies=cookies, timeout=settings.AUTH_API_TIMEOUT)
        return response

    def authenticate(self, request, username=None, password=None):
        payload = {"email": username, "password": password}
        try:
            response = self._send_request_to_login(payload)
        except Exception:
            return None
        if response.status_code != http.HTTPStatus.OK:
            return None

        access_token = response.cookies.get(settings.ACCESS_TOKEN_COOKIE_NAME)
        claims = jwt.get_unverified_claims(access_token)
        user, created = User.objects.get_or_create(sso_id=claims["user_id"])

        cookies = {settings.ACCESS_TOKEN_COOKIE_NAME: access_token}
        try:
            response = self._send_request_to_profile(user.sso_id, cookies)
        except Exception:
            return None
        if response.status_code != http.HTTPStatus.OK:
            return None

        data = response.json()
        try:
            user.email = data["email"]
            user.is_admin = Roles.ADMIN in claims["roles"]
            user.save()
        except Exception as exc:
            logger.error("Error while trying to save user: %s", exc)
            return None

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
