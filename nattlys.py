import time
import mu_time
from firebase_realtime import Realtime
import env_vars
import eyes

headers = ''
with open('validate.txt', 'r') as validate:
    headers = validate.read()

realtime_db = Realtime(env_vars.FIREBASE_URL, headers)

#####   Time Info   #####

# Defaults incase of network trouble
time_settings = {'wakey-time': '06:30',
                 'sleepy-time': '18:30',
                 'slumber-mode': False}


# Check to see if Slumber Mode is engaged
def get_slumber_mode():
    try:
        flg, slumber_mode = realtime_db.get('Nattlys/slumber-mode')
        time_settings['slumber-mode'] = slumber_mode
    except:
        slumber_mode = time_settings['slumber-mode']
    return slumber_mode


# Extends sleepy-time by the slumber length provided (in minutes)
def sleep_in(slumber_length: int=30):
    try:
        sleepy_time = get_sleepytime()
    except:
        sleepy_time = time_settings['sleepy-time']

    hour = int(sleepy_time.split(':')[0])
    minute = int(sleepy_time.split(':')[1])
    
    minute += slumber_length
    while minute >= 60:
        hour += 1
        minute %= 60

    hour = f'0{hour}' if hour < 10 else f'{hour}'
    minute = f'0{minute}' if minute < 10 else f'{minute}'
    return f'{hour}:{minute}'


# Get Wakey-time info from Firebase
def get_wakeytime():
    try:
        flg, w_time_info = realtime_db.get('Nattlys/default-time/wakey-time')
    
        hour = w_time_info['HR']
        minute = w_time_info['MIN']
    
        shr = f'0{hour}'  if hour < 10 else f'{hour}'
        smin = f'0{minute}' if minute < 10 else f'{minute}'

        wakey_time = f'{shr}:{smin}'

        time_settings['wakey-time'] = wakey_time

    except:
        wakey_time = time_settings['wakey-time']

    return wakey_time


# Changes wakey-time and updates Firebase
def change_wakey_time(new_time: str):
    hour = new_time.split(':')[0]
    minute = new_time.split(':')[1]

    realtime_db.patch('/Nattlys/default-time/wakey-time', ({'HR': hour}, {'MIN': minute}))

    time_settings['wakey-time'] = new_time

    print(f'Wakey-time has been updated to {new_time}')


# Get Sleepy-time info from Firebase
def get_sleepytime():
    try:
        flg, s_time_info = realtime_db.get('Nattlys/default-time/sleepy-time')

        hour = s_time_info['HR']
        minute = s_time_info['MIN']

        # assign the updated value to sleepy_time
        sleepy_time = f'0{hour}:{minute}' if hour < 10 else f'{hour}:{minute}'
        time_settings['sleepy-time'] = sleepy_time

    except:
        sleepy_time = time_settings['sleepy-time']

    return sleepy_time


# Changes sleepy-time and updates Firebase
def change_sleepy_time(new_time: str):
    hour = new_time.split(':')[0]
    minute = new_time.split(':')[1]

    realtime_db.patch('/Nattlys/default-time/sleepy-time', ({'HR': hour}, {'MIN': minute}))

    time_settings['sleepy-time'] = new_time

    print(f'Sleepy-time has been updated to {new_time}')


# Compare the current time with sleepy-time and wakey-time to see if it is time to get up
def is_wakeytime():
    slumber_mode = get_slumber_mode()
    wakey_time = sleep_in if slumber_mode else get_wakeytime()
    sleepy_time = get_sleepytime()
    current_time = mu_time.now()

    after_wakeup = wakey_time <= current_time
    before_bedtime = current_time < sleepy_time

    return after_wakeup and before_bedtime


# Update the lights so that the appropriate eyes are lit 
def update_lights():

    eyes.green_on_yellow_off() if is_wakeytime() else eyes.yellow_on_green_off()

    print(f"""
    -------------------------------------
            Wakey-Time Nightlight
    -------------------------------------

        The current time is:    {mu_time.now}
        Sleepy-Time is set to:  {get_sleepytime()}
        Wakey-Time is set to:   {get_wakeytime()}

    -------------------------------------

        {'It is okay to get up now' if is_wakeytime() else 'You should be in bed'}

    """)


# Light show
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
