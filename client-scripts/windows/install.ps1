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
$installPath = "C:\busylight"
$pythonScriptPath = "$installPath\mic-in-use-windows.py"
$requirementsPath = "$installPath\requirements.txt"
$taskName = "MicInUseTask"
$taskDescription = "Task to run the mic-in-use-windows.py script at logon."

# Create installation folder if it does not exist
if (-not (Test-Path -Path $installPath)) {
    Write-Output "Creating installation directory at $installPath..."
    New-Item -ItemType Directory -Path $installPath
}

# Get the location of the script (current directory)
$scriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Definition

# Check if the files exist and move them
if (Test-Path "$scriptDirectory\mic-in-use-windows.py") {
    Write-Output "Moving mic-in-use-windows.py to $installPath..."
    Move-Item -Path "$scriptDirectory\mic-in-use-windows.py" -Destination $pythonScriptPath -Force
} else {
    Write-Error "mic-in-use-windows.py not found in the script directory."
    exit 1
}

if (Test-Path "$scriptDirectory\requirements.txt") {
    Write-Output "Moving requirements.txt to $installPath..."
    Move-Item -Path "$scriptDirectory\requirements.txt" -Destination $requirementsPath -Force
} else {
    Write-Error "requirements.txt not found in the script directory."
    exit 1
}

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

# Unregister old task (if exists)
Write-Output "Checking if the task $taskName already exists..."
schtasks /Query /TN $taskName > $null 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Output "Task $taskName already exists. Deleting..."
    schtasks /Delete /TN $taskName /F
}

# Register new task using schtasks.exe with your original cmd.exe /c start /min line
$user = $env:USERNAME
$taskCommand = "cmd.exe"
$taskArguments = "/c start /min python `"$pythonScriptPath`""

Write-Output "Registering the scheduled task as user $user..."
schtasks /Create `
    /TN $taskName `
    /TR "$taskCommand $taskArguments" `
    /SC ONLOGON `
    /RL HIGHEST `
    /F `
    /DELAY 0000:30 `
    /RU $user

if ($LASTEXITCODE -eq 0) {
    Write-Output "Scheduled task created successfully."
} else {
    Write-Error "Failed to create the scheduled task. Exit code: $LASTEXITCODE"
    exit 1
}

Write-Output "Installation and configuration completed successfully."
