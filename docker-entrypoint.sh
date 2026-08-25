#!/bin/sh
set -e

python manage.py migrate --noinput

if [ "$NOVAERP_SEED_DEMO" = "True" ]; then
    python manage.py seed_demo || true
fi

exec "$@"
