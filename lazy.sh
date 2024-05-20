#!/bin/bash

echo "> Creating virtual environment..."
python -m venv env
echo "> Activating virtual environment..."
source env/bin/activate
echo "> Installing required packages..."
pip install -r requirements.txt
echo "> Google API v3 requires key. You can obtain it from the following link:"
echo "https://console.cloud.google.com/apis/credentials"
read -p "Enter your Google API v3 key: " api_key
echo "> Setting the API key..."
python scripts/app.py -k "$api_key"
echo "> Setup complete. Deleting setup script..."
rm -- "$0"