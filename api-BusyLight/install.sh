#!/bin/bash
# ---------------------------------------------------------------------------------------
# Project: BusyLight API Deployment Script
# Author: Evaristo R. Rivieccio Vega - SysAdmin
# GitHub: https://github.com/evaristorivi
# LinkedIn: https://www.linkedin.com/in/evaristorivieccio/
# Web: https://www.evaristorivieccio.es/
# ---------------------------------------------------------------------------------------
# Description:
# This script is designed to deploy and run the BusyLight API on a server.
# It handles the necessary configurations and starts the API service using FastAPI.
#
# The script ensures that all dependencies are met, configures the server settings, 
# and launches the API in an environment that can handle multiple clients simultaneously.
# The API is responsible for controlling a Waveshare RGB LED HAT as a BusyLight.
#
# Use:
# sudo chmod +x install.sh
# sudo ./install.sh
#
# ---------------------------------------------------------------------------------------


# Check if the script is being run as root
if [ "$(id -u)" -ne 0 ]; then
  echo "This script must be run as root. Use sudo to execute the script."
  exit 1
fi

# Variables
APP_DIR=$(pwd)
VENV_DIR="$APP_DIR/venv"
REQUIREMENTS_FILE="$APP_DIR/requirements.txt"
SERVICE_FILE="/etc/systemd/system/busylight-evaristorivi.service"
USER="$(whoami)"

# Install system dependencies
echo "Updating repositories..."
apt-get update
echo "Installing system dependencies..."
apt-get install -y python3-venv python3-pip

# Create the application directory if it does not exist
echo "Creating the application directory..."
mkdir -p $APP_DIR

# Create and activate the virtual environment
echo "Creating the virtual environment..."
python3 -m venv $VENV_DIR

# Install the application dependencies within the virtual environment
echo "Installing application dependencies..."
$VENV_DIR/bin/pip install --upgrade pip
$VENV_DIR/bin/pip install -r $REQUIREMENTS_FILE

# Create systemd service file
echo "Creating systemd service file..."
tee $SERVICE_FILE > /dev/null <<EOL
[Unit]
Description=FastAPI Application Service
After=network.target

[Service]
User=$USER
WorkingDirectory=$APP_DIR
ExecStart=$VENV_DIR/bin/uvicorn API:app --host 0.0.0.0 --port 5000
Restart=always
RestartSec=10
Environment="PATH=$VENV_DIR/bin"

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd, start and enable the service
echo "Reloading systemd and configuring the service..."
systemctl daemon-reload
systemctl start busylight-evaristorivi.service
systemctl enable busylight-evaristorivi.service

echo "Deployment completed."
