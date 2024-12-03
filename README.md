# IOT-FinalProject
Title: The Smart Greenhouse Controller 

Team: Jade and Emma

Introduction: This project aims to implement a smart greenhouse controller using a Raspberry Pi. It is designed to monitor and manage Greenhouse conditions, such as soil mosisture, temperature changes, light intensity etc. This system uses AWS IoT Core for data management and ThingsBoard for a user friendly dashboard.

Solution Overview: 
The Smart Greenhouse Controller uses a Raspberry Pi to monitor temperature, soil moisture, and light in a greenhouse, automatically activating a water pump, fan, and grow lights as needed. Users can view real-time data via the ThingsBoard dashboard, with data securely managed through AWS IoT Core and DynamoDB.
![image](https://github.com/user-attachments/assets/7c12fcfd-d0e7-42f6-afc1-f6a7d7b53577)

List of components:
- Raspberry Pi
- Temperature sensor - DS18B20
- Light intensity - Photoresistor
- Soil moisture
- Red Led - water pump (actuator)
- Fan - HVAC system (actuator)
- Sensor data
- 2 LEDS (actuator)
- Breadboard

Software:
- AWS IoT core for secure data transmission
- ThingsBoard for web-based monitoring and control dashboard
- Python Libaries for actuator control and sensor readings

Implementation
- Install Hardware --> connect sensors and actuators to Raspberry Pi
- Test Hardware --> ensure all sensors and actuators work correctly
- Develop scripts
- Ability to set threshold in terminal at runtime 
  
- AWS
![image](https://github.com/user-attachments/assets/3945bb89-1c81-40d0-bce3-467d3ed316e3)
![image](https://github.com/user-attachments/assets/e82874f1-6a22-4c9d-b2e6-2ed7b9ca1a71)

- ThingsBoard
![image](https://github.com/user-attachments/assets/1b8df954-538d-499c-9e0c-845722bd24b2)

  


