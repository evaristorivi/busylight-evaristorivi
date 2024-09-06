# ---------------------------------------------------------------------------------------
# Project: BusyLight Linux Client (Multi-Distribution)
# Author: Evaristo R. Rivieccio Vega - SysAdmin
# GitHub: https://github.com/evaristorivieccio
# LinkedIn: https://www.linkedin.com/in/evaristorivieccio/
# Web: https://www.evaristorivieccio.es/
# ---------------------------------------------------------------------------------------
# Description:
# This Python script is designed for Linux systems (Ubuntu, Debian, RedHat, CentOS, etc.) 
# to monitor microphone usage and communicate with the BusyLight API. It detects the active
# audio system (PulseAudio, PipeWire, or ALSA) and uses system commands to determine whether 
# the microphone is in use.
# 
# Key Functionalities:
# 
# 1. **Configuration**: Allows toggling between full mode and shared mode via `USE_SHARED_MODE`.
#    In shared mode, `SHARED_SIDE` determines which side of the LED strip is affected.
# 
# 2. **Audio System Detection**: Automatically detects whether PulseAudio, PipeWire, or ALSA is being
#    used and adjusts the microphone monitoring method accordingly.
# 
# 3. **Microphone Monitoring**: Uses system commands (`pactl`, `arecord`) to check the microphone's 
#    status and determine if it is in use.
# 
# 4. **Signal Transmission**: Sends a POST request to the BusyLight API endpoint to indicate whether 
#    the microphone is in use ("red") or not ("green").
# 
# 5. **Main Loop**: Continuously checks the microphone status and sends appropriate signals when a 
#    change is detected.
# 
# Usage:
# 1. Ensure Python and the `requests` library are installed.
# 2. Update the `base_url` variable to point to your BusyLight API.
# 3. Run this script on a Linux machine. The script will continuously check microphone usage and
#    send corresponding signals to the BusyLight API.
#
# Example:
#    python linux_client.py
#
# ---------------------------------------------------------------------------------------

import subprocess
import time
import requests
import json

# Define the base URL for your API
base_url = "http://192.168.1.129:5000/API/signal"  # Change according to your API server address

# Configuration
USE_SHARED_MODE = True  # Set to False for full mode, True for shared mode
SHARED_SIDE = "right"  # Options: "left" or "right", only used if USE_SHARED_MODE is True

# Detect the audio system (PulseAudio, PipeWire, or ALSA)
def detect_audio_system():
    try:
        # Check if PulseAudio is running
        subprocess.run(['pactl', 'info'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return 'pulseaudio'
    except subprocess.CalledProcessError:
        pass

    try:
        # Check if PipeWire is running (also uses pactl)
        subprocess.run(['pipewire', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return 'pipewire'
    except subprocess.CalledProcessError:
        pass

    try:
        # Check if ALSA is available
        subprocess.run(['arecord', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return 'alsa'
    except subprocess.CalledProcessError:
        pass

    return None

# Function to check if the microphone is in use with PulseAudio
def is_microphone_in_use_pulseaudio():
    try:
        result = subprocess.run(['pactl', 'list', 'source-outputs'], capture_output=True, text=True)
        return bool(result.stdout.strip())
    except Exception as e:
        print(f"Error executing command: {e}")
        return False

# Function to check if the microphone is in use with ALSA
def is_microphone_in_use_alsa():
    try:
        result = subprocess.run(['arecord', '-l'], capture_output=True, text=True)
        return bool(result.stdout.strip())
    except Exception as e:
        print(f"Error executing command: {e}")
        return False

# Function to send a signal to the API
def send_signal(color):
    payload = {"color": color}
    
    if USE_SHARED_MODE:
        payload["half"] = SHARED_SIDE
    
    response = requests.post(base_url, headers={"Content-Type": "application/json"}, data=json.dumps(payload))
    
    print(f"Response Code: {response.status_code}")
    print(f"Response Body: {response.json()}")

def main():
    # Detect the audio system
    audio_system = detect_audio_system()

    if audio_system == 'pulseaudio' or audio_system == 'pipewire':
        print(f"Using audio system: {audio_system}")
        is_microphone_in_use = is_microphone_in_use_pulseaudio
    elif audio_system == 'alsa':
        print("Using audio system: ALSA")
        is_microphone_in_use = is_microphone_in_use_alsa
    else:
        print("No compatible audio system detected.")
        return

    mic_in_use = is_microphone_in_use()

    if mic_in_use:
        print("Initial check: The microphone is in use.")
        send_signal("red")
    else:
        print("Initial check: The microphone is not in use.")
        send_signal("green")

    state = mic_in_use

    while True:
        mic_in_use = is_microphone_in_use()

        if mic_in_use != state:
            if mic_in_use:
                print("The microphone is in use.")
                send_signal("red")
            else:
                print("The microphone is not in use.")
                send_signal("green")
            
            state = mic_in_use

        time.sleep(5)

if __name__ == "__main__":
    main()
