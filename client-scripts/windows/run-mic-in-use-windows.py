# ---------------------------------------------------------------------------------------
# Project: BusyLight Windows Client - Runner Script
# Author: Evaristo R. Rivieccio Vega - SysAdmin
# GitHub: https://github.com/evaristorivi
# LinkedIn: https://www.linkedin.com/in/evaristorivieccio/
# Web: https://www.evaristorivieccio.es/
# ---------------------------------------------------------------------------------------
# Description:
# This Python script is a runner for the BusyLight Windows Client. It is designed to 
# ensure that the main script, mic-in-use-windows.py, continues to run indefinitely by 
# restarting it if it closes unexpectedly. 
# 
# The main script monitors the status of audio sessions in real-time and sends signals 
# to the BusyLight API to control the LED strip based on whether the microphone is in use 
# or not. 
# 
# The runner script is responsible for:
# - Launching the main script.
# - Detecting if the main script terminates.
# - Restarting the main script if it exits.
# 
# Usage:
# Run this script to ensure that the BusyLight client script is always running.
# 
# ---------------------------------------------------------------------------------------

import subprocess
import time
import os
import sys

def run_script():
    print("The service is running. You can minimise this window.")
    script_path = os.path.join(os.path.dirname(__file__), 'mic-in-use-windows.py')
    
    process = subprocess.Popen([sys.executable, script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    while True:
        exit_code = process.wait()
        
        # stdout, stderr = process.communicate()
        # if stdout:
        #     print(stdout.decode())
        # if stderr:
        #     print(stderr.decode())
        
        time.sleep(1) 
        process = subprocess.Popen([sys.executable, script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

if __name__ == "__main__":
    run_script()
