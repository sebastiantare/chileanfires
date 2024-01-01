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

source $API_SRC/miniconda3/bin/activate api
cd $API_SRC/chileanfires/cron
$CONDA_SRC/envs/api/bin/python $API_SRC/chileanfires/cron/get-data.py