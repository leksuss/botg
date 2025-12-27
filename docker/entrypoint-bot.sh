#!/bin/sh
set -e

python /app/src/manage.py migrate --noinput

exec python /app/src/manage.py runbot
