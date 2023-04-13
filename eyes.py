import board
import time
from digitalio import DigitalInOut, Direction


class Eyes():
    def __init__(self, left_pin, right_pin, color):
        self.left_eye = DigitalInOut(left_pin)
        self.left_eye.direction = Direction.OUTPUT

        self.right_eye = DigitalInOut(right_pin)
        self.right_eye.direction = Direction.OUTPUT

        self.color = color

    def lights_on(self):
        self.left_eye.value = True
        self.right_eye.value = True

    def lights_out(self):
        self.left_eye.value = False
        self.right_eye.value = False

    def wink(self, eye):
        eye.value = False
        time.sleep(1)
        eye.value = True

    def flash(self):
        for i in range(3):
            self.lights_on()
            time.sleep(0.05)
            self.lights_out()
            time.sleep(0.05)

    def check(self):
        self.left_eye.value = True
        time.sleep(0.05)
        self.right_eye.value = True
        time.sleep(0.05)
        self.wink(self.left_eye)
        time.sleep(0.05)
        self.wink(self.right_eye)
        time.sleep(0.05)
        self.flash()

green_eyes = Eyes(board.D33, board.D32, 'green')
yellow_eyes = Eyes(board.D5, board.D18, 'yellow')

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
