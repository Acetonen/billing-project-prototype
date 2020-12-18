#!/bin/bash

set -e


case "$1" in
  gunicorn)
    python manage.py migrate --no-input
    python manage.py collectstatic --no-input --clear
    ;;
esac

exec "$@"
