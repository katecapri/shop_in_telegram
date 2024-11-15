#!/bin/bash

cd src || { echo "Directory 'src' not found."; exit 1; }

python manage.py migrate
python manage.py collectstatic --noinput
export DJANGO_SUPERUSER_EMAIL=admin@admin.com
export DJANGO_SUPERUSER_PASSWORD=admin
export DJANGO_SUPERUSER_USERNAME=admin
python manage.py createsuperuser --no-input

gunicorn --bind 0.0.0.0:8008 config.wsgi