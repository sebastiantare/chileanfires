#!/bin/bash

conda init bash

source ~/.bashrc

conda activate api

# Set the path to your Parquet file
export PARQUET_FILE_PATH="./db/fires.parquet"

# Run the Flask app
export FLASK_APP=./api/run.py

flask run
