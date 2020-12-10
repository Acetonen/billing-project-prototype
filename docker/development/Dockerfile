FROM python:3.8-slim

ENV PYTHONUNBUFFERED="1" \
    LC_ALL="C.UTF-8" \
    LANG="C.UTF-8"
RUN apt-get update && apt install -y curl
RUN apt install -y curl wget

WORKDIR /code/

COPY Pipfile* ./

RUN pip install -U pip pipenv gunicorn \
          && pipenv install --system \
          && pip uninstall -y pipenv virtualenv virtualenv-clone \
          && rm -Rf /root/.cache/pip/

RUN touch config.env \
 && ln -sf conf/config.env config.env

## Add the wait script to the image
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.5.0/wait /wait
RUN chmod +x /wait

EXPOSE 8000