#!/usr/bin/python
'''*****************************************************************************************************************
    Pi Temperature Station
********************************************************************************************************************'''

from __future__ import print_function

import datetime
import os
import sys
import time
from urllib import urlencode

import urllib2
from sense_hat import SenseHat

#from config import Config
from ubidots import ApiClient          # Ubidots Library

# ============================================================================
# Constants
# ============================================================================
# specifies how often to measure values from the Sense HAT (in minutes)
MEASUREMENT_INTERVAL = 10  # minutes
# Set to False when testing the code and/or hardware
# Set to True to enable upload of weather data to Weather Underground
# WEATHER_UPLOAD = True
# the weather underground URL used to upload weather data
# WU_URL = "http://weatherstation.wunderground.com/weatherstation/updateweatherstation.php"
# some string constants
SINGLE_HASH = "#"
HASHES = "########################################"
SLASH_N = "\n"

# Setup Variables for Ubidots
dS = None

# constants used to display an up and down arrows plus bars
# modified from https://www.raspberrypi.org/learning/getting-started-with-the-sense-hat/worksheet/
# set up the colours (blue, red, empty)
b = [0, 0, 255]  # blue
r = [255, 0, 0]  # red
e = [0, 0, 0]  # empty
# create images for up and down arrows
arrow_up = [
    e, e, e, r, r, e, e, e,
    e, e, r, r, r, r, e, e,
    e, r, e, r, r, e, r, e,
    r, e, e, r, r, e, e, r,
    e, e, e, r, r, e, e, e,
    e, e, e, r, r, e, e, e,
    e, e, e, r, r, e, e, e,
    e, e, e, r, r, e, e, e
]
arrow_down = [
    e, e, e, b, b, e, e, e,
    e, e, e, b, b, e, e, e,
    e, e, e, b, b, e, e, e,
    e, e, e, b, b, e, e, e,
    b, e, e, b, b, e, e, b,
    e, b, e, b, b, e, b, e,
    e, e, b, b, b, b, e, e,
    e, e, e, b, b, e, e, e
]
bars = [
    e, e, e, e, e, e, e, e,
    e, e, e, e, e, e, e, e,
    r, r, r, r, r, r, r, r,
    r, r, r, r, r, r, r, r,
    b, b, b, b, b, b, b, b,
    b, b, b, b, b, b, b, b,
    e, e, e, e, e, e, e, e,
    e, e, e, e, e, e, e, e
]


def c_to_f(input_temp):
    # convert input_temp from Celsius to Fahrenheit
    return (input_temp * 1.8) + 32


def get_cpu_temp():
    # 'borrowed' from https://www.raspberrypi.org/forums/viewtopic.php?f=104&t=111457
    # executes a command at the OS to pull in the CPU temperature
    res = os.popen('vcgencmd measure_temp').readline()
    return float(res.replace("temp=", "").replace("'C\n", ""))


# use moving average to smooth readings
def get_smooth(x):
    # do we have the t object?
    if not hasattr(get_smooth, "t"):
        # then create it
        get_smooth.t = [x, x, x]
    # manage the rolling previous values
    get_smooth.t[2] = get_smooth.t[1]
    get_smooth.t[1] = get_smooth.t[0]
    get_smooth.t[0] = x
    # average the three last temperatures
    xs = (get_smooth.t[0] + get_smooth.t[1] + get_smooth.t[2]) / 3
    return xs


def get_temp():
    # ====================================================================
    # Unfortunately, getting an accurate temperature reading from the
    # Sense HAT is improbable, see here:
    # https://www.raspberrypi.org/forums/viewtopic.php?f=104&t=111457
    # so we'll have to do some approximation of the actual temp
    # taking CPU temp into account. The Pi foundation recommended
    # using the following:
    # http://yaab-arduino.blogspot.co.uk/2016/08/accurate-temperature-reading-sensehat.html
    # ====================================================================
    # First, get temp readings from both sensors
    t1 = sense.get_temperature_from_humidity()
    t2 = sense.get_temperature_from_pressure()
    # t becomes the average of the temperatures from both sensors
    t = (t1 + t2) / 2
    # Now, grab the CPU temperature
    t_cpu = get_cpu_temp()
    # Calculate the 'real' temperature compensating for CPU heating
    t_corr = t - ((t_cpu - t) / 1.5)
    # Finally, average out that value across the last three readings
    t_corr = get_smooth(t_corr)
    # convoluted, right?
    # Return the calculated temperature
    return t_corr

# Function to verify if the variable exists or not in your Ubidots account
def getVarbyNames(varName,dS):
    for var in dS.get_variables():
        if var.name == varName:
            return var
    return None


temp_ds = None
humidity = None
pressure = None

def main():
    global last_temp

    # initialize the lastMinute variable to the current time to start
    last_minute = datetime.datetime.now().minute
    # on startup, just use the previous minute as lastMinute
    last_minute -= 1
    if last_minute == 0:
        last_minute = 59

    # ========================================================
    # Code to connect a Ubidots
    # ========================================================
    try:
        api = ApiClient("A1E-baee7da49300eee20eb148229cf1ead45d71") # Connect to Ubidots. Don't forget to put your own apikey
        #api = ApiClient("A1E-6ea6e644f236c649a0a43105e276658540d9") # Connect to Ubidots. Don't forget to put your own apikey

        print("Inizializza Ubidots")

        for curDs in api.get_datasources():                        # Check if there's any Data Source with the name AirPi
            print("Inizializza Ubidots for get_datasources")
            if curDs.name == "PiSenseHat":
                dS = curDs
                break

        print("Inizializza Ubidots get_datasources")

        if dS is None:
            dS = api.create_datasource({"name":"PiSenseHat"})            # If doesn't exist it'll create a Data Source with the name Airpi

        print("Inizializza Ubidots dS")

        temp_ds = getVarbyNames("temp",dS)
        if temp_ds is None:
            temp_ds = dS.create_variable({"name": "Temperature", "unit": "C"})    #Create a new Variable for temperature

        print("Inizializza Ubidots temp_c")

        humidity_ds = getVarbyNames("humidity",dS)
        if humidity_ds is None:
            humidity_ds = dS.create_variable({"name": "Humidity","unit": "%"}) # Create a new Variable for humidity

        print("Inizializza Ubidots humidity")

        pressure_ds = getVarbyNames("pressure",dS)
        if pressure_ds is None:
            pressure_ds = dS.create_variable({"name": "Pressure","unit": "hPa"}) # Create a new Variable for temperature

        print("Ubidots Initialization complete")
    except:
        print("Can't connect to Ubidots")
        return

    # infinite loop to continuously check weather values
    while 1:
        # The temp measurement smoothing algorithm's accuracy is based
        # on frequent measurements, so we'll take measurements every 5 seconds
        # but only upload on measurement_interval
        current_second = datetime.datetime.now().second
        # are we at the top of the minute or at a 5 second interval?
        if (current_second == 0) or ((current_second % 5) == 0):
            # ========================================================
            # read values from the Sense HAT
            # ========================================================
            # Calculate the temperature. The get_temp function 'adjusts' the recorded temperature adjusted for the
            # current processor temp in order to accommodate any temperature leakage from the processor to
            # the Sense HAT's sensor. This happens when the Sense HAT is mounted on the Pi in a case.
            # If you've mounted the Sense HAT outside of the Raspberry Pi case, then you don't need that
            # calculation. So, when the Sense HAT is external, replace the following line (comment it out  with a #)
            calc_temp = get_temp()
            # with the following line (uncomment it, remove the # at the line start)
            # calc_temp = sense.get_temperature_from_pressure()
            # or the following line (each will work)
            # calc_temp = sense.get_temperature_from_humidity()
            # ========================================================
            # At this point, we should have an accurate temperature, so lets use the recorded (or calculated)
            # temp for our purposes
            temp_c = round(calc_temp, 1)
            temp_f = round(c_to_f(calc_temp), 1)
            humidity = round(sense.get_humidity(), 0)
            # convert pressure from millibars to inHg before posting
            pressure = round(sense.get_pressure(), 1) # * 0.0295300
            print("Temp: %sF (%sC), Pressure: %s mbar, Humidity: %s%%" % (temp_f, temp_c, pressure, humidity))

            # get the current minute
            current_minute = datetime.datetime.now().minute
            # is it the same minute as the last time we checked?
            if current_minute != last_minute:
                # reset last_minute to the current_minute
                last_minute = current_minute
                # is minute zero, or divisible by 10?
                # we're only going to take measurements every MEASUREMENT_INTERVAL minutes
                if (current_minute == 0) or ((current_minute % MEASUREMENT_INTERVAL) == 0):
                    # get the reading timestamp
                    now = datetime.datetime.now()
                    print("\n%d minute mark (%d @ %s)" % (MEASUREMENT_INTERVAL, current_minute, str(now)))
                    # did the temperature go up or down?
                    if last_temp != temp_f:
                        if last_temp > temp_f:
                            # display a blue, down arrow
                            sense.set_pixels(arrow_down)
                        else:
                            # display a red, up arrow
                            sense.set_pixels(arrow_up)
                    else:
                        # temperature stayed the same
                        # display red and blue bars
                        sense.set_pixels(bars)
                    # set last_temp to the current temperature before we measure again
                    last_temp = temp_f

                    # Post values to Ubidots
                    temp_ds.save_value({'value':temp_c})
                    humidity_ds.save_value({'value':humidity})
                    pressure_ds.save_value({'value':pressure})

        # wait a second then check again
        # You can always increase the sleep value below to check less often
        time.sleep(1)  # this should never happen since the above is an infinite loop

    #print("Leaving main()")

# ============================================================================
# here's where we start doing stuff
# ============================================================================
#print(SLASH_N + HASHES)
#print(SINGLE_HASH, "Pi Weather Station                  ", SINGLE_HASH)
#print(SINGLE_HASH, "By John M. Wargo (www.johnwargo.com)", SINGLE_HASH)
#print(HASHES)

# make sure we don't have a MEASUREMENT_INTERVAL > 60
if (MEASUREMENT_INTERVAL is None) or (MEASUREMENT_INTERVAL > 60):
    print("The application's 'MEASUREMENT_INTERVAL' cannot be empty or greater than 60")
    sys.exit(1)

# ============================================================================
#  Read Weather Underground Configuration Parameters
# ============================================================================
#print("\nInitializing Weather Underground configuration")
#wu_station_id = Config.STATION_ID
#wu_station_key = Config.STATION_KEY
#if (wu_station_id is None) or (wu_station_key is None):
#    print("Missing values from the Weather Underground configuration file\n")
#    sys.exit(1)

# we made it this far, so it must have worked...
#print("Successfully read Weather Underground configuration values")
#print("Station ID:", wu_station_id)
# print("Station key:", wu_station_key)

# ============================================================================
# initialize the Sense HAT object
# ============================================================================
try:
    print("Initializing the Sense HAT client")
    sense = SenseHat()
    # sense.set_rotation(180)
    # then write some text to the Sense HAT's 'screen'
    sense.show_message("Init", text_colour=[255, 255, 0], back_colour=[0, 0, 255])
    # clear the screen
    sense.clear()
    # get the current temp to use when checking the previous measurement
    last_temp = round(c_to_f(get_temp()), 1)
    print("Current temperature reading:", last_temp)
except:
    print("Unable to initialize the Sense HAT library:", sys.exc_info()[0])
    sys.exit(1)

print("Initialization complete!")

# Now see what we're supposed to do next
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting application\n")
        sys.exit(0)
