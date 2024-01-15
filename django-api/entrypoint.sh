#!/bin/bash

cd api

python manage.py makemigrations

python manage.py migrate

python manage.py shell < populate_database.py

gunicorn -c gunicorn_config.py api.wsgi 