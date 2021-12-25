#!/usr/bin/python3

# libraries
import _thread
from time import sleep
import struct
from os import system, name
import math
import argparse
import sys

# bluetooth serial IO
import serial
ser = serial.Serial('/dev/rfcomm0', 57600, timeout=1)

# global variables
# 0 = fire detection
# 1 = azimuth to face
tx_data_flags = ["y", "25"]

def bluetooth_magnetometer():
    ser.write(b'initialize\r\n')
    while(ser.in_waiting <= 0):
        continue
    read_buffer = str(ser.readline())
    read_buffer = read_buffer[2:len(read_buffer)-5]
    if(read_buffer != "ack"):
        print("Bluetooth not initialized properly.")
    while(1):
        # Wait for data which should be the azimuth of magnetometer on arduino
        while(ser.in_waiting <= 0):
            continue
        read_buffer = str(ser.readline())
        read_buffer = read_buffer[2:len(read_buffer)-5]
        # send fire detection flag and azimuth to face
        tx_data = tx_data_flags[0] + "," + tx_data_flags[1]
        ser.write(tx_data.encode())
        # Empty IO buffers
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        print("Arduino Azimuth: " + read_buffer)


def main():
    try:
        _thread.start_new_thread(bluetooth_magnetometer, ())
    except:
        print('Error opening new thread.')
    while(1):
        pass

main()
