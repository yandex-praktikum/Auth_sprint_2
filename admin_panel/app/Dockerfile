FROM python:3.11-slim 

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates openssl tzdata make git \
    gcc g++ openssh-client \
    llvm zip unzip wget \
    libxml2-dev libxml2-utils liblz4-dev libxslt-dev build-essential libpq-dev \
    libgeoip-dev libjpeg-dev liblzma-dev libncurses5-dev libncursesw5-dev \
    libffi-dev libssl-dev dnsutils liblzma-dev postgresql-client \
    libunwind-dev procps curl vis vim grep bash gettext\
    && rm -rf /var/lib/apt/lists/*


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /opt/app

RUN groupadd -r web && useradd -d /opt/app -r -g web web_user \
    && chown web_user:web -R /opt/app

COPY .meta/packages ./requirements.txt

RUN mkdir -p /opt/app/static/ \
     && mkdir -p /var/www/static/ \
     && mkdir -p /opt/app/media/ \
     && mkdir -p /var/www/media/ \
     && pip install --upgrade pip \
     && pip install -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput && python manage.py compilemessages -l en -l ru

EXPOSE 8000

USER web_user
ENTRYPOINT ["sh", "entrypoint.sh"]