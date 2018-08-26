#!/usr/bin/python3

#import gpiozero
from gpiozero import LEDBarGraph, LED, Button
from time import sleep

GPIO_led_R = 14
GPIO_led_Y = 15
GPIO_led_G = 4
GPIO_led_B = 17
GPIO_btn_B = 18

graph = LEDBarGraph(GPIO_led_R, GPIO_led_Y, GPIO_led_G, pwm=True)

mtrSts = LED(GPIO_led_B)

mtrSts.on()

graph.value = 0
print("Graph off.  Waiting 5 seconds...")
sleep(5)
print("Graphing")

for i in range(0,100, 5):
    graph.value = i/100
    print("i=",i)
    mtrSts.toggle()
    sleep(1)
