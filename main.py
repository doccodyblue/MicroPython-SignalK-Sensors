import time
import network
import socket
import machine
import onewire
import ds18x20
import credentials
import utime

# select sensor and interval in seconds
ena_ds18x20 = True
int_ds18x20 = 10

sk_server = "192.168.2.47"

# needs to be defined as UDP input in SignalK server
sk_udp_port = 20222

source_prefix = "WirelessSensor"

debug = True

last_readout_DS1820 = 0
last_status = 0

if debug: print("Connected to WiFi\n")

def sk_transmit(source: str, path: str, value: str, port):
    SignalK = '{"updates": [{"$source": "'+source+'","values":[ {"path":"'+path+'","value":' + value+ '}]}]}'

    if debug: print("Sending: ", SignalK)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(SignalK.encode(), (sk_server, sk_udp_port))
    sock.close()

## main
# connect to wifi
if debug: print("Connecting to WiFi\n")
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect(credentials.ssid, credentials.password) # Connect to an AP

while not sta_if.isconnected():
    time.sleep(1)
    if debug: print("Waiting for Wifi...\n")
    pass


## init sensors

if ena_ds18x20:
    # DS18x20
    ds_pin = machine.Pin(4)
    ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
    roms = ds_sensor.scan()
    if debug: print('Found DS devices: ', roms)

while True:
    # main loop
    current_time = utime.ticks_ms()
    if utime.ticks_diff(current_time, last_status) >= 10 * 1000:
        sk_transmit(source_prefix+"_RSSI","sensor.rssi", str(sta_if.status()), sk_udp_port)
        last_status = current_time

    if ena_ds18x20:
        if utime.ticks_diff(current_time, last_readout_DS1820) >= int_ds18x20 * 1000:
            i = 0
            ds_sensor.convert_temp()
            time.sleep(1)
            for rom in roms:
                # read temperature and convert to Kelvin
                a = ds_sensor.read_temp(rom) + 273.15
                sk_transmit(source_prefix+"_DS18B20_S"+str(i), "environment.temperature.outside", str(a), sk_udp_port)
                i +=1
                print(a)
            last_readout_DS1820 = current_time




