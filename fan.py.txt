#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

# Set up the GPIO mode and pin
FAN_PIN = 5
GPIO.setmode(GPIO.BCM)
GPIO.setup(FAN_PIN, GPIO.OUT)

try:
    while True:
        GPIO.output(FAN_PIN, GPIO.HIGH)  # Turn fan on
        time.sleep(10)                   # Wait for 10 seconds
        GPIO.output(FAN_PIN, GPIO.LOW)   # Turn fan off
        time.sleep(10)                   # Wait for 10 seconds
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()  # Clean up GPIO settings
