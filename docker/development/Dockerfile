FROM debian:9-slim

ENV LIBRARY_PATH="/lib:/usr/lib" \
    PYTHONUNBUFFERED="1" \
    PYTHONDONTWRITEBYTECODE="1" \
    DOCKER="1" \
    DEBIAN_FRONTEND="noninteractive" \
    LC_ALL="C.UTF-8" \
    LANG="C.UTF-8" \
    PYCURL_SSL_LIBRARY=openssl

RUN apt-get update && \
    apt-get install --no-install-recommends -y graphviz vim-tiny wget ca-certificates git patch \
            g++ make libgraphviz-dev zlib1g-dev libssl-dev libreadline-dev libbz2-dev libsqlite3-dev libpq-dev \
            autoconf libffi-dev procps libcurl4-openssl-dev openssl gettext && \
    rm -rf /var/lib/apt/lists/*

ENV PYENV_ROOT="/usr/local/pyenv" \
    LIBRARY_PATH="/lib:/usr/lib" \
    PYTHONUNBUFFERED="1" \
    DOCKER="1" \
    DEBIAN_FRONTEND="noninteractive" \
    PYTHON3_VERSION="3.8.0"

ENV PATH=":/usr/local/pyenv/shims:/usr/local/pyenv/versions/$PYTHON3_VERSION/bin:/usr/local/pyenv/bin/:$PATH"

# install Python (via pyenv) and dependencies
RUN mkdir -p /usr/local/pyenv/ && \
    wget -q https://github.com/pyenv/pyenv/archive/v1.2.21.tar.gz -O - | \
        tar -xzf - --strip-components=1 -C /usr/local/pyenv/ && \
    pyenv install $PYTHON3_VERSION && \
    pyenv global $PYTHON3_VERSION && \
    pip install -U pipenv pip && \
    rm -Rf /root/.cache/pip/


# Other stuff
RUN wget https://raw.githubusercontent.com/marcelor/fabric-bash-autocompletion/master/fab -O /etc/bash_completion.d/fab && \
    wget https://github.com/django/django/raw/master/extras/django_bash_completion -O /etc/bash_completion.d/django && \
    echo . /etc/bash_completion.d/fab >> /etc/bash.bashrc && \
    echo . /etc/bash_completion.d/django >> /etc/bash.bashrc

WORKDIR /code/

COPY Pipfile* ./

RUN pipenv install --system --dev && \
    rm -Rf /root/.cache/pip/

RUN touch config.env \
 && ln -sf conf/config.env config.env

## Add the wait script to the image
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.5.0/wait /wait
RUN chmod +x /wait

EXPOSE 8000
EXPOSE 6900
