#!/bin/bash

# Get the current username and groupname
USERNAME=$(whoami)
GROUPNAME=$(id -gn)
CONDA_ENV_NAME="api"

APP_PATH="$HOME/chileanfires/fires-api/cron"
GET_DATA="$APP_PATH/get-data.py"
MERGE_DATA="$APP_PATH/merge-data.py"

# Schedule cron jobs
(crontab -l 2>/dev/null; echo "*/10 * * * * "$HOME/miniconda3/envs/$CONDA_ENV_NAME/bin/python" $GET_DATA") | crontab -
(crontab -l 2>/dev/null; echo "*/10 * * * * "$HOME/miniconda3/envs/$CONDA_ENV_NAME/bin/python" $MERGE_DATA") | crontab -

# Set up scripts to run on boot (add to crontab)
@reboot $HOME/miniconda3/envs/$CONDA_ENV_NAME/bin/python $GET_DATA
@reboot $HOME/miniconda3/envs/$CONDA_ENV_NAME/bin/python $MERGE_DATA