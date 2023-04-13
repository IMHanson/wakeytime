import os
import ntp
import rtc
import mu_time
import board
from digitalio import DigitalInOut, Direction, Pull
from socketpool import SocketPool
import wifi
from nattlys import *
from nattlys import nattlys as Nattlys
from adafruit_httpserver.mime_type import MIMEType
from adafruit_httpserver.request import HTTPRequest
from adafruit_httpserver.response import HTTPResponse
from adafruit_httpserver.server import HTTPServer
from adafruit_httpserver.methods import HTTPMethod
import mdns


#####   Environment Variables   #####
SSID = os.getenv('CIRCUITPY_WIFI_SSID')
WIFI_PASSWORD = os.getenv('CIRCUITPY_WIFI_PASSWORD')


#####   Wifi    #####
def connect_wifi(password:str):
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
                    ssid=ssid, password=password, channel=channel)
                except ConnectionError as connection_error:
                    print(f'Connection failed: {connection_error}')

    print(f'Connection established. IP-address: {wifi.radio.ipv4_address}')


#####   Connect to Wifi #####
try:
    wifi.radio.connect(SSID, WIFI_PASSWORD)
except ConnectionError:
    connect_wifi()


#####   Initiate button pin #####
dance_button = DigitalInOut(board.D19)
dance_button.direction = Direction.INPUT
dance_button.pull = Pull.UP


#####   Initiate socket and set time    #####
pool = SocketPool(wifi.radio)
ntp_time = ntp.NTP(pool)

rtc.set_time_source(ntp_time)

get_idToken()
get_sleepy_time()
get_wakey_time()
update_lights()


#####   HTTP server #####
mdns_server = mdns.Server(wifi.radio)
mdns_server.hostname = "wakey-time"
mdns_server.advertise_service(service_type="_http", protocol="_tcp", port=8000)

server = HTTPServer(pool)
HOST = str(wifi.radio.ipv4_address)

@server.route("/")
def index(request: HTTPRequest):
    with HTTPResponse(request, content_type=MIMEType.TYPE_HTML) as response:
        response.send_file('/static/index.html')


@server.route("/wakey-data")
def wakey_data(request: HTTPRequest):
    data = {'sleepy-time': Nattlys['sleepy-time'],
            'wakey_time': Nattlys['wakey-time'],
            'wakey-status': "Wakey-Time" if nattlys.is_wakey_time() else "Sleepy-Time",
            'status-message': 'It is okay to get up now' if nattlys.is_wakey_time() else 'You should be in bed',
            'isWakeyTime': is_wakey_time()}
    data = json.dumps(data)

    with HTTPResponse(request, content_type=MIMEType.TYPE_JSON) as response:
        response.send(data)


@server.route("/styles.css")
def css(request: HTTPRequest):
    with HTTPResponse(request, content_type=MIMEType.TYPE_CSS) as response:
        response.send_file('/static/styles.css')


@server.route("/change-wakey-time")
def change_wakey_time(request: HTTPRequest):
    new_time = request.query_params('wakeyTime')
    
    set_wakey_time(new_time)
    
    with HTTPResponse(request, content_type=MIMEType.TYPE_TXT) as response:
        response.send('Wakey-time updated')


@server.route("/change-sleepy-time")
def change_sleepy_time(request: HTTPRequest):
    new_time = request.query_params('sleepyTime')
    
    set_sleepy_time(new_time)

    with HTTPResponse(request, content_type=MIMEType.TYPE_TXT) as response:
        response.send('Sleepy-Time updated')


@server.route("/toggle-slumber")
def slumber(request: HTTPRequest):
    toggle_slumber()
    with HTTPResponse(request, content_type=MIMEType.TYPE_TXT) as response:
        response.send('Slumber toggled')


@server.route("/dance")
def dance(request: HTTPRequest):
    dance_party()
    with HTTPResponse(request, content_type=MIMEType.TYPE_TXT) as response:
        response.send("Dance Party!")


server.start(host=HOST, port=8000)


#####   Main Loop   #####
loop_count = 0

while mu_time.now() < '08:00':
    if dance_button.value == True:
        print('dance')
        dance_party()
    
    if loop_count == 9:
        get_sleepy_time()
        get_wakey_time()
    elif loop_count >= 10:
        loop_count = 0

    try:
        server.poll()
    except OSError as err:
        print(err)
        continue
