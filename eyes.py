from machine import Pin
import time

class Eyes():
    def __init__(self, left_pin: int, right_pin: int, color: str):
        self.left_eye = Pin(left_pin, Pin.OUT)
        self.right_eye = Pin(right_pin, Pin.OUT)
        self.eye_color = color

    def __repr__(self):
        return f'These eyes are {self.eye_color}.'
    
    def lights_on(self):
        self.left_eye.on()
        self.right_eye.on()

    def lights_out(self):
        self.left_eye.off()
        self.right_eye.off()

    def wink(self, eye):
        eye.off()
        time.sleep(1)
        eye.on()

    def flash(self):
        for i in range(3):
            self.lights_on()
            time.sleep(0.05)
            self.lights_out()
            time.sleep(0.05)

    def check(self):
        self.left_eye.on()
        time.sleep_ms(50)
        self.right_eye.on()
        time.sleep_ms(50)
        self.wink(self.left_eye)
        time.sleep_ms(50)
        self.wink(self.right_eye)
        time.sleep_ms(50)
        self.flash()
    
green_eyes = Eyes(33, 32, 'green')
yellow_eyes = Eyes(5, 18, 'yellow')

def green_on_yellow_off():
    green_eyes.lights_on()
    yellow_eyes.lights_out()

def yellow_on_green_off():
    yellow_eyes.lights_on()
    green_eyes.lights_out()

def eye_check():
    print('Checking eyes...')
    green_eyes.check()
    yellow_eyes.check()
    print('Eye check complete!')