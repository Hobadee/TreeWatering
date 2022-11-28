#!/usr/bin/python3
from time import sleep

import os
import time
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn



# Set several GPIOs as GND to provide power
GPIO_GND = []
GPIO_GND.append(board.D16)
GPIO_GND.append(board.D19)
GPIO_GND.append(board.D20)
GPIO_GND.append(board.D21)

#led.direction = digitalio.Direction.OUTPUT
for pin in GPIO_GND:
    p = digitalio.DigitalInOut(pin)
    p.direction = digitalio.Direction.OUTPUT
    p.value = False

# Set several GPIOs as 3.3V to provide power
GPIO_3v = []
GPIO_3v.append(board.D5)
GPIO_3v.append(board.D6)
GPIO_3v.append(board.D12)
GPIO_3v.append(board.D13)

for pin in GPIO_3v:
    p = digitalio.DigitalInOut(pin)
    p.direction = digitalio.Direction.OUTPUT
    p.value = True

#exit()


# Create the SPI bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

# Create the CS (Chip Select)
cs = digitalio.DigitalInOut(board.D25)

# Create the MCP object
mcp = MCP.MCP3008(spi, cs)

# Create an analog input channel on pin 0
chan0 = AnalogIn(mcp, MCP.P0)

while True:
    os.system('clear')
    print('Raw ADC Value: ', chan0.value)
    print('ADC Voltage: ' + str(chan0.voltage) + 'V')
    sleep(0.5)

last_read = 0       # To prevent jitter, we only update when we have moved
tolerance = 250     # some significant amount

exit()

# Min = 33728
# Max = 42304
