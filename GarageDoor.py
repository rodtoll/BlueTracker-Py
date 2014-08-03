__author__ = 'rodtoll'

import RPi.GPIO as GPIO
import time

def press_garage_door_button(pin_number):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin_number, GPIO.OUT, initial=False)
    GPIO.output(pin_number, True)
    time.sleep(2)
    GPIO.output(pin_number,False)
    GPIO.cleanup()

