#!/usr/bin/python3
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor
from gpiozero import LEDBarGraph, LED, Button, DigitalInputDevice, SmoothedInputDevice, DigitalOutputDevice
#from signal import pause
from time import sleep

import signal
import time
import atexit
import os

class treeWater:
        def __init__(self):
                self.GPIO_led_R1 = 14
                self.GPIO_led_Y1 = 15
                self.GPIO_led_G1 = 4
                self.GPIO_led_B1 = 17
                self.GPIO_btn_B1 = 18
                self.MTR_pump1 = 1
                
                self.GPIO_wtr_tgd = 21
                self.GPIO_wtr_t01 = 20
                self.GPIO_wtr_t02 = 19
                self.GPIO_wtr_t03 = 16
                self.GPIO_wtr_t04 = 13
                self.GPIO_wtr_t05 = 12
                self.GPIO_wtr_t06 = 6
                self.GPIO_wtr_t07 = 5
                self.GPIO_wtr_t08 = 7
                self.GPIO_wtr_t09 = 8
                self.GPIO_wtr_t10 = 11
                self.GPIO_wtr_t11 = 9
                self.GPIO_wtr_t12 = 10
                self.GPIO_wtr_t13 = 25
                
                self.GPIO_wtr_pgd = 22
                self.GPIO_wtr_p01 = 23
                
                # Setup the water level indicator
#                self.wtrLevel = LEDBarGraph(self.GPIO_led_R1, self.GPIO_led_Y1, self.GPIO_led_G1, pwm=True)
                
                # Setup the Pump Water Level Sensor
                # _pumpWtrLevelGnd should remain ON the entire time
                self._pumpWtrLevelGnd = DigitalOutputDevice(self.GPIO_wtr_pgd, True, True)
                self.pumpWtrLevel = DigitalInputDevice(self.GPIO_wtr_p01)
                
                # Setup the tree water level indicator
                # _treeWtrLevelGnd should remain ON the entire time
                self._treeWtrLevelGnd = DigitalOutputDevice(self.GPIO_wtr_tgd, True, True)

                self.treeWtrLevel01 = DigitalInputDevice(self.GPIO_wtr_t01)
                self.treeWtrLevel02 = DigitalInputDevice(self.GPIO_wtr_t02)
                self.treeWtrLevel03 = DigitalInputDevice(self.GPIO_wtr_t03)
                self.treeWtrLevel04 = DigitalInputDevice(self.GPIO_wtr_t04)
                self.treeWtrLevel05 = DigitalInputDevice(self.GPIO_wtr_t05)
                self.treeWtrLevel06 = DigitalInputDevice(self.GPIO_wtr_t06)
                self.treeWtrLevel07 = DigitalInputDevice(self.GPIO_wtr_t07)
                self.treeWtrLevel08 = DigitalInputDevice(self.GPIO_wtr_t08)
                self.treeWtrLevel09 = DigitalInputDevice(self.GPIO_wtr_t09)
                self.treeWtrLevel10 = DigitalInputDevice(self.GPIO_wtr_t10)
                self.treeWtrLevel11 = DigitalInputDevice(self.GPIO_wtr_t11)
                self.treeWtrLevel12 = DigitalInputDevice(self.GPIO_wtr_t12)
                self.treeWtrLevel13 = DigitalInputDevice(self.GPIO_wtr_t13)
                
                # Setup the pump status indicator and manual override button
                self.pumpStsLED = LED(self.GPIO_led_B1)
                self.pumpBtn = Button(self.GPIO_btn_B1, True)
                
                # create a default object, no changes to I2C address or frequency
                self.mtrHat = Adafruit_MotorHAT(addr=0x60)
                
                self.pump = self.mtrHat.getMotor(self.MTR_pump1)
                
                # We should always run at max speed
                self.pump.setSpeed(255)
                
                self.pumpSts = False

        # recommended for auto-disabling motors on shutdown!
        def Shutdown(self):
	        self.mtrHat.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
	        self.mtrHat.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
	        self.mtrHat.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
	        self.mtrHat.getMotor(4).run(Adafruit_MotorHAT.RELEASE)

        def pumpRun(self):
                if self.pumpSts == False:
                        # Pump is off; Turn it on
                        self.log("Turning Pump On","INFO")
                        self.pump.run(Adafruit_MotorHAT.FORWARD)
                        self.pumpSts = True
                        self.pumpStsLED.on()
                #else:
                        # Pump is already running; Do nothing

        def pumpStop(self):
                if self.pumpSts == True:
                        # Pump is on; Turn it off
                        self.log("Turning Pump Off","INFO")
                        self.pump.run(Adafruit_MotorHAT.RELEASE)
                        self.pumpSts = False
                        self.pumpStsLED.off()
                #else:
                        # Pump is already off; Do nothing

        def log(self, msg, level = "INFO"):
                # Probably prefix MSG with timestamp?
                # Add logging facilities later
                ts = time.gmtime()
                ts = time.strftime("%Y-%m-%d %H:%M:%S", ts)
                print(ts," - ",level,": ",msg)

        def manualRun(self):
                self.log("Manual override process running...")
                while True:
                        if self.pumpBtn.value:
                                self.pumpRun()
                        else:
                                self.pumpStop()
                        # Cool this down a little
                        sleep(0.5)

        def autoFill(self):
                self.log("Automatic filler process running...")
                while True:
                        if self.WtrLevel.value <= 0.5 and self.pumpWtrLevel.value:
                                self.pumpRun()
                        else:
                                self.pumpStop()
                        # Cool this down a little
                        sleep(0.5)
                        
        def monitorWtrPump(self):
                self.log("Pump water level checker running...")
                lastState = not self.pumpWtrLevel.value
                stateCheck = True
                while True:
                        state = self.pumpWtrLevel.value
                        if lastState != state:
                                lastState = state
                                if state:
                                        self.log("Pump water present","INFO")
                                        if self.pumpSts:
                                                self.pumpStsLED.on()
                                        else:
                                                self.pumpStsLED.off()
                                else:
                                        self.log("Low pump water level","WARNING")
                                        self.pumpStsLED.blink(0.5,0.5,None,True)
                        # Cool this down a little
                        sleep(0.5)

        def monitorTreeWtr(self):
                self.log("Tree water level monitor running...")
                self.wtrLevel = LEDBarGraph(self.GPIO_led_R1, self.GPIO_led_Y1, self.GPIO_led_G1, pwm=True)
                level = 0
                lastLevel = -1

                while True:
                        # This is terrible, horrible, very bad code!
                        if self.treeWtrLevel13.value:
                                level = 13
                        elif self.treeWtrLevel12.value:
                                level = 12
                        elif self.treeWtrLevel11.value:
                                level = 11
                        elif self.treeWtrLevel10.value:
                                level = 10
                        elif self.treeWtrLevel09.value:
                                level = 9
                        elif self.treeWtrLevel08.value:
                                level = 8
                        elif self.treeWtrLevel07.value:
                                level = 7
                        elif self.treeWtrLevel06.value:
                                level = 6
                        elif self.treeWtrLevel05.value:
                                level = 5
                        elif self.treeWtrLevel04.value:
                                level = 4
                        elif self.treeWtrLevel03.value:
                                level = 3
                        elif self.treeWtrLevel02.value:
                                level = 2
                        elif self.treeWtrLevel01.value:
                                level = 1
                        else:
                                level = 0

                        if lastLevel != level:
                                self.log("Tree water level now at level " + str(level), "INFO")
                                lastLevel = level

                        level = level / 13
                        self.wtrLevel.value = level
                        sleep(1)


def parent():
        tree = treeWater()

        # We should spawn these children in a better manner with IPC
        manualRun = os.fork()
        if manualRun == 0:
                tree.manualRun()
                os._exit()
        
#        monitorWtrPump = os.fork()
#        if monitorWtrPump == 0:
#                tree.monitorWtrPump()
#                os._exit()

#        monitorTreeWtr = os.fork()
#        if monitorTreeWtr == 0:
#                tree.monitorTreeWtr()
#                os._exit()

#        autoFill = os.fork()
#        if autoFill == 0:
#                tree.autoFill()
#                os._exit()

        print("Waiting for children to start...")
        sleep(5)
        
        while True:
                sleep(1)
#                reply = input("\nq for quit\n")
#                if reply == 'q':
#                        break

        os.kill(manualRun, signal.SIGKILL)
#        os.kill(monitorWtrPump, signal.SIGKILL)
#        os.kill(monitorTreeWtr, signal.SIGKILL)
#        os.kill(autoFill, signal.SIGKILL)
        tree.Shutdown()
        wtrLevel = LEDBarGraph(tree.GPIO_led_R1, tree.GPIO_led_Y1, tree.GPIO_led_G1, pwm=True)
        wtrLevel = 0.0

        
parent()

#atexit.register(tree.Shutdown)
