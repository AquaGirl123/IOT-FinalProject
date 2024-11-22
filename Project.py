#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
import threading
import ADC0832
import os
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import config
import json

FAN = 5 # HVAC
RED_LED = 20 # WaterPump
BLUE_LED = 21 # Grow lights - lighting when its dark

GPIO.setmode(GPIO.BCM)
GPIO.setup(FAN, GPIO.OUT)
GPIO.setup(RED_LED, GPIO.OUT)
GPIO.setup(BLUE_LED, GPIO.OUT)

CLIENT_ID = 'projectIOT'
TOPIC = 'champlain/sensor/10/data'

# ThingBoard
THINGSBOARD_HOST = "demo.thingsboard.io"
THINGSBOARD_TOKEN = 'rtKIlzb1Ep5pb8FtqWMS'
TB_TOPIC = 'v1/devices/me/telemetry'

# MQTT Client Setup for ThingsBoard
client = mqtt.Client()
client.username_pw_set(THINGSBOARD_TOKEN)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to ThingsBoard successfully.")
    else:
        print(f"Connection failed with code {rc}")

# Configure the MQTT client
myMQTTClient = AWSIoTMQTTClient(config.CLIENT_ID)
myMQTTClient.configureEndpoint(config.AWS_HOST, config.AWS_PORT)
myMQTTClient.configureCredentials(config.AWS_ROOT_CA, config.AWS_PRIVATE_KEY, config.AWS_CLIENT_CERT)
myMQTTClient.configureOfflinePublishQueueing(config.OFFLINE_QUEUE_SIZE)
myMQTTClient.configureDrainingFrequency(config.DRAINING_FREQ)
myMQTTClient.configureConnectDisconnectTimeout(config.CONN_DISCONN_TIMEOUT)
myMQTTClient.configureMQTTOperationTimeout(config.MQTT_OPER_TIMEOUT)

# Thresholds for FAN
TEMP_THRESHOLD = 25.0 # Fan is activated if higher than 25

# Use ADC0832converter 
# Water pump (RED_LED) is activated for 5 seconds if moisture falls below 150
SOIL_MOISTURE_THRESHOLD = 150 

# Use ADC0832 (0-255, low = dark)
# Grow lights (BLUE_LED) turn on if the light intensity is below 100
LIGHT_THRESHOLD = 100

# DS18B20 sesnor 
TEMPERATURE_SENSOR = "28-3c01b556342e"  

# Initialize ADC0832
ADC0832.setup()

# DS18B20 sensor
# Reads the temperature from a DS18B20 sensor file
# Converts readings to Celsius
def read_temp_sensor(sensor_id):
    try:
        with open(f"/sys/bus/w1/devices/{sensor_id}/w1_slave") as tfile:
            text = tfile.read()
        second_line = text.split("\n")[1]
        temperature_data = second_line.split(" ")[9]
        temperature = float(temperature_data[2:]) / 1000
        return temperature
    except FileNotFoundError:
        print(f"Temperature sensor {sensor_id} not found.")
        return None


# Soil Moisture 
# Reads the moisture level using ADC0832. Higher ADC values mean drier soil.
def read_soil_moisture():
    adc_value = ADC0832.getADC(0) # channel 0
    return 255 - adc_value  # Higher value = drier soil

# Photoresister Module
# Reads the light level using ADC0832. Lower values mean darker conditions
def read_light_intensity():
    return ADC0832.getADC(1)  # channel 1

# Fan
# Activates the fan if the temperature exceeds the TEMP_THRESHOLD which is 25
def control_fan(temp):
    if temp > TEMP_THRESHOLD:
        GPIO.output(FAN, GPIO.HIGH)
        time.sleep(5)
        GPIO.output(FAN, GPIO.LOW)

# RED LED - Water pump
# Activates the water pump (RED_LED) if soil moisture falls below the SOIL_MOISTURE_THRESHOLD which is 150
def control_water_pump(moisture):
    if moisture < SOIL_MOISTURE_THRESHOLD:
        GPIO.output(RED_LED, GPIO.HIGH)
        time.sleep(5)
        GPIO.output(RED_LED, GPIO.LOW)

# Photoresister 
# Turns the grow lights on/off based on light intensity
def control_grow_lights(light_level):
    if light_level < LIGHT_THRESHOLD:
        GPIO.output(BLUE_LED, GPIO.HIGH) # light on
    else:
        GPIO.output(BLUE_LED, GPIO.LOW) # light off

# 
def actuator_manual_control():
    """Simulate manual actuator control from a dashboard."""
    print("hi")
    while True:
        command = input("Enter command (fan/pump/light/exit): ").strip().lower()
        if command == "fan":
            GPIO.output(FAN, not GPIO.input(FAN))
            print("Fan toggled.")
        elif command == "pump":
            GPIO.output(RED_LED, not GPIO.input(RED_LED))
            print("Water pump toggled.")
        elif command == "light":
            GPIO.output(BLUE_LED, not GPIO.input(BLUE_LED))
            print("Grow light toggled.")
        elif command == "exit":
            break

def main():
    try:
        # Initialize MQTT connection
        print("Initializing MQTT connection...")
        myMQTTClient.connect()

        threading.Thread(target=actuator_manual_control, daemon=True).start()

        while True:
            temp = read_temp_sensor(TEMPERATURE_SENSOR)
            moisture = read_soil_moisture()
            light_level = read_light_intensity()

            print(f"Temperature: {temp:.2f} °C")
            print(f"Soil Moisture: {moisture}")
            print(f"Light Intensity: {light_level}")

            if temp:
                control_fan(temp)
            control_water_pump(moisture)
            control_grow_lights(light_level)

            # Publish sensor data
            message = {
                "temperature": temp,
                "moisture": moisture,
                "light": light_level,
                "timestamp": time.time()
            }
            myMQTTClient.publish(config.TOPIC, json.dumps(message), 1)

            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting program...")
    finally:
        GPIO.cleanup()
        ADC0832.destroy()
        myMQTTClient.disconnect()

if __name__ == "__main__":
    main()