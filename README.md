![BusyLight](images/BusyLight_50_percent.png)

# BusyLight
## Description
<img src="images/2.jpg" alt="BusyLight" width="500"/>
<img src="images/3.jpg" alt="BusyLight" width="500"/>
<img src="images/green.jpg" alt="BusyLight" width="500"/>
<img src="images/redall.jpg" alt="BusyLight" width="500"/>
<img src="images/red_green.jpg" alt="BusyLight" width="500"/>


**BusyLight** is a solution designed for remote work or office environments, allowing others to know if you're in a meeting or available. It works by monitoring microphone activity with a script, which then sends a signal to an API that controls an RGB LED light, indicating your status.

This system can be used for a single office or in shared mode, where the light can be split to show the availability of two different workspaces. Whether you're at home or in the office, BusyLight helps communicate your availability clearly, without interruptions.
## Project Components

- **API Server**: A backend service that receives signals and controls the light.
- **Windows Client**: A Python script for Windows to monitor microphone status and communicate with the API server.
- **macOS Client (modern)**: A Python script for modern macOS systems to check microphone status and send signals.
- **macOS Client (legacy)**: A Python script using system commands for older macOS versions.
- **Shutdown Script**: A cross-platform script to turn off the light through the API.

## API Server

**Description:**
The API has been installed on a Raspberry Pi Zero 2W with a Waveshare RGB LED HAT. This API controls the Waveshare RGB LED HAT, designed to function as a BusyLight indicator. It supports multiple lighting modes, including the ability to set different colors (green, red, orange) and adjust the intensity. The API can operate in full mode or shared mode (left and right sides). It also includes scheduling functionality to enforce operating hours and can respond to system status requests such as CPU temperature.

**Key Features:**
- Control the color and intensity of the LED strip.
- Split the control between the left and right halves of the strip (in shared mode).
- Schedule operation hours with automatic shutdown outside of operating times.
- Monitor CPU temperature.

**Usage:**
- Send POST requests to `/API/signal` to control the LED colors and intensity.
- Send POST requests to `/API/off` to turn off all or part of the LED strip.
- Use GET requests to `/API/temperature` to retrieve the current CPU temperature.

**API Documentation:**
- API docs: http://API.IP...:5000/docs
- API Redoc: http://API.IP...:5000/redoc

## Installation

### API Server Installation
1. **Clone the Repository**

   ```
   #Download the repository or clone it
   git clone https://github.com/evaristorivi/busylight-evaristorivi
   cd busylight-evaristorivi/api-BusyLight/
2. **Run Installation Script**
   ```
   chmod +x install.sh
   sudo ./install.sh
This will install in the current directory the virtual python environment with its dependencies and set up a systemd service.

Note: It is recommended to use a static IP address for the API server, either configured manually or through DHCP, as this IP address will be used in the client scripts.

### Scripts Clients Installation
#### Windows
1. **Clone the Repository**

   ```
   #Download the repository or clone it
   git clone https://github.com/evaristorivi/busylight-evaristorivi
   cd busylight-evaristorivi\client-scripts\windows\
2. **Run Installation Script**
   ```
   powershell -ExecutionPolicy Bypass -File .\install.ps1
This script installs all necessary dependencies and sets up a scheduled task to automate the script execution.

Note: Ensure to run PowerShell as Administrator.

#### macOS Installation
There is no installation script at the moment. But you can automate it yourself with LaunchAgents or Automator.
##### Requirements
- **Python 3.x**: Ensure Python 3.x is installed on your system.
- **Pip**: Python package manager for installing dependencies.

   ```
   git clone https://github.com/evaristorivi/busylight-evaristorivi
   cd busylight-evaristorivi/client-scripts/macOS/NEWS/
   # or
   cd busylight-evaristorivi/client-scripts/macOS/LEGACY/
   pip install -r requirements.txt
   python3 mic-in-use_macOS-News.py

busylight-evaristorivi/client-scripts/macOS/NEWS is for current macOS as sonoma.

busylight-evaristorivi/client-scripts/macOS/LEGACY has been tested on el capitan.

###  [Shutdown Script - Optional]
The leds-off_Windows_and_macOS.py script is intended to turn off the LED lights when the system is shut down. It can be configured to run automatically when the user logs off.

This is optional as the API server will turn off the lights outside of the configured schedule anyway.


## License
This project is licensed under the MIT License - see the LICENSE file for details.