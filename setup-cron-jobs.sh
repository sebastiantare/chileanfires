#!/bin/bash
cd cron

GET_DATA="get-data.py"
MERGE_DATA="merge-data.py"

# Get the current username and groupname
USERNAME=$(whoami)
GROUPNAME=$(id -gn)
CONDA_ENV_NAME="api"

# Schedule cron jobs
(crontab -l 2>/dev/null; echo "*/10 * * * * "$HOME/miniconda3/envs/$CONDA_ENV_NAME/bin/python" /path/to/script1.py") | crontab -
(crontab -l 2>/dev/null; echo "*/10 * * * * "$HOME/miniconda3/envs/$CONDA_ENV_NAME/bin/python" /path/to/script2.py") | crontab -

# Set up scripts to run on boot (add to crontab)
@reboot /path/to/conda activate my_env && /path/to/python /path/to/script1.py
@reboot /path/to/conda activate my_env && /path/to/python /path/to/script2.py