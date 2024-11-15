#!/usr/bin/env python3
import os
import time
 
#----------------------------------------------------------------
#   Note:
#       ds18b20's data pin must be connected to pin7(GPIO4).
#----------------------------------------------------------------
# Reads temperature from sensor and prints to stdout
# id is the id of the sensor
def readSensor(id):
    try:
        with open(f"/sys/bus/w1/devices/{id}/w1_slave") as tfile:
            text = tfile.read()
        secondline = text.split("\n")[1]
        temperaturedata = secondline.split(" ")[9]
        temperature = float(temperaturedata[2:]) / 1000
        print(f"Sensor: {id} - Current temperature: {temperature:.3f} °C")
    except FileNotFoundError:
        print(f"Sensor {id} not found. Check the connection.")
 
# Reads temperature from all sensors found in /sys/bus/w1/devices/
# starting with "28-...
def readSensors():
    count = 0
    for file in os.listdir("/sys/bus/w1/devices/"):
        if file.startswith("28-"):
            readSensor(file)
            count += 1
    if count == 0:
        print("No sensor found! Check connection.")
 
# read temperature every second for all connected sensors
def loop():
    while True:
        readSensors()
        time.sleep(1)
 
# Nothing to cleanup
def destroy():
    pass
 
# Main starts here
if __name__ == "__main__":
    try:
        loop()
    except KeyboardInterrupt:
        destroy()
 