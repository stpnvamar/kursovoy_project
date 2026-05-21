#!/bin/sh
set -e

echo "==> Running makemigrations..."
python manage.py makemigrations users tasks --noinput

echo "==> Running migrate..."
python manage.py migrate --noinput

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

echo "==> Starting Gunicorn..."
exec gunicorn taskmanager_backend.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120
