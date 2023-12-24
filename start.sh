#!/bin/bash

conda shell.bash activate api

export FLASK_APP=./fires-api/run.py

flask run
