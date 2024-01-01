#!/bin/bash

# Env vars
source set-env-vars.sh

# This will show the limiter options for the flask API
export FLASK_APP=./fires-api/run.py
flask limiter limits