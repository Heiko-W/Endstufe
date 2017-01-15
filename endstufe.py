#!/usr/bin/python3

# Author:       Heiko Wilke
# Description:  Script to contral Digital Amplifier with Texas Instruments TAS5518 
#               via I2C using Firmata on Arduino 
# Copyright 2017 Heiko Wilke

import time
import signal
import sys
import subprocess
import re
from pymata_aio.pymata3 import PyMata3
from pymata_aio.constants import Constants

print("Started Endstufe Controller")

I2C_MULTIPLEX_ADDRESS = 0x70
TAS5518_ADDRESS = 0x1B
TAS5518_MASTER_VOL_REG = 0xD9
TAS5518_AUTOMUTE_CTRL_REG = 0x14
TAS5518_AUTOMUTE_PWM_REG = 0x15

MAX_VOLUME_VAL = 0x01
MIN_VOLUME_VAL = 0x1F0
MUTE = 0x03FF

VOL_STEP = (MIN_VOLUME_VAL-MAX_VOLUME_VAL) /100

firmata = PyMata3()
firmata.i2c_config()

# Initialisiere Emdstufe (4x TAS5518 über NXP PCA 9544A - I2C Multiplexer) 
for i in range(0x04, 0x08):
    firmata.i2c_write_request(I2C_MULTIPLEX_ADDRESS, [i])
    firmata.i2c_write_request(TAS5518_ADDRESS, [0x03, 0x90])
    firmata.i2c_write_request(TAS5518_ADDRESS, [0x16, 0x04])
    # Set Master Volume to default start value
    firmata.i2c_write_request(TAS5518_ADDRESS, [TAS5518_MASTER_VOL_REG, 0x00, 0x00, 0x00, 0x90])
    # Deactivate Automute
    firmata.i2c_write_request(TAS5518_ADDRESS, [TAS5518_AUTOMUTE_CTRL_REG, 0x04])
    firmata.i2c_write_request(TAS5518_ADDRESS, [TAS5518_AUTOMUTE_PWM_REG, 0x05])


# Try to Set System Volume to 25% - Otherwise quit program
try:
    amixer_out = subprocess.run(["amixer", "sset", "'Master'", "25%"], check=True) 
except:
    print("Error using amixer")
    print("Program ends")
    firmata.shutdown()
    sys.exit(0)

# Define exit function
def exit_gracefully(signum, frame):
    print("Program ends")
    firmata.shutdown()
    sys.exit(0)

# setup signal handler
signal.signal(signal.SIGINT, exit_gracefully)

# Function to set volume - input is integer volume in percent
# channel: 1-8
def set_volume(vol):
    arrvolume = bytes(4)
    # Lautstärke Wert für Register berechnen
    volume = int(MIN_VOLUME_VAL - (VOL_STEP*vol))
    if vol == 0:
        volume = MUTE
    arrvolume = volume.to_bytes(4,byteorder="big")
    print("Volume: 0x{0:X}".format(volume))
    for i in range(0x04, 0x08):
        firmata.i2c_write_request(I2C_MULTIPLEX_ADDRESS, [i])
        firmata.i2c_write_request(TAS5518_ADDRESS, [TAS5518_MASTER_VOL_REG, arrvolume[0], arrvolume[1], arrvolume[2], arrvolume[3]])

vol_percent_old = 0
while True:
    # Check System Volume mit amixer get Master
    amixer_out = subprocess.check_output(['amixer', 'get', 'Master'])
    amixer_str = str(amixer_out, 'utf-8')
    amixer_substr = re.findall(r'Front Left:.*\d+.*\d+.*\d+', amixer_str)
    values = re.findall(r'\d+', amixer_substr[0])
    vol_percent = int(values[1])
    #vol_db=float(values[2]+"."+values[3])

    if vol_percent_old != vol_percent:
        set_volume(vol_percent)
    vol_percent_old = vol_percent

    time.sleep(100.0/1000.0)