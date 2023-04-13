import os
import wifi
import ntp
import socketpool
import rtc
import mu_time


#   Environment Variables
SSID = os.getenv('CIRCUITPY_WIFI_SSID')
WIFI_PASSWORD = os.getenv('CIRCUITPY_WIFI_PASSWORD')


#   Connect to WiFi
try:
    wifi.radio.connect(ssid=SSID, password=WIFI_PASSWORD)
except ConnectionError:
    pass

while wifi.radio.ipv4_address == None:
    access_points = {}
    print('Looking for network')

    for network in wifi.radio.start_scanning_networks(start_channel=1, stop_channel=13):
        access_points[network.ssid] = {
            'ssid': network.ssid, 'channel': network.channel}
    wifi.radio.stop_scanning_networks()

    for ap in access_points.values():
        if wifi.radio.ipv4_address == None:
            ssid = ap['ssid']
            channel = ap['channel']
            try:
                print('Trying to connect to {0}'.format(ssid))
                wifi.radio.connect(
                    ssid=ssid, password=WIFI_PASSWORD, channel=channel)
            except ConnectionError as connection_error:
                print(f'Connection failed: {connection_error}')

print(f'Connection established. IP-address: {wifi.radio.ipv4_address}')


#   Establish websocket and set time

pool = socketpool.SocketPool(wifi.radio)
ntp_time = ntp.NTP(pool)

rtc.set_time_source(ntp_time)

print(f'Current time: {mu_time.now()}')
