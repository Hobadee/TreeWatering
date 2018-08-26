#!/usr/bin/python3

import gpiozero
import time

input = 18

ip = gpiozero.InputDevice(input,True)

if ip.value:
    print("Input ",input," detected.")
else:
    print("Input ",input," not detected.")
