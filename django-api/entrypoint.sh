#!/bin/bash

cd api

python manage.py makemigrations

python manage.py migrate

python manage.py shell < populate_database.py

# This now is managed in the Dockerfile
# gunicorn -c gunicorn_config.py api.wsgi 
