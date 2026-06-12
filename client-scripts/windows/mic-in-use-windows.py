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
# Run the script directly using Python. Ensure the BusyLight API is correctly configured and running.
#
# ---------------------------------------------------------------------------------------

import time
import requests
import json
import winreg

# -----------------------------
# CONFIGURATION
# -----------------------------

base_url = "http://192.168.1.129:5000/API/signal"

USE_SHARED_MODE = True
SHARED_SIDE = "right"

MICROPHONE_REG_BASE = r"Software\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\microphone"

# -----------------------------
# BUSYLIGHT API
# -----------------------------

def send_signal(color):
    payload = {"color": color}

    if USE_SHARED_MODE:
        payload["half"] = SHARED_SIDE

    try:
        response = requests.post(
            base_url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=3
        )
        print(f"Response Code: {response.status_code}")
        print(f"Response Body: {response.json()}")

    except requests.RequestException as e:
        print(f"Error sending signal: {e}")

# -----------------------------
# MICROPHONE DETECTION
# -----------------------------

def any_app_using_microphone():
    """
    Returns True if any application is currently using the microphone.
    Uses Windows CapabilityAccessManager registry (reliable for Teams/WebView2 apps).
    """
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, MICROPHONE_REG_BASE)

        i = 0
        while True:
            try:
                subkey_name = winreg.EnumKey(key, i)
                i += 1

                app_path = MICROPHONE_REG_BASE + "\\" + subkey_name
                app_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, app_path)

                try:
                    start, _ = winreg.QueryValueEx(app_key, "LastUsedTimeStart")
                    stop, _ = winreg.QueryValueEx(app_key, "LastUsedTimeStop")

                    # If start > stop → microphone currently in use
                    if start > stop:
                        return True, subkey_name

                except FileNotFoundError:
                    continue

            except OSError:
                break

    except Exception as e:
        print(f"Microphone check error: {e}")

    return False, None

# -----------------------------
# MAIN LOOP
# -----------------------------

def main():
    mic_in_use = False

    # Initial state
    in_use, app = any_app_using_microphone()
    mic_in_use = in_use

    if mic_in_use:
        print(f"Microphone is in use by: {app}")
        send_signal("red")
    else:
        print("Microphone is not in use.")
        send_signal("green")

    # Monitoring loop
    while True:
        in_use, app = any_app_using_microphone()

        if in_use != mic_in_use:
            if in_use:
                print(f"Microphone is in use by: {app}")
                send_signal("red")
            else:
                print("Microphone is not in use.")
                send_signal("green")

            mic_in_use = in_use

        time.sleep(2)

# -----------------------------
# ENTRY POINT
# -----------------------------

if __name__ == "__main__":
    main()