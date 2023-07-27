# MicroPython-SignalK-Sensors
Use Micropython (i.e. on ESP32) to send sensor data to a SignalK server (on a Boat)

This code runs on any Micropython device. It reads out hooked up sensors and sends the values to a SignalK server.

Feel free to adapt to your needs.

Please adapt credentials.py to your needs.
You have to set up a SignalK server on your boat. I use a Raspberry Pi with OpenPlotter and SignalK.
Create a data port in SignalK. I use port 20222 UDP and let my sensors send data to this port.
