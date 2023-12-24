#!/bin/bash

# For start on boot, use serve.sh instead.

cd fires-api
conda run -n api gunicorn --config gunicorn_config.py run:app
