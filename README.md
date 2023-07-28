# Yacht Sensor Module with ESP8266

This repository contains the code for a yacht sensor module based on the ESP8266 microcontroller and MicroPython. The sensor module is equipped with various sensors to monitor the yacht's environment and engine.

## Features

- DS18x20 temperature sensor support.
- BMP180 pressure sensor support.
- Pulse counter for RPM measurements.
- WiFi connectivity to transmit sensor data.
- Sensor data transmission to a SignalK server over UDP.
- Uptime tracking.
- Auto-reboot if WiFi connection is not established within 5 minutes.

## Hardware Requirements

- ESP8266 microcontroller.
- DS18x20 temperature sensor.
- BMP180 pressure sensor.
- Pulse sensor for RPM measurements.
- ADS1115 ADC (coming up).

## Setup and Installation

1. Clone this repository.
2. Install MicroPython on your ESP8266.
3. Upload the Python files to your ESP8266.
4. Update the `credentials.py` file with your WiFi SSID and password.
5. Update the `sk_server` variable in the main Python file with the IP address of your SignalK server.
6. Connect your sensors to the ESP8266 as described in the 'Sensor Connections' section below.

## Sensor Connections

- DS18x20: Connect to pin 13.
- Pulse Sensor: Connect to pin of choice. Be sure to adapt it in the source.
- BMP180: Connect SDA to pin 4, and SCL to pin 5.

## Usage

Power up the ESP8266. It will automatically connect to the WiFi network, start reading from the sensors, and transmit the sensor data to the SignalK server.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.



