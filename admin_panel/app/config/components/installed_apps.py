import os

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "movies.apps.MoviesConfig",
    "users.apps.UsersConfig",
]

if os.environ.get("DEBUG", False) == "True":
    INSTALLED_APPS += ["debug_toolbar"]
