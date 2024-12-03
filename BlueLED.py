#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

# Set up the GPIO mode and pin
LED_PIN = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

try:
    while True:
        GPIO.output(LED_PIN, GPIO.HIGH)  # Turn LED on
        time.sleep(5)                    # Wait for 5 seconds
        GPIO.output(LED_PIN, GPIO.LOW)   # Turn LED off
        time.sleep(5)                    # Wait for 5 seconds
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()  # Clean up GPIO settings
