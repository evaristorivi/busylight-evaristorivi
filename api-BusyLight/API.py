# ---------------------------------------------------------------------------------------
# Project: BusyLight API
# Author: Evaristo R. Rivieccio Vega - SysAdmin
# GitHub: https://github.com/evaristorivi
# LinkedIn: https://www.linkedin.com/in/evaristorivieccio/
# Web: https://www.evaristorivieccio.es/
# ---------------------------------------------------------------------------------------
# Description:
# This API controls a Waveshare RGB LED HAT, designed to function as a BusyLight indicator.
# It supports multiple lighting modes, including the ability to set different colors (green, red, orange) 
# and adjust the intensity. The API can operate in full mode or shared mode (left and right sides). 
# It also includes scheduling functionality to enforce operating hours and can respond to system status 
# requests such as CPU temperature.
#
# Key features:
# - Control the color and intensity of the LED strip.
# - Split the control between the left and right halves of the strip (in shared mode).
# - Schedule operation hours with automatic shutdown outside of operating times.
# - Monitor CPU temperature.
#
# Usage:
# - Send POST requests to "/API/signal" to control the LED colors and intensity.
# - Send POST requests to "/API/off" to turn off all or part of the LED strip.
# - Use GET requests to "/API/temperature" to retrieve the current CPU temperature.
# API Doc:
# http://API.IP...:5000/docs
# http://API.IP...:5000/redoc
# ---------------------------------------------------------------------------------------

from fastapi import FastAPI, HTTPException
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel
from typing import Optional
import psutil  # Library for system monitoring
from rpi_ws281x import Adafruit_NeoPixel, Color
from datetime import datetime, time
import threading
import time as t

# Configuration API
DEFAULT_INTENSITY = 20  # Default intensity percentage (0-100)
CONTROL_INTENSITY = True  # Set to False to ignore intensity settings from the API
VERSION = '1.2.0'

# Schedule configuration
USE_SCHEDULE = True  # Set to True to enforce the schedule
START_TIME = time(8, 0)  # Start time in the format (hour, minute)
END_TIME = time(17, 0)   # End time in the format (hour, minute)
WEEKDAYS = [0, 1, 2, 3, 4]  # Days of the week to apply the schedule (0 = Monday, 4 = Friday)

# Orientation configuration
INVERT_POSITION = False  # Set to True if the device is mounted upside-down

#################################################################
# Configuration values
LED_COUNT = 32        # Number of LED pixels
LED_PIN = 18          # GPIO pin connected to the pixels (must support PWM)
LED_FREQ_HZ = 800000  # LED signal frequency in Hertz (usually 800kHz)
LED_DMA = 10          # DMA channel to use for generating signal
LED_BRIGHTNESS = 255  # Set to 0 for the darkest and 255 for the brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)

app = FastAPI()

# Create NeoPixel object with the appropriate configuration.
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)

# Initialize the library (must be called once before other functions).
strip.begin()

# Data model for the signal
class Signal(BaseModel):
    color: Optional[str] = None  # Color in the format "green", "red", "orange", or "off"
    half: Optional[str] = None  # "left", "right", or None for all
    intensity: Optional[int] = DEFAULT_INTENSITY  # Intensity in percentage (0-100). Default is 100%

    class Config:
        schema_extra = {
            "example": {
                "color": "green",
                "half": "left",
                "intensity": 75
            }
        }

# Data model for the 'off' endpoint
class OffRequest(BaseModel):
    half: Optional[str] = None  # "left", "right", or None for all

# Function to get the CPU temperature
def get_temperature():
    temp = psutil.sensors_temperatures()
    if 'cpu_thermal' in temp:
        return temp['cpu_thermal'][0].current
    return None

# Function to get color based on a string
def get_color(color_str: str, intensity: Optional[int] = DEFAULT_INTENSITY) -> Color:
    colors = {
        "green": Color(0, 255, 0),
        "red": Color(255, 0, 0),
        "orange": Color(255, 69, 0)
    }
    
    if color_str.lower() not in colors:
        raise HTTPException(status_code=400, detail="Unsupported color. Use 'green', 'red', or 'orange'.")

    color = colors[color_str.lower()]
    
    if intensity < 0 or intensity > 100:
        raise HTTPException(status_code=400, detail="Intensity must be between 0 and 100")
    
    # Adjust RGB values according to the intensity
    factor = intensity / 100
    red = int((color >> 16 & 0xFF) * factor)
    green = int((color >> 8 & 0xFF) * factor)
    blue = int((color & 0xFF) * factor)
    
    return Color(red, green, blue)

# Function to set the color for the left half of the LED strip
def set_left_square(color):
    rows = 4  # Number of rows
    cols = 8  # Number of columns
    for row in range(rows):
        for col in range(0, cols // 2):  # LEDs in columns 0 to 3
            index = row * cols + col
            strip.setPixelColor(index, color)
    strip.show()

# Function to set the color for the right half of the LED strip
def set_right_square(color):
    rows = 4  # Number of rows
    cols = 8  # Number of columns
    for row in range(rows):
        for col in range(cols // 2, cols):  # LEDs in columns 4 to 7
            index = row * cols + col
            strip.setPixelColor(index, color)
    strip.show()

# Function to set the color for all LEDs
def set_all_square(color):
    for i in range(LED_COUNT):
        strip.setPixelColor(i, color)
    strip.show()

# Function to turn off all LEDs
def turn_off_leds():
    set_all_square(Color(0, 0, 0))  # Set all LEDs to black/off

# Function to check if the current time is within the allowed schedule
def is_within_schedule():
    if not USE_SCHEDULE:
        return True  # If schedule enforcement is disabled, always return True

    now = datetime.now()
    current_time = now.time()
    current_day = now.weekday()
    
    # Check if today is within the allowed weekdays and the current time is within the allowed range
    return current_day in WEEKDAYS and START_TIME <= current_time <= END_TIME

# Background thread function to check schedule every minute
def schedule_checker():
    while True:
        if not is_within_schedule():
            turn_off_leds()
        t.sleep(60)  # Check every minute

# Start the schedule checker thread
threading.Thread(target=schedule_checker, daemon=True).start()

# Route to receive signals and control LEDs
@app.post("/API/signal", summary="Control the LED strip", description="""
Controls an LED strip based on the received signal. You can specify the color, the half of the strip to illuminate, and the intensity of the color.

- **color**: The color to set. Supported values are 'green', 'red', 'orange', or 'off' to turn off LEDs.
- **half**: Which half of the strip to illuminate or turn off. Options are 'left', 'right', or None for the entire strip. Note that 'left' and 'right' are based on the orientation of the device. If the USB charging port is facing downwards, 'left' will illuminate the left half from that perspective. If the device is mounted upside-down, set the `INVERT_POSITION` variable to `True` to reverse these sides.
- **intensity**: (Optional) The intensity of the color, in percentage (0-100). Default is 100%. 
  - **Note**: If the server is configured to ignore intensity changes (`CONTROL_INTENSITY` is False), the specified intensity will be ignored, and the default intensity will be used.

**Examples**:
1. To illuminate the left half with green color and 75% intensity (with USB charging port facing downwards):
   {
     "color": "green",
     "half": "left",
     "intensity": 75
   }

2. To illuminate the entire strip with red color with default intensity:
   {
     "color": "red"
   }

3. To illuminate the right half with green color with the default intensity (with USB charging port facing downwards):
   {
     "color": "green",
     "half": "right"
   }

4. To turn off the left half of the LEDs:
   {
     "color": "off",
     "half": "left"
   }

5. To turn off the entire strip of LEDs:
   {
     "color": "off"
   }
""")
async def receive_signal(signal: Signal):
    if not is_within_schedule():
        raise HTTPException(status_code=403, detail="Outside of operating hours")

    if signal.color and signal.color.lower() == "off":
        if signal.half == "left":
            set_left_square(Color(0, 0, 0))
        elif signal.half == "right":
            set_right_square(Color(0, 0, 0))
        elif signal.half is None:  # If "half" is not specified, turn off the entire strip
            turn_off_leds()
        else:
            raise HTTPException(status_code=400, detail="Unsupported half value for 'off'")
    else:
        if not CONTROL_INTENSITY:
            # Inform client that intensity control is disabled and use default intensity
            color = get_color(signal.color, DEFAULT_INTENSITY)
        else:
            color = get_color(signal.color, signal.intensity)
        
        # Adjust for inverted position
        if INVERT_POSITION:
            if signal.half == "left":
                set_right_square(color)
            elif signal.half == "right":
                set_left_square(color)
            elif signal.half is None:  # If "half" is not specified, illuminate the entire strip
                set_all_square(color)
            else:
                raise HTTPException(status_code=400, detail="Unsupported half value")
        else:
            if signal.half == "left":
                set_left_square(color)
            elif signal.half == "right":
                set_right_square(color)
            elif signal.half is None:  # If "half" is not specified, illuminate the entire strip
                set_all_square(color)
            else:
                raise HTTPException(status_code=400, detail="Unsupported half value")
    
    return {"status": "success", "message": f"LEDs {signal.half or 'all'} set to {signal.color} with {signal.intensity if CONTROL_INTENSITY else DEFAULT_INTENSITY}% intensity"}

# Route to get the current temperature
@app.get("/API/temperature", summary="Get current CPU temperature", description="""
Returns the current CPU temperature.

**Response**:
- Returns a JSON object with the temperature in Celsius. If the temperature cannot be determined, returns a 500 error.

Example:
{ "temperature": 45.0 }
""")
async def get_temperature_endpoint():
    temp = get_temperature()
    if temp is None:
        raise HTTPException(status_code=500, detail="Unable to retrieve temperature")
    return {"temperature": temp}

# Route to turn off LEDs (for control purposes)
@app.post("/API/off", summary="Turn off LEDs", description="""
Turns off LEDs on the strip. You can specify which part of the strip to turn off.

- **half**: Which half of the strip to turn off. Options are 'left', 'right', or None for the entire strip. 

**Examples**:
1. To turn off the left half of the LEDs:
   {
     "half": "left"
   }

2. To turn off the entire strip of LEDs:
   {}
""")
@app.post("/API/off", summary="Turn off LEDs", description="""
Turns off LEDs on the strip. You can specify which part of the strip to turn off.

- **half**: Which half of the strip to turn off. Options are 'left', 'right', or None for the entire strip. 

**Examples**:
1. To turn off the left half of the LEDs:
   {
     "half": "left"
   }

2. To turn off the entire strip of LEDs:
   {}
""")
async def turn_off(request: OffRequest):
    if not is_within_schedule():
        raise HTTPException(status_code=403, detail="Outside of operating hours")
    
    # Apaga solo la mitad izquierda
    if request.half == "left":
        set_left_square(Color(0, 0, 0))  # Apaga LEDs de la izquierda

    # Apaga solo la mitad derecha
    elif request.half == "right":
        set_right_square(Color(0, 0, 0))  # Apaga LEDs de la derecha

    # Apaga todos los LEDs si no se especifica `half`
    elif request.half is None:
        turn_off_leds()  # Apaga todos los LEDs

    else:
        raise HTTPException(status_code=400, detail="Unsupported half value for 'off'")

    return {"status": "success", "message": f"LEDs {request.half or 'all'} turned off"}

# Customize the OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="BusyLight - evaristorivi",
        version=VERSION,
        description="Control a Waveshare RGB LED HAT as a BusyLight. Suitable for 1 or 2 offices simultaneously.",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

# Assign the customized OpenAPI schema to the application
app.openapi = custom_openapi
