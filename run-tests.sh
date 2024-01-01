#!/bin/bash

cd fires-api
export FLASK_APP=./fires-api/run.py
conda run -n api python -m unittest tests.test_api