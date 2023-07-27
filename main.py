import time
import network
import socket
import machine
import onewire
import ds18x20
import credentials
import utime
from bmp085 import BMP180



# wifi should be disabled only for debugging
ena_wifi = True

# select sensor and interval in seconds
# DS18x20
ena_ds18x20 = True
int_ds18x20 = 60
pin_ds18x20 = 13

# Pulse Counter (for RPM)
ena_rev = False
pin_rev = 5
# simple filter (upper limit, lower limit, average) all in Hz
ul_rev = 80
ll_rev = 5


# BMP180 for pressure
ena_bmp180 = True
int_bmp180 = 120
pin_sda = 4
pin_scl = 5

# you signalk server here
#sk_server = "192.168.2.47"
sk_server = "10.10.10.1"

# needs to be defined as UDP input in SignalK server
sk_udp_port = 20222

source_prefix = "ESMSensor_Helm"

debug = False


# init delay to give uploader a chance
print("Boot delay active")
time.sleep(5)

# declarations
last_readout_DS1820 = 0
last_readout_BMP180 = 0
last_readout_dev = 0
last_status = 0
pulse_count = 0
sock = None

def pulse_callback(p):
    # this is the callback from the pulse counter interrupt
    global pulse_count
    pulse_count += 1

def rev_timer_callback(t):
    global pulse_count, last_readout_rev

    # boundary filter
    if pulse_count < ll_rev:
        pulse_count = 0

    if pulse_count < ul_rev:
        # only sends a value if it is below the upper limit. else drop the data
        sk_transmit(source_prefix + "_rev", "propulsion.main.revolutions", str(pulse_count), sk_udp_port)
        sk_transmit(source_prefix + "_rev", "propulsion.main.rpm", str(pulse_count * 60), sk_udp_port)

    pulse_count = 0
    last_readout_rev = current_time

def sk_transmit(source: str, path: str, value: str, port):
    global ena_wifi, sock
    SignalK = '{"updates": [{"$source": "'+source+'","values":[ {"path":"'+path+'","value":' + value+ '}]}]}'

    if debug: print("Sending: ", SignalK)
    if ena_wifi:
        # Only create a new socket if one doesn't exist
        if sock is None:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(SignalK.encode(), (sk_server, sk_udp_port))


def get_uptime():
    millis = utime.ticks_ms()
    minutes = millis / 60000
    return minutes

## main
# connect to wifi
if ena_wifi:
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
    ds_pin = machine.Pin(pin_ds18x20)
    ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
    roms = ds_sensor.scan()
    if debug: print('Found DS devices: ', roms)

if ena_rev:
    pulse_pin = machine.Pin(pin_rev, machine.Pin.IN)
    # Attach the callback function to the pin
    pulse_pin.irq(trigger=machine.Pin.IRQ_RISING, handler=pulse_callback)

    timer = machine.Timer(0)
    timer.init(period=1000, mode=machine.Timer.PERIODIC, callback=rev_timer_callback)

if ena_bmp180:
    i2c = machine.I2C(sda=machine.Pin(pin_sda), scl = machine.Pin(pin_scl))
    bmp = BMP180(i2c)
    bmp.oversample = 3
    bmp.sealevel = 101325


while True:
    # main loop
    current_time = utime.ticks_ms()
    if utime.ticks_diff(current_time, last_status) >= 10 * 1000:
        if ena_wifi:
            sk_transmit(source_prefix+"_status","sensor.rssi", str(sta_if.status()), sk_udp_port)
        sk_transmit(source_prefix + "_status", "sensor.uptime", str(get_uptime()), sk_udp_port)
        last_status = current_time

    if ena_bmp180:
        p: int = 0
        if utime.ticks_diff(current_time, last_readout_BMP180) >= int_bmp180 * 1000:
            p = bmp.pressure * 100 # needs to be in pascal
            sk_transmit(source_prefix + "_BMP", "environment.outside.pressure", str(p), sk_udp_port)
            last_readout_BMP180 = current_time

    if ena_ds18x20:
        if utime.ticks_diff(current_time, last_readout_DS1820) >= int_ds18x20 * 1000:
            i = 0
            ds_sensor.convert_temp()
            time.sleep(0.5)
            for rom in roms:
                # read temperature and convert to Kelvin
                a = ds_sensor.read_temp(rom) + 273.15
                sk_transmit(source_prefix+"_DS18B20_S"+str(i), "environment.temperature.outside", str(a), sk_udp_port)
                i +=1
            last_readout_DS1820 = current_time

