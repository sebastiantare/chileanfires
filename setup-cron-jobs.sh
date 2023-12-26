#!/bin/bash

USERNAME=$(whoami)
GROUPNAME=$(id -gn)
CONDA_ENV_NAME="api"

APP_PATH="$HOME/chileanfires/fires-api/cron"
GET_DATA="$APP_PATH/get-data.py"
MERGE_DATA="$APP_PATH/merge-data.py"

(crontab -l 2>/dev/null; echo "*/10 * * * * "$HOME/miniconda3/envs/$CONDA_ENV_NAME/bin/python" $GET_DATA") | crontab -
(crontab -l 2>/dev/null; echo "*/11 * * * * "$HOME/miniconda3/envs/$CONDA_ENV_NAME/bin/python" $MERGE_DATA") | crontab -

@reboot $HOME/miniconda3/envs/$CONDA_ENV_NAME/bin/python $GET_DATA
@reboot $HOME/miniconda3/envs/$CONDA_ENV_NAME/bin/python $MERGE_DATA