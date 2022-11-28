#!/usr/bin/python3

import os                                           # Used for OS interaction (os.system('clear'))
from time import sleep                              # Used for sleep()
import time                                         # Used for timestamps

import threading                                    # Lets us multithread

import board                                        # Used to reference pins by name on the Pi
import digitalio                                    # Used to control I/Os on the Pi
import busio                                        # Used for SPI

from gpiozero import LED, Button                    # Used for "LED" and "Button" types of I/O
from gpiozero import LEDBarGraph, DigitalInputDevice, SmoothedInputDevice, DigitalOutputDevice

import adafruit_mcp3xxx.mcp3008 as MCP              # Used to interface with the MCP3008 over SPI
from adafruit_mcp3xxx.analog_in import AnalogIn     # Used to read the MCP3008 analog values
from Adafruit_MotorHAT import Adafruit_MotorHAT     # Used to interface with the Motor HAT
from Adafruit_MotorHAT import Adafruit_DCMotor      # Used to control motors on the Motor HAT



class treeWtr:
    #
    # This object will track the status of various elements of the tree watering Pi
    # 
    # Things we should store:
    # - Water Level
    # - Motor Status
    # - Reference to water level sensor
    # - Statically set pins for power
    # - Reference to Water Level LED Bar Graph
    #

    #
    # Config Vars
    #
    wtrLevelRawMin = 33728
    wtrLevelRawMax = 42304
    wtrLevelRawTol = 250


    # Create vars for the LEDs and buttons
    GPIO_led_R1 = board.D14
    GPIO_led_Y1 = board.D15
    GPIO_led_G1 = board.D4
    GPIO_led_B1 = board.D17
    GPIO_btn_B1 = board.D18

    # Setup SPI variables
    SPI_CLOCK = board.SCK
    SPI_MISO = board.MISO
    SPI_MOSI = board.MOSI
    SPI_CS_3008 = board.D25    # PIN 25 is CS for the 3008 SPI
    
    # GPIOs for water resevoir sensor
    GPIO_wtr_pgd = board.D22
    GPIO_wtr_p01 = board.D23

    # Motor to use to pump water
    MTR_pump1 = 1

    # If I had the 3008 properly wired on the motor hat, I wouldn't need to do this.
    # Since I have it wired outboard, I need to power it separately

    # Set several GPIOs as GND to provide power
    GPIO_GND = []
    GPIO_GND.append(board.D16)
    GPIO_GND.append(board.D19)
    GPIO_GND.append(board.D20)
    GPIO_GND.append(board.D21)

    # Set several GPIOs as 3.3V to provide power
    GPIO_3v = []
    GPIO_3v.append(board.D5)
    GPIO_3v.append(board.D6)
    GPIO_3v.append(board.D12)
    GPIO_3v.append(board.D13)


    #
    # Interal Vars
    #
    wtrLevel = 0


    #
    # Constructor
    #
    def __init__(self):

        #
        # Setup the static pins
        #

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

        #
        # Setup the LED Bar Graph
        #
        # Setup the water level indicator
        self.wtrLevelGraph = LEDBarGraph(self.GPIO_led_R1.id, self.GPIO_led_Y1.id, self.GPIO_led_G1.id, pwm=True)

    
    #
    # Register all child 
    #
    def forkYou():
        #
        sleep(1)
    

    #
    # Logging facility
    # Nicely log all messages to the terminal
    # TODO: implement a FIFO queue to handle threading
    #
    def log(self, msg, level = "INFO"):
        # Probably prefix MSG with timestamp?
        # Add logging facilities later
        ts = time.gmtime()
        ts = time.strftime("%Y-%m-%d %H:%M:%S", ts)
        print(ts," - ",level,": ",msg)


##
# treeWtrPump Check requested pump status and run accordingly
#
# - Check if button is pushed
# - Check water level
# Run if either conditions are met
#
class treeWtrPump(threading.Thread):
    def __init__(self, treeWtr, *args, **kwargs):
        super(treeWtrPump,self).__init__(*args, **kwargs)
        self.treeWtr = treeWtr

    def run(self):
        # Not implemented
        sleep(1)


##
# Check and update the water level of the tree water
#
class treeWtrLevel(threading.Thread):
    def __init__(self, treeWtr, *args, **kwargs):
        super(treeWtrLevel,self).__init__(*args, **kwargs)
        self.treeWtr = treeWtr

    def run(self):
        self.treeWtr.log("treeWtrLevel running...", "INFO")

        lastLevel = 0

        while True:
            # Check the current level
            level = self.treeWtr.chan0.value
            # See how much the current level has changed from last time
            change = abs(level - lastLevel)
            # Reduce jitter - only update if we are above level of jitter
            if change > self.treeWtr.wtrLevelRawTol:
                self.treeWtr.wtrLevel = level
                lastLevel = level
                pct = limit_pct(val_pct(level, self.treeWtr.wtrLevelRawMin, self.treeWtr.wtrLevelRawMax))
                self.treeWtr.log("Tree water level is now " + str(round(pct, 2) * 100) + "% (Raw: " + str(level) + ")", "INFO")
            sleep(0.5)


##
# Check and update the existence of water for the resevoir pump
#
class treeWtrPumpLevel(threading.Thread):
    def __init__(self, treeWtr, *args, **kwargs):
        super(treeWtrPumpLevel,self).__init__(*args, **kwargs)
        self.treeWtr = treeWtr

    def run(self):
        self.treeWtr.log("treeWtrPumpLevel running...", "INFO")

        while True:
            # Currently not implemented
            sleep(10)


##
# Display the status of the tree watering system
#
# - LED Bar graph w/water level
# - Pump Status
# - Alerts & Errors
#
class treeWtrDisplay(threading.Thread):
    def __init__(self, treeWtr, *args, **kwargs):
        super(treeWtrDisplay,self).__init__(*args, **kwargs)
        self.treeWtr = treeWtr

    def run(self):
        self.treeWtr.log("treeWtrDisplay running...", "INFO")

        lastLevel = 0

        while True:
            level = self.treeWtr.wtrLevel
            change = abs(level - lastLevel)
            if change > self.treeWtr.wtrLevelRawTol:
                pct = limit_pct(val_pct(level, self.treeWtr.wtrLevelRawMin, self.treeWtr.wtrLevelRawMax))
                self.treeWtr.wtrLevelGraph.value = pct
                lastLevel = level
            sleep(0.5)


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


treeWtr = treeWtr()

threads = [ #treeWtrPump(treeWtr=treeWtr, name='a'), 
            treeWtrLevel(treeWtr=treeWtr, name='b'),
            #treeWtrPumpLevel(treeWtr=treeWtr)#,
            treeWtrDisplay(treeWtr=treeWtr)
]
for t in threads:
    t.start()
for t in threads:
    t.join()

print("Process Terminated")
