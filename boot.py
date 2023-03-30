# This is script that run when device boot up or wake from sleep.
import ntptime
import network
import env_vars
from firebase_realtime import Auth
import eyes

#####   Initialize Wifi  & set time #####

wifi = network.WLAN(network.STA_IF)

if not wifi.isconnected():

    print('connecting to network...')
    wifi.active(True)
    wifi.connect(env_vars.WIFI_SSID, env_vars.WIFI_PASSWORD)

    while not wifi.isconnected():
        eyes.green_eyes.flash()
        eyes.yellow_eyes.flash()

print('network config:', wifi.ifconfig())
eyes.eye_check()

ntptime.settime()

#####   Initialize Firebase #####

auth = Auth()
flg, headers = auth.validate_user(env_vars.EMAIL, env_vars.PASSWORD, env_vars.API_KEY)
with open('validate.txt', 'w') as validate:
    validate.write(headers)