#!/bin/bash

# Env vars
source set-env-vars.sh

# Get the current username and groupname
USERNAME=$(whoami)
GROUPNAME=$(id -gn)

# Set your configuration variables
APP_PATH="$HOME/chileanfires/fires-api/"
CONDA_ENV_NAME="api"
GUNICORN_CONFIG="gunicorn_config.py"
APP_MODULE="run:app"
GUNICORN_CMD="$HOME/miniconda3/envs/$CONDA_ENV_NAME/bin/gunicorn --config $GUNICORN_CONFIG $APP_MODULE"

# Create Gunicorn service file
SERVICE_FILE="/etc/systemd/system/myapp_gunicorn.service"

cat <<EOF > $SERVICE_FILE
[Unit]
Description=Gunicorn instance to serve fires-api
After=network.target

[Service]
User=$USERNAME
Group=$GROUPNAME
WorkingDirectory=$APP_PATH
ExecStart=$GUNICORN_CMD

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and start the service
systemctl daemon-reload
systemctl start myapp_gunicorn

# Enable the service to start on boot
systemctl enable myapp_gunicorn

echo "Gunicorn setup complete. The service is now running and will start on boot."