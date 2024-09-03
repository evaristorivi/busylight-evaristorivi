# ---------------------------------------------------------------------------------------
# Project: BusyLight Installation Script
# Author: Evaristo R. Rivieccio Vega - SysAdmin
# GitHub: https://github.com/evaristorivi
# LinkedIn: https://www.linkedin.com/in/evaristorivieccio/
# Web: https://www.evaristorivieccio.es/
# ---------------------------------------------------------------------------------------

# Paths for installation and files
$installPath = "C:\busylight"
$pythonScriptPath = "$installPath\run-mic-in-use-windows.py"
$requirementsPath = "$installPath\requirements.txt"
$taskName = "MicInUseTask"
$taskDescription = "Task to run the run-mic-in-use-windows.py script at logon."

# Create installation folder if it does not exist
if (-not (Test-Path -Path $installPath)) {
    Write-Output "Creating installation directory at $installPath..."
    New-Item -ItemType Directory -Path $installPath
}

# Get the location of the script (current directory)
$scriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Definition

# Check if the files exist and move them
if (Test-Path "$scriptDirectory\run-mic-in-use-windows.py") {
    Write-Output "Moving run-mic-in-use-windows.py to $installPath..."
    Move-Item -Path "$scriptDirectory\run-mic-in-use-windows.py" -Destination $pythonScriptPath -Force
} else {
    Write-Error "run-mic-in-use-windows.py not found in the script directory."
    exit 1
}

if (Test-Path "$scriptDirectory\mic-in-use-windows.py") {
    Write-Output "Moving mic-in-use-windows.py to $installPath..."
    Move-Item -Path "$scriptDirectory\mic-in-use-windows.py" -Destination "$installPath\mic-in-use-windows.py" -Force
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
