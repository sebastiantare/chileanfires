#!/bin/bash

USERNAME=$(whoami)
GROUPNAME=$(id -gn)
CONDA_ENV_NAME="api"

APP_PATH="$HOME/chileanfires/cron"
GET_DATA="$APP_PATH/get-data.sh"
MERGE_DATA="$APP_PATH/merge-data.sh"

(crontab -l 2>/dev/null; echo "*/10 * * * * $GET_DATA") | crontab -
(crontab -l 2>/dev/null; echo "1,11,21,31,41,51 * * * * $MERGE_DATA") | crontab -