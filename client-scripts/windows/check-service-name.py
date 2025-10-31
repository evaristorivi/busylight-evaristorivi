# ---------------------------------------------------------------------------------------
# Project: BusyLight Windows Client
# Author: Evaristo R. Rivieccio Vega - SysAdmin
# GitHub: https://github.com/evaristorivi
# LinkedIn: https://www.linkedin.com/in/evaristorivieccio/
# Web: https://www.evaristorivieccio.es/
# ---------------------------------------------------------------------------------------
# Description:
# # This is to find out the name of the application that is using the sound and add it to the ignored_processes or communication_apps variable.
#
#
# ---------------------------------------------------------------------------------------

from pycaw.pycaw import AudioUtilities, IAudioSessionControl2

sessions = AudioUtilities.GetAllSessions()
for session in sessions:
    try:
        control = session._ctl.QueryInterface(IAudioSessionControl2)
        process_id = control.GetProcessId()
        process_name = session.Process.name() if session.Process else "Unknown"
        state = control.GetState()
        print(f"Process: {process_name}, PID: {process_id}, State: {state}")
    except Exception as e:
        print(f"Error: {e}")
