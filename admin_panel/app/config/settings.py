from pathlib import Path

from split_settings.tools import include

BASE_DIR = Path(__file__).resolve().parent.parent

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

include(
    "components/auth.py",
    "components/database.py",
    "components/installed_apps.py",
    "components/internationalization.py",
    "components/logging.py",
    "components/middleware.py",
    "components/rest_framework.py",
    "components/security.py",
    "components/static.py",
)
