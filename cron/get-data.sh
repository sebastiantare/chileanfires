#!/bin/bash

if [ -z "$API_SRC" ]; then
    echo "Error: API_SRC is not set."
    exit 1
fi

# Check if the environment variable is set
if [ -z "$CONDA_SRC" ]; then
    echo "Error: CONDA_SRC is not set."
    exit 1
fi

source $CONDA_SRC/bin/activate api
cd $API_SRC/cron
$CONDA_SRC/envs/api/bin/python $API_SRC/cron/get-data.py