# ---------------------------------------------------------------------------------------
# Project: BusyLight Windows Client
# Author: Evaristo R. Rivieccio Vega - SysAdmin
# GitHub: https://github.com/evaristorivi
# LinkedIn: https://www.linkedin.com/in/evaristorivieccio/
# Web: https://www.evaristorivieccio.es/
# ---------------------------------------------------------------------------------------
# Description:
# This Python script is a Windows client designed to control the BusyLight system by 
# monitoring the status of audio sessions in real-time. The script uses the Pycaw library 
# to detect whether the microphone is in use by common communication applications 
# such as Microsoft Teams, Zoom, Skype, or Slack. 
# 
# When the microphone is in use, it sends a signal to the BusyLight API to turn the LED 
# strip red. When the microphone is not in use, it sends a signal to change the color to green.
#
# The client can operate in shared mode or full mode:
# - **Shared mode**: Controls either the left or right half of the LED strip (useful for shared offices).
# - **Full mode**: Controls the entire strip.
#
# The script continuously monitors the audio session states and only sends signals to 
# the API when a change in the microphone status is detected.
#
# Configuration options allow setting the mode (shared or full) and defining which half of 
# the strip to control in shared mode.
#
# Usage:
# Use install.ps1
#
# ---------------------------------------------------------------------------------------

from pycaw.pycaw import AudioUtilities, IAudioSessionControl2
from ctypes import cast, POINTER
import psutil
import time
import requests
import json

# Define the base URL for your API
base_url = "http://192.168.1.129:5000/API/signal" #CHANGES ACCORDING TO THE ADDRESS OF YOUR API SERVER

# Configuration
USE_SHARED_MODE = True  # Set to False for full mode, True for shared mode
SHARED_SIDE = "right"  # Options: "left" or "right", only used if USE_SHARED_MODE is True

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

# List of processes to ignore
ignored_processes = {'simhubwpf.exe'}
communication_apps = {'ms-teams.exe', 'Teams.exe', 'Msteams.exe', 'zoom.exe', 'skype.exe', 'slack.exe'}

def get_session_process_name(session):
    """Gets the name of the process using the audio session."""
    try:
        control = cast(session._ctl, POINTER(IAudioSessionControl2))
        process_id = control.GetProcessId()
        process = psutil.Process(process_id)
        return process.name().lower()
    except Exception as e:
        print(f"Error getting process name: {e}")
        return None

def is_microphone_in_use():
    """Checks if the microphone is in use and returns the process name if it is."""
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        try:
            control = cast(session._ctl, POINTER(IAudioSessionControl2))
            state = control.GetState()
            
            # Check if the session is active (IAudioSessionStateActive)
            if state & 1:  # This indicates that the session is in use
                process_name = get_session_process_name(session)
                if process_name and process_name not in ignored_processes:
                    return process_name
        except Exception as e:
            print(f"Error checking session: {e}")
    
    return None

def main():
    # Initial microphone state
    mic_in_use = False

    # Check initial state and send the first signal
    process_name = is_microphone_in_use()
    mic_in_use = process_name in communication_apps

    if mic_in_use:
        print(f"The microphone is in use by: {process_name}")
        send_signal("red")
    else:
        print("The microphone is not in use.")
        send_signal("green")

    # Main loop
    while True:
        # Check the current microphone state
        process_name = is_microphone_in_use()
        new_mic_in_use = process_name in communication_apps

        # Only send a signal when the state changes
        if new_mic_in_use != mic_in_use:
            if new_mic_in_use:
                print(f"The microphone is in use by: {process_name}")
                send_signal("red")
            else:
                print("The microphone is not in use.")
                send_signal("green")

            # Update the microphone state
            mic_in_use = new_mic_in_use
        
        # Wait before checking again
        time.sleep(5)

if __name__ == "__main__":
    main()
