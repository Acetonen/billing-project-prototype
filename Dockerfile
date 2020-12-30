
FROM python:3.8-slim

ENV PYTHONUNBUFFERED="1" \
    LC_ALL="C.UTF-8" \
    LANG="C.UTF-8"

ARG ENVIRONMENT

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /code/project/static

WORKDIR /code/

COPY poetry.lock ./
COPY pyproject.toml ./

RUN pip install -U pip poetry gunicorn \
    && poetry config virtualenvs.create false \
    && case $ENVIRONMENT in \
          dev*) poetry install;; \
          *)    poetry install --no-dev;; \
        esac \
    && pip uninstall -y poetry virtualenv virtualenv-clone \
    && rm -Rf /root/.cache/pip/


COPY . /code/

EXPOSE 8000

COPY docker/billing/*.sh /usr/bin/

RUN chmod +x /usr/bin/*.sh