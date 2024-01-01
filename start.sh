#!/bin/bash
source set-env-vars.sh

echo "Starting with DEV=$DEV..."

cd $API_SRC/fires-api
conda run -n api gunicorn --config gunicorn_config.py run:app --log-level=debug
