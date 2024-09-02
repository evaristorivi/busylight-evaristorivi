# ---------------------------------------------------------------------------------------
# Project: BusyLight macOS Legacy Client
# Author: Evaristo R. Rivieccio Vega - SysAdmin
# GitHub: https://github.com/evaristorivieccio
# LinkedIn: https://www.linkedin.com/in/evaristorivieccio/
# Web: https://www.evaristorivieccio.es/
# ---------------------------------------------------------------------------------------
# Description:
# This Python script is designed for macOS systems to monitor microphone usage and communicate
# with the BusyLight API. It is considered a legacy approach using system commands to determine
# microphone status.
# 
# Key Functionalities:
# 
# 1. **Configuration**: Allows toggling between full mode and shared mode via `USE_SHARED_MODE`.
#    In shared mode, `SHARED_SIDE` determines which side of the LED strip is affected.
# 
# 2. **Microphone Monitoring**: Uses `subprocess` to execute system commands to check the microphone's
#    status. Specifically, it queries the `ioreg` command for the AppleHDA engine and uses `grep` and
#    `wc` to determine if the microphone is active.
# 
# 3. **Signal Transmission**: Sends a POST request to the BusyLight API endpoint to indicate whether
#    the microphone is in use ("red") or not ("green").
# 
# 4. **Main Loop**: Continuously checks the microphone status and sends appropriate signals when a
#    change is detected.
# 
# Usage:
# 1. Ensure Python and the `requests` library are installed.
# 2. Update the `base_url` variable to point to your BusyLight API.
# 3. Run this script on a macOS machine. The script will continuously check microphone usage and
#    send corresponding signals to the BusyLight API.
#
# Example:
#    python mac_legacy_client.py
#
# ---------------------------------------------------------------------------------------

import subprocess
import time
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

# Function to check if the microphone is in use
def is_microphone_in_use():
    try:
        # Execute the ioreg command to get the input details of the AppleHDA engine
        result = subprocess.run(
            ['ioreg', '-l', 'AppleHDAEngineInput'],
            capture_output=True,
            text=False
        )
        
        # Use grep to filter the output based on IOAudioEngineState being active (1)
        grep_result = subprocess.run(
            ['grep', '"IOAudioEngineState" = 1'],
            input=result.stdout,
            capture_output=True,
            text=False
        )

        # Count the number of matching lines with wc -l
        wc_result = subprocess.run(
            ['wc', '-l'],
            input=grep_result.stdout,
            capture_output=True,
            text=False
        )
        
        # Return True if the microphone is in use (i.e., if there are more than 0 lines)
        return int(wc_result.stdout.strip()) > 0

    except Exception as e:
        print(f"Error executing the command: {e}")
        return False

def main():
    # Initial state of the microphone (not in use)
    state = False

    # Continuous loop to check microphone status
    while True:
        mic_in_use = is_microphone_in_use()

        # If the microphone state changes, send the appropriate signal
        if mic_in_use != state:
            if mic_in_use:
                print("The microphone is in use.")
                send_signal("red")
            else:
                print("The microphone is not in use.")
                send_signal("green")
            # Update the state
            state = mic_in_use

        # Wait for 5 seconds before the next check
        time.sleep(5)

if __name__ == "__main__":
    main()
