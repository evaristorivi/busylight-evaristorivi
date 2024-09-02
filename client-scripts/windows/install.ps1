# ---------------------------------------------------------------------------------------
# Project: BusyLight Installation Script
# Author: Evaristo R. Rivieccio Vega - SysAdmin
# GitHub: https://github.com/evaristorivi
# LinkedIn: https://www.linkedin.com/in/evaristorivieccio/
# Web: https://www.evaristorivieccio.es/
# ---------------------------------------------------------------------------------------
# Description:
# This PowerShell script is designed to automate the installation and configuration of the 
# BusyLight Windows client. It performs the following tasks:
# 
# 1. **Checks for Python and Pip**: Ensures that Python and Pip are installed and available 
#    in the system PATH.
# 2. **Installs Dependencies**: Reads the `requirements.txt` file to install the necessary 
#    Python packages required by the BusyLight client script.
# 3. **Configures Scheduled Task**: Sets up a Windows Scheduled Task to run the 
#    `mic-in-use-windows.py` script automatically at user logon. This ensures that the 
#    BusyLight client script starts running when the user logs in, monitoring microphone 
#    usage and sending appropriate signals to the BusyLight API.
# 
# The script will:
# - Verify if Python and Pip are installed.
# - Install the Python dependencies if `requirements.txt` is present.
# - Check for an existing scheduled task with the same name and remove it if necessary.
# - Create a new scheduled task to run the BusyLight client script with the highest privileges.
#
# Usage:
# 1. Ensure that `mic-in-use-windows.py` and `requirements.txt` are in the same folder. 

# 2. Run this PowerShell script as an Administrator to install and configure the BusyLight 
#    client.
#
# Example:
#    powershell -ExecutionPolicy Bypass -File .\install.ps1
#
# ---------------------------------------------------------------------------------------

# Paths for installation and files
$pythonScriptPath = "C:\busylight\mic-in-use-windows.py"
$requirementsPath = "C:\busylight\requirements.txt"
$taskName = "MicInUseTask"
$taskDescription = "Task to run the mic-in-use-windows.py script at logon."

# Check if Python is installed
$pythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $pythonPath) {
    Write-Error "Python is not installed or not in the PATH."
    exit 1
}

# Check if pip is installed
$pipPath = (Get-Command pip -ErrorAction SilentlyContinue).Source
if (-not $pipPath) {
    Write-Error "Pip is not installed or not in the PATH."
    exit 1
}

# Install dependencies from requirements.txt
if (Test-Path $requirementsPath) {
    Write-Output "Installing dependencies from $requirementsPath..."
    & $pipPath install -r $requirementsPath
} else {
    Write-Error "requirements.txt not found at the specified location."
    exit 1
}

# Check if the scheduled task already exists and unregister it if so
if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
    Write-Output "Task $taskName already exists. Unregistering..."
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

# Define the configuration for the scheduled task
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -Hidden:$false `
    -WakeToRun:$false `
    -ExecutionTimeLimit (New-TimeSpan -Seconds 0) `
    -Priority 7 `
    -MultipleInstances IgnoreNew `
    -DontStopOnIdleEnd `
    -RestartOnIdle `
    -IdleWaitTimeout (New-TimeSpan -Minutes 10)

# Define the action for the scheduled task
$action = New-ScheduledTaskAction `
    -Execute "cmd.exe" `
    -Argument "/c start /min python $pythonScriptPath"

# Define the trigger for the scheduled task
$trigger = New-ScheduledTaskTrigger `
    -AtLogon

# Define the principal for the scheduled task
$principal = New-ScheduledTaskPrincipal `
    -UserId "$($env:USERNAME)" `
    -LogonType Interactive `
    -RunLevel Highest

# Register the scheduled task
if (Test-Path $pythonScriptPath) {
    Write-Output "Registering the scheduled task..."
    Register-ScheduledTask `
        -TaskName $taskName `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Principal $principal `
        -Description $taskDescription
} else {
    Write-Error "The Python script was not found at the specified location."
    exit 1
}

Write-Output "Installation and configuration completed successfully."

