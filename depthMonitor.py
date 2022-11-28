#!/usr/bin/python3
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor
from gpiozero import LEDBarGraph, LED, Button, DigitalInputDevice, SmoothedInputDevice, DigitalOutputDevice
#from signal import pause
from time import sleep

import signal
import atexit

import os
import time
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn


# Helper since pump water level sensor is currently not active
class pumpWtrLevel:
        def __init__(self):
                self.value = True


class treeWater:
        #
        # Constructor
        #
        def __init__(self):

                #
                # Initialize Variables
                #

                # Create vars for the LEDs and buttons
                self.GPIO_led_R1 = board.D14
                self.GPIO_led_Y1 = board.D15
                self.GPIO_led_G1 = board.D4
                self.GPIO_led_B1 = board.D17
                self.GPIO_btn_B1 = board.D18

                # Setup SPI variables
                self.SPI_CLOCK = board.SCK
                self.SPI_MISO = board.MISO
                self.SPI_MOSI = board.MOSI
                self.SPI_CS_3008 = board.D25    # PIN 25 is CS for the 3008 SPI
                
                # GPIOs for water resevoir sensor
                self.GPIO_wtr_pgd = board.D22
                self.GPIO_wtr_p01 = board.D23

                # Motor to use to pump water
                self.MTR_pump1 = 1


                #
                # Initialize power for 3008
                #

                # If I had the 3008 properly wired on the motor hat, I wouldn't need to do this.
                # Since I have it wired outboard, I need to power it separately

                # Set several GPIOs as GND to provide power
                self.GPIO_GND = []
                self.GPIO_GND.append(board.D16)
                self.GPIO_GND.append(board.D19)
                self.GPIO_GND.append(board.D20)
                self.GPIO_GND.append(board.D21)

                # Set several GPIOs as 3.3V to provide power
                self.GPIO_3v = []
                self.GPIO_3v.append(board.D5)
                self.GPIO_3v.append(board.D6)
                self.GPIO_3v.append(board.D12)
                self.GPIO_3v.append(board.D13)

                # Init all GND pins
                for pin in self.GPIO_GND:
                        p = digitalio.DigitalInOut(pin)
                        p.direction = digitalio.Direction.OUTPUT
                        p.value = False

                # Init all 3.3v pins
                for pin in self.GPIO_3v:
                        p = digitalio.DigitalInOut(pin)
                        p.direction = digitalio.Direction.OUTPUT
                        p.value = True


                #
                # Setup the MCP3008 ADC
                #

                # Create the SPI bus
                spi = busio.SPI(clock=self.SPI_CLOCK, MISO=self.SPI_MISO, MOSI=self.SPI_MOSI)

                # Create the CS (Chip Select)
                cs = digitalio.DigitalInOut(self.SPI_CS_3008)

                # Create the MCP object
                mcp = MCP.MCP3008(spi, cs)

                # Create an analog input channel on pin 0
                self.chan0 = AnalogIn(mcp, MCP.P0)

                #print('Raw ADC Value: ', self.chan0.value)
                #print('ADC Voltage: ' + str(self.chan0.voltage) + 'V')

                #last_read = 0       # To prevent jitter, we only update when we have moved
                #tolerance = 250     # some significant amount


                #
                # 
                #

                self.wtrLevelMin = 33728
                self.wtrLevelMax = 42304
                self.wtrLevelTol = 250          # Change tolerance of the water level sensor

                # Setup the water level indicator
                #self.wtrLevelGraph = LEDBarGraph(self.GPIO_led_R1.id, self.GPIO_led_Y1.id, self.GPIO_led_G1.id, pwm=True)
                
                # Setup the Pump Water Level Sensor
                # _pumpWtrLevelGnd should remain ON the entire time
                #self._pumpWtrLevelGnd = DigitalOutputDevice(self.GPIO_wtr_pgd, True, True)
                #self.pumpWtrLevel = DigitalInputDevice(self.GPIO_wtr_p01)

                # Pump water level sensor currently not implemented - force true
                #self.pumpWtrLevel.value = True
                self.pumpWtrLevel = pumpWtrLevel()
                
                # Setup the pump status indicator and manual override button
                self.pumpStsLED = LED(self.GPIO_led_B1.id)
                self.pumpBtn = Button(self.GPIO_btn_B1.id, True)
                
                # Initialize the Motor HAT, no changes to I2C address or frequency
                self.mtrHat = Adafruit_MotorHAT(addr=0x60)
                
                self.pump = self.mtrHat.getMotor(self.MTR_pump1)
                # We should always run at max speed
                self.pump.setSpeed(255)
                # Start w/pump off
                self.pump.run(Adafruit_MotorHAT.RELEASE)
                self.pumpSts = False
                self.pumpStsLED.off()


                # Seed the water level
                level = self.chan0.value
                pct = limit_pct(val_pct(level, self.wtrLevelMin, self.wtrLevelMax))
                self.wtrLevel = pct


        #
        # Shutdown routine
        #
        # recommended for auto-disabling motors on shutdown!
        def Shutdown(self):
	        self.mtrHat.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
	        self.mtrHat.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
	        self.mtrHat.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
	        self.mtrHat.getMotor(4).run(Adafruit_MotorHAT.RELEASE)
                # Release all items in:
                # self.GPIO_3v
                # self.GPIO_GND


        # Start the pump
        def pumpRun(self):
                if self.pumpSts == False:
                        # Pump is off; Turn it on
                        self.log("Turning Pump On","INFO")
                        self.pump.run(Adafruit_MotorHAT.FORWARD)
                        self.pumpSts = True
                        self.pumpStsLED.on()
                #else:
                        # Pump is already running; Do nothing


        # Stop the pump
        def pumpStop(self):
                if self.pumpSts == True:
                        # Pump is on; Turn it off
                        self.log("Turning Pump Off","INFO")
                        self.pump.run(Adafruit_MotorHAT.RELEASE)
                        self.pumpSts = False
                        self.pumpStsLED.off()
                #else:
                        # Pump is already off; Do nothing


        #
        # Logging facility
        # Nicely log all messages to the terminal
        #
        def log(self, msg, level = "INFO"):
                # Probably prefix MSG with timestamp?
                # Add logging facilities later
                ts = time.gmtime()
                ts = time.strftime("%Y-%m-%d %H:%M:%S", ts)
                print(ts," - ",level,": ",msg)


        #
        # Manually run the pump while the button is pressed
        #
        def manualRun(self):
                self.log("Manual override process running...")
                lastState = False
                while True:
                        state = self.pumpBtn.value
                        if lastState != state:
                                lastState = state
                                if self.pumpBtn.value and self.pumpWtrLevel.value:
                                        self.log("Starting pump manually","INFO")
                                        self.pumpRun()
                                else:
                                        self.log("Stopping pump manually","INFO")
                                        self.pumpStop()
                        # Cool this down a little
                        sleep(0.5)


        #
        # Automatically keep the tree filled
        #
        def autoFill(self):
                self.log("Automatic filler process running...")
                lastState = False
                while True:
                        state = self.wtrLevel <= 0.7 and self.pumpWtrLevel.value
                        if lastState != state:
                                if state:
                                        self.pumpRun()
                                else:
                                        self.pumpStop()
                        # Cool this down a little
                        sleep(0.5)


        #
        # Monitor if there is water in the resevoir
        # 
        def monitorWtrPump(self):
                self.log("Pump water level checker running...")
                lastState = False
                while True:
                        state = self.pumpWtrLevel.value
                        if lastState != state:
                                # If state has changed, log change
                                lastState = state
                                if state:
                                        self.log("Pump water present","INFO")
                                        # I don't know what I was trying to do here...
                                        #if self.pumpSts:
                                        #        self.pumpStsLED.on()
                                        #else:
                                        #        self.pumpStsLED.off()
                                else:
                                        self.log("Low pump water level","WARNING")
                                        # If pump is out of water, blink the LED
                                        self.pumpStsLED.blink(0.5,0.5,None,True)
                        # Cool this down a little
                        sleep(0.5)


        #
        # Monitor the tree's water level
        #
        def monitorTreeWtr(self):
                self.log("Tree water level monitor running...")

                level = 0
                lastLevel = -65535

                self.wtrLevelGraph = LEDBarGraph(self.GPIO_led_R1.id, self.GPIO_led_Y1.id, self.GPIO_led_G1.id, pwm=True)

                while True:
                        level = self.chan0.value

                        change = abs(level - lastLevel)

                        # If the change > our tolerance to change, update
                        if change > self.wtrLevelTol:
                                pct = limit_pct(val_pct(level, self.wtrLevelMin, self.wtrLevelMax))
                                self.wtrLevel = pct
                                self.wtrLevelGraph.value = pct
                                lastLevel = level
                                self.log("Tree water level is now " + str(round(pct, 2) * 100) + "% (Raw: " + str(level) + ")", "INFO")
                                # Update the water level LEDs

                        sleep(1)


#
# Remap values from an old range to a new range
#
# For example, we can remap 0-65535 values to 0-255 values
#
def val_remap(value, old_min, old_max, new_min, new_max):
        old_range = old_max - old_min
        new_range = new_max - new_min

        # Convert old value to a percent
        pct = val_pct(value, old_min, old_max)

        # Convert percent to new value
        new_value = int(new_min + (pct * new_range))

        return new_value


#
# Return the percent a value is in a given range
#
def val_pct(value, min, max):
        return int(value - min) / int (max - min)


#
# Limit percentage to 0-100%
#
# Value is taken as a 0-1 float
#
def limit_pct(value):
        if value > 1:
                return 1
        if value < 0:
                return 0
        return value


#
#
#
def parent():
        tree = treeWater()

        monitorTreeWtr = os.fork()
        if monitorTreeWtr == 0:
                tree.monitorTreeWtr()
                os._exit()

        print("Waiting for children to start...")
        sleep(5)
        
        while True:
                sleep(1)
                # This works great for command line, but kills it when it's daemonized
#                reply = input("\nq for quit\n")
#                if reply == 'q':
#                        break

        os.kill(monitorTreeWtr, signal.SIGKILL)
        tree.Shutdown()


os.system('clear')
        
parent()

#atexit.register(tree.Shutdown)
