#!/usr/bin/env bash
set -e
python manage.py migrate
if [ "$DJANGO_SUPERUSER_USERNAME" ]
then
    python manage.py createsuperuser \
        --noinput \
        --username $DJANGO_SUPERUSER_USERNAME \
        --email $DJANGO_SUPERUSER_EMAIL || true
fi

# use exec to handle SIGINT to speed up the container shutdown process
if [ "$ENVIRONMENT" = "PROD" ]; then
    exec uwsgi --strict --ini /opt/app/uwsgi.ini
elif [ "$ENVIRONMENT" = "LOCAL" ]; then
    exec python manage.py runserver 0.0.0.0:8000
else
    echo You are required to specify the ENVIRONMENT
fi