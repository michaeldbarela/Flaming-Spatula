#!/usr/bin/python3

# libraries
import _thread
from time import sleep
import struct
from os import system, name
import math
import argparse
import sys

# magnetometer
import py_qmc5883l
sensor = py_qmc5883l.QMC5883L()
#sensor.calibration = [[1.139841045215691, -0.035190940226347944, 843.0365014520114],[-0.035190940226347944, 1.0088557853104163, 4722.011426906752], [0.0, 0.0, 1.0]]
#sensor.calibration = [[2.756901236137457, -0.042039201436829, -745.9331375252375], [-0.042039201436829, 1.0010059156548445, 472.23058960629913], [0.0, 0.0, 1.0]]
#sensor.calibration = [[1.5552220845488176, 0.3947498845160558, 78.49449159546141], [0.3947498845160558, 1.2806579126838358, -228.80020595386833], [0.0, 0.0, 1.0]]
sensor.declination = 11.60
sensor.calibration = [[1.0949618278189537, 0.11913629789872908, -40.241010471353405], [0.1191362978987291, 1.1494648723914076, 45.03506458466989], [0.0, 0.0, 1.0]]

# bluetooth serial IO
import serial
ser = serial.Serial('/dev/rfcomm0', 57600, timeout=2)
#ser.baudrate = 115200
#ser.port = '/dev/rfcomm0'
#ser.open()
#ser.close()

def get_magnetometer_jet():
    m = sensor.get_magnet()
#    print(m)
    angle = math.atan2(m[1], m[0])

    if(angle > 2*math.pi):
     	angle = angle - 2*math.pi
    if(angle < 0):
	    angle = angle + 2*math.pi

    angle = angle*(180/math.pi)
#    angle = int(angle)
#    angle = str(angle)
#    print(angle)
    return angle

def bluetooth_magnetometer():
    while(1):
        angle = get_magnetometer_jet()
        angle = str(int(angle))
        print("Jetson Nano Azimuth: " + angle)
#        while(ser.in_waiting > 0):
#            continue
        ser.write(b'magnetometer')
#        ser.reset_input_buffer()
#        ser.reset_output_buffer()
        sleep(1)
#        while(ser.in_waiting > 0):
#            continue
        ser.write(angle.encode())
#        ser.write("this is a test\r\n".encode('ASCII'))
#        ser.reset_input_buffer()
#        ser.reset_output_buffer()
        sleep(1)
        if(ser.in_waiting > 0):
            read_buffer = ser.readline()
#            ser.reset_input_buffer()
#            ser.reset_output_buffer()
            print("Arduino Azimuth: " + str(read_buffer))
        ser.reset_input_buffer()
        ser.reset_output_buffer()

def bluetooth_receive():
    while(1):
        if(ser.in_waiting > 0):
#            while(ser.out_waiting > 0):
#                continue
            read_buffer = ser.readline()
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            print(read_buffer)

def main():
    try:
        _thread.start_new_thread(bluetooth_magnetometer, ())
#        _thread.start_new_thread(bluetooth_receive, ())
    except:
        print('Error opening new thread.')
    while(1):
        pass
#    sleep(5)
#    ser.close()

main()
