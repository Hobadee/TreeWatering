#!/usr/bin/python3
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor
from gpiozero import LEDBarGraph, LED, Button
from signal import pause
from time import sleep

import time
import atexit

GPIO_led_R1 = 14
GPIO_led_Y1 = 15
GPIO_led_G1 = 4
GPIO_led_B1 = 17
GPIO_btn_B1 = 18
MTR_pump1 = 1

wtrLevel = LEDBarGraph(GPIO_led_R1, GPIO_led_Y1, GPIO_led_G1, pwm=True)
pumpSts = LED(GPIO_led_B1)
pumpBtn = Button(GPIO_btn_B1, True)

# create a default object, no changes to I2C address or frequency
mtrHat = Adafruit_MotorHAT(addr=0x60)

pump = mtrHat.getMotor(MTR_pump1)

# set the speed to start, from 0 (off) to 255 (max speed)
pump.setSpeed(255)

# recommended for auto-disabling motors on shutdown!
def Shutdown():
	mtrHat.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
	mtrHat.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
	mtrHat.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
	mtrHat.getMotor(4).run(Adafruit_MotorHAT.RELEASE)

def pumpRun():
        log("Turning Pump On")
        pump.run(Adafruit_MotorHAT.FORWARD)
        pumpSts.on()

def pumpStop():
        log("Turning Pump Off")
        pump.run(Adafruit_MotorHAT.RELEASE)
        pumpSts.off()

def log(msg):
        print(msg)
        
atexit.register(Shutdown)

pumpBtn.when_pressed = pumpRun
pumpBtn.when_released = pumpStop
#pumpSts.source = pumpBtn.values

for i in range(0,105, 5):
        wtrLevel.value = i/100
        print("i=",i)
        sleep(1)

pause()

#runtime = 5.0
#offtime = 5.0
#loops = 0

#while (True):
#	print("Running for ",runtime," seconds.")
#	pump.run(Adafruit_MotorHAT.FORWARD)
#	time.sleep(runtime)
#	print("Off for ",offtime," seconds")
#	pump.run(Adafruit_MotorHAT.RELEASE)
#	time.sleep(offtime)
#	loops = loops + 1
#	print("We have run ",loops," times.")
