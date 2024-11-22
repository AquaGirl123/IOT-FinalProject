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
RGB_LED_RED = 20 # WaterPump
RGB_LED_GREEN = 6 # WaterPump
RGB_LED_BLUE = 19 # WaterPump
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

# DS18B20 sensor 
TEMPERATURE_SENSOR = "28-3c01b556342e"  

# Initialize ADC0832
ADC0832.setup()

def get_user_inputs():
    """Prompt user to input thresholds."""
    temp_threshold = float(input("Enter the temperature threshold for the fan (°C): "))
    soil_moisture_threshold = int(input("Enter the soil moisture threshold for the water pump: "))
    light_threshold = int(input("Enter the light intensity threshold for grow lights: "))
    return temp_threshold, soil_moisture_threshold, light_threshold

# DS18B20 sensor
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

def read_soil_moisture():
    adc_value = ADC0832.getADC(0) # channel 0
    return 255 - adc_value  # Higher value = drier soil

def read_light_intensity():
    return ADC0832.getADC(1)  # channel 1

def control_fan(temp, temp_threshold):
    if temp > temp_threshold:
        GPIO.output(FAN, GPIO.HIGH)
        time.sleep(5)
        GPIO.output(FAN, GPIO.LOW)

def control_water_pump(moisture, soil_moisture_threshold):
    if moisture < soil_moisture_threshold:
        GPIO.output(RED_LED, GPIO.HIGH)
        time.sleep(5)
        GPIO.output(RED_LED, GPIO.LOW)

def control_grow_lights(light_level, light_threshold):
    if light_level < light_threshold:
        GPIO.output(BLUE_LED, GPIO.HIGH) # light on
    else:
        GPIO.output(BLUE_LED, GPIO.LOW) # light off

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
    temp_threshold, soil_moisture_threshold, light_threshold = get_user_inputs()
    
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
                control_fan(temp, temp_threshold)
            control_water_pump(moisture, soil_moisture_threshold)
            control_grow_lights(light_level, light_threshold)

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
