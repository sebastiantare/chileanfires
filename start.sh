#!/bin/bash

#export FLASK_APP=./fires-api/run.py
#conda run -n api flask run

cd fires-api
conda run -n api gunicorn --config gunicorn_config.py run:app
