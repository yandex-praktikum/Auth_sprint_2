FROM python:3.12-bullseye

WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt

RUN  mkdir -p /opt/app/static/ \
     && mkdir -p /opt/app/media/ \
     && apt update \
     && pip install --upgrade pip \
     && pip install -r requirements.txt \
     && apt install -y vim

COPY ./src .

ENTRYPOINT gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind "$FASTAPI_HOST":"$FASTAPI_PORT"