# ---------------------------------------------------------------------------------------
# Project: BusyLight Power Off Script
# Author: Evaristo R. Rivieccio Vega - SysAdmin
# GitHub: https://github.com/evaristorivieccio
# LinkedIn: https://www.linkedin.com/in/evaristorivieccio/
# Web: https://www.evaristorivieccio.es/
# ---------------------------------------------------------------------------------------
# Description:
# This Python script is used to send a signal to turn off the BusyLight indicator via an API.
# It supports both shared and full mode configurations, allowing users to control which side
# of the LED strip is affected if in shared mode.
# 
# Key Functionalities:
# 
# 1. **Configuration**: Allows toggling between full mode and shared mode via `USE_SHARED_MODE`.
#    In shared mode, `SHARED_SIDE` determines which side of the LED strip is turned off.
# 
# 2. **Signal Transmission**: Sends a POST request to the BusyLight API endpoint with a payload
#    to indicate that the light should be turned off.
# 
# 3. **Main Execution**: When run, this script will send the "off" signal to the BusyLight API.
# 
# Usage:
# 1. Ensure Python and the `requests` library are installed.
# 2. Update the `base_url` variable to point to your BusyLight API.
# 3. Run this script to turn off the BusyLight indicator.
#
# Example:
#    python power_off_script.py
#
# ---------------------------------------------------------------------------------------

import requests
import json

# Configuration for shared or full mode
USE_SHARED_MODE = True  # Change to False for full mode
SHARED_SIDE = "left"  # If in shared mode, use "left" or "right"

# Define the base URL for your API 
base_url = "http://192.168.1.129:5000/API/signal" #CHANGES ACCORDING TO THE ADDRESS OF YOUR API SERVER

# Function to send the OFF signal
def send_off_signal():
    # Create the request payload
    payload = {
        "color": "off"
    }
    
    # Add the half key to the payload if shared mode is enabled
    if USE_SHARED_MODE:
        payload["half"] = SHARED_SIDE
    
    # Send the POST request
    response = requests.post(base_url, headers={"Content-Type": "application/json"}, data=json.dumps(payload))
    
    # Print the result
    print(f"Response Code: {response.status_code}")
    print(f"Response Body: {response.json()}")

if __name__ == "__main__":
    send_off_signal()
