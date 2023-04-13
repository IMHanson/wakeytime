import json
import os
import ssl
import time
import adafruit_requests as requests
import wifi
from socketpool import SocketPool
import eyes
import mu_time

EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('EMAIL_PASSWORD')
AUTH_URL = os.getenv('URL')
BASE_URL = os.getenv('FIREBASE_URL')

pool = SocketPool(wifi.radio)
context = ssl.create_default_context()
http = requests.Session(pool, context)

nattlys = {'wakey-time': '06:30',
           'sleepy-time': '18:30',
           'slumber-mode': False}
idToken = ''

def get_idToken():
    auth_data = {'email': EMAIL, 'password': PASSWORD,
                 'returnSecureToken': True}
    auth_data = json.dumps(auth_data)
    headers = {'content-type': 'application/json'}

    response = http.post(url=AUTH_URL, headers=headers, data=auth_data)

    if response.status_code == 200:
        response_data = response.json()
        header_data = {'content-type': 'application/json; charset=utf-8'}

        for header in ('idToken', 'email', 'refreshToken', 'expiresIn', 'localId'):
            header_data[header] = str(response_data[header])

        response.close()
        idToken = header_data['idToken']
    else:
        get_idToken()


def format_url(rel_url):
    return f'{BASE_URL}/{rel_url}/.json?auth={idToken}'


#####   Sleepy-Time #####

def get_sleepy_time():
    try:
        sleepy_url = format_url('Nattlys/sleepy-time')
        response = http.get(sleepy_url)
        sleepy_data = response.json()
        response.close()

        hour = int(sleepy_data['HR'])
        minute = int(sleepy_data['MIN'])
        shr = f'0{hour}' if hour < 10 else f'{hour}'
        smin = f'0{minute}' if minute < 10 else f'{minute}'

        nattlys['sleepy-time'] = f'{shr}:{smin}'
    except Exception as ex:
        print(f'{ex}\nUsing default settings')


def set_sleepy_time(new_time: str):
    nattlys['sleepy-time'] = new_time

    hour = new_time.split(':')[0]
    minute = new_time.split(':')[1]
    data = {'HR': int(hour), 'MIN': int(minute)}
    data = json.dumps(data)

    sleepy_url = format_url('Nattlys/sleepy-time')
    response = http.patch(url=sleepy_url, data=data)
    print(response.status_code)
    response.close()


#####   Slumber-Mode    #####

def is_slumber_mode():
    try:
        slumber_url = format_url('Nattlys/slumber-mode')
        response = http.get(slumber_url)
        nattlys['slumber-mode'] = response.json()
        response.close()
    except Exception as ex:
        print(f'{ex}\nUsing default settings')

    return nattlys['slumber-mode']


def toggle_slumber():
    nattlys['slumber-mode'] = not nattlys['slumber-mode']
    slumber_mode = nattlys['slumber-mode']

    url = format_url('Nattlys')
    data = {'slumber-mode': slumber_mode}
    data = json.dumps(data)
    response = http.patch(url=url, data=data)
    print(response.status_code)
    response.close()


#####   Wakey-Time #####

def sleep_in(slumber_length: int = 30):
    wakey_time = nattlys['wakey-time']

    hour = int(wakey_time.split(':')[0])
    minute = int(wakey_time.split(':')[1])
    hour += slumber_length // 60
    minute += slumber_length % 60

    shr = f'0{hour}' if hour < 10 else f'{hour}'
    smin = f'0{minute}' if minute < 10 else f'{minute}'

    return f'{shr}:{smin}'


def get_wakey_time():
    try:
        wakey_url = format_url('Nattlys/wakey-time')
        response = http.get(wakey_url)
        wakey_data = response.json()
        response.close()

        hour = wakey_data['HR']
        minute = wakey_data['MIN']
        shr = f'0{hour}' if hour < 10 else f'{hour}'
        smin = f'0{minute}' if minute < 10 else f'{minute}'

        nattlys['wakey-time'] = f'{shr}:{smin}'
    except Exception as ex:
        print(f'{ex}\nUsing default settings')


def set_wakey_time(new_time: str):
    nattlys['wakey-time'] = new_time

    hour = new_time.split(':')[0]
    minute = new_time.split(':')[1]
    data = {'HR': int(hour), 'MIN': int(minute)}
    data = json.dumps(data)

    wakey_url = format_url('Nattlys/wakey-time')
    response = http.patch(url=wakey_url, data=data)
    print(response.status_code)
    response.close()


def is_wakey_time():
    wakey_time = sleep_in() if is_slumber_mode() else nattlys['wakey-time']
    sleepy_time = nattlys['sleepy-time']
    current_time = mu_time.now()

    after_wakeup = wakey_time <= current_time
    before_bedtime = current_time < sleepy_time

    return after_wakeup and before_bedtime


#####   Controll the lights #####

def update_lights():
    eyes.green_on_yellow_off() if is_wakey_time() else eyes.yellow_on_green_off()

    print(f"""
    -------------------------------------
            Wakey-Time Nightlight
    -------------------------------------

        The current time is:    {mu_time.now()}
        Sleepy-Time is set to:  {nattlys['sleepy-time']}
        Wakey-Time is set to:   {nattlys['wakey-time']}
        Slumber-Mode is:        {'ON' if is_slumber_mode() else 'OFF'}

    -------------------------------------

        {'It is okay to get up now' if is_wakey_time() else 'You should be in bed'}

    """)


def dance_party():
    print('\n\n\t\tDANCE PARTY!!!\n\n')
    eyes.green_eyes.check()
    eyes.green_eyes.flash()
    eyes.yellow_eyes.check()
    eyes.yellow_eyes.flash()
    for i in range(3):
        eyes.green_on_yellow_off()
        time.sleep_ms(250)
        eyes.yellow_on_green_off()
        time.sleep_ms(250)
    eyes.green_eyes.check()
    eyes.green_eyes.flash()
    eyes.yellow_eyes.check()
    eyes.yellow_eyes.flash()
    update_lights()
