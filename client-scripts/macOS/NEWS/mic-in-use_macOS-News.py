# ---------------------------------------------------------------------------------------
# Project: BusyLight macOS Client
# Author: Evaristo R. Rivieccio Vega - SysAdmin
# GitHub: https://github.com/evaristorivi
# LinkedIn: https://www.linkedin.com/in/evaristorivieccio/
# Web: https://www.evaristorivieccio.es/
# ---------------------------------------------------------------------------------------
# Description:
# This Python script is designed for macOS to interact with the BusyLight API. It monitors
# the microphone usage and sends a signal to the BusyLight API to indicate the microphone
# status. It does the following:
# 
# 1. **Configuration**: Allows configuration for shared mode where the light will be controlled
#    for either the left or right side of the LED strip based on `USE_SHARED_MODE` and `SHARED_SIDE`.
# 
# 2. **Mic Status Monitoring**: Uses the `atomacos` library to access macOS's Control Center and
#    determine if the microphone is currently in use.
# 
# 3. **Signal Transmission**: Sends a POST request to the BusyLight API endpoint with either
#    "red" or "green" based on the microphone status.
# 
# 4. **Main Loop**: Continuously checks the microphone status and updates the BusyLight API
#    whenever a change in status is detected.
# 
# Usage:
# 1. Ensure that the `atomacos` library is installed. This script requires macOS's Accessibility
#    permissions to function properly.
# 2. Update the `base_url` variable with the correct URL for your BusyLight API.
# 3. Run this script on a macOS machine. It will continuously monitor the microphone usage
#    and send appropriate signals to the BusyLight API.
#
# Example:
#    python mac_client.py
#
# ---------------------------------------------------------------------------------------

import time
import atomacos
import requests
import json

# Define the base URL for your API
base_url = "http://192.168.1.129:5000/API/signal" #CHANGES ACCORDING TO THE ADDRESS OF YOUR API SERVER

# Configuration
USE_SHARED_MODE = True  # Set to False for full mode, True for shared mode
SHARED_SIDE = "left"  # Options: "left" or "right", only used if USE_SHARED_MODE is True

# Function to send a POST request
def send_signal(color):
    # Create the request payload
    payload = {
        "color": color
    }

    # Add the half key to the payload only if shared mode is enabled
    if USE_SHARED_MODE:
        payload["half"] = SHARED_SIDE
    
    # Send the POST request
    response = requests.post(base_url, headers={"Content-Type": "application/json"}, data=json.dumps(payload))
    
    # Print the result
    print(f"Response Code: {response.status_code}")
    print(f"Response Body: {response.json()}")

# Get a reference to the Control Center of macOS
sysui = atomacos.getAppRefByBundleId('com.apple.controlcenter')

# Initial microphone state
state = {"incall": False}

# Function to check the microphone status
def check_mic_state():
    # Find all relevant elements in the Control Center interface
    elems = [elem for elem in sysui.findAllR() if 'AXDescription' in elem.getAttributes()]
    
    # Filter elements that mention "Microphone" and "use", but only if they have 'AXDescription'
    descs = []
    for elem in elems:
        try:
            # Check if the element has an AXDescription and analyze it
            if elem.AXDescription and 'Microphone' in elem.AXDescription.split() and 'use' in elem.AXDescription.split():
                descs.append(elem)
        except AttributeError:
            # Ignore the element if it does not have AXDescription or if it cannot be accessed
            pass
    
    # Determine if the microphone is in use
    return bool(descs)

# Check initial microphone state
is_mic_on = check_mic_state()

# Send the initial signal based on the microphone state
if is_mic_on:
    print("The microphone is in use.")
    send_signal("red")
else:
    print("The microphone is not in use.")
    send_signal("green")

# Update the initial state
state = {"incall": is_mic_on}

# Main loop
while True:
    # Check the current microphone state
    is_mic_on = check_mic_state()

    # New state based on the verification
    new_state = {"incall": is_mic_on}

    # Compare the new state with the previous state
    if new_state != state:
        if is_mic_on:
            print("The microphone is in use.")
            send_signal("red")
        else:
            print("The microphone is not in use.")
            send_signal("green")
        
        # Update the state
        state = new_state
    
    # Wait for a brief period before the next check
    time.sleep(5)
