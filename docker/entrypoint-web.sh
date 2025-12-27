#!/bin/sh
set -e

python /app/src/manage.py migrate --noinput
python /app/src/manage.py collectstatic --noinput

exec uvicorn config.asgi:application --app-dir /app/src --host 0.0.0.0 --port 8000
