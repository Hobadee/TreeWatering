#!/usr/bin/python3

from gpiozero import Button, LED
from signal import pause

GPIO_btn_B = 18
GPIO_led_B = 17

btn = Button(GPIO_btn_B, True)
led = LED(GPIO_led_B)

led.source = btn.values

pause()
