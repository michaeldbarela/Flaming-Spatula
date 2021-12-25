#!/usr/bin/python3
#
# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#

# misc libraries
import _thread
from time import sleep
import math
from os import system, name
import argparse
import sys

# detectnet
sys.path.append('/home/jetson-nano/jetson-inference/build/aarch64/bin')
import jetson.inference
import jetson.utils

# bluetooth
import serial
ser = serial.Serial('/dev/rfcomm0', 57600, timeout=0)

# global variables
# 0 = fire detection
# 1 = azimuth from nano (direction to face)
# 2 = x1
# 3 = y1
# 4 = x2
# 5 = y2
# 6 = left or right
# 7 = distance
tx_data_vals = ["n", "361", "0", "1", "2", "3", "l", "10"]
# 0 = azimuth from arduino
# 1, 2, 3 = ultrasonic sensors
# 4 = fire detected by flame sensors
# 5 = 
rx_data_vals = ["0", "", "", "", "", ""]

def clear():
    _ = system('clear')

def ky_fire_detect(net, detections):
    detect = [0, 0]
    for detection in detections:
        if('flaming_spatula' == net.GetClassDesc(detection.ClassID)):
            detect[0] = detection
        if('non-lit_candle' == net.GetClassDesc(detection.ClassID)):
            detect[1] = detection
    return detect

def get_coordinates(detect):
    x1 = detect[0].Center[0]
    y1 = detect[0].Center[1]
    x2 = detect[1].Center[0]
    y2 = detect[1].Center[1] 
    tx_data_vals[2] = str(x1);
    tx_data_vals[3] = str(y1);
    tx_data_vals[4] = str(x2);
    tx_data_vals[5] = str(y2);
    return x1, y1, x2, y2

def set_relative_loc(coordinates):
    ky_coord = [coordinates[0], coordinates[1]]
    fire_coord = [coordinates[2], coordinates[3]]
    temp_x = ky_coord[0] - fire_coord[0]
    temp_y = ky_coord[1] - fire_coord[1]
    message = ''
    if(temp_x >= 0):
        message = message + 'left'
    else:
        message = message + 'right'
    if(temp_y < 0):
        message = message + ' and down'
    else:
        message = message + ' and up'
    return message
    
def get_angle(coordinates):
    angle = 0
    angle = math.atan2((coordinates[3]-coordinates[1]), (coordinates[2]-coordinates[0]))
    angle = int(math.degrees(angle))
    if(angle < 0):
        angle = angle + 360
    if(angle <= 270):
        angle = angle + 90
    else:
        angle = (angle + 90) - 360
    return angle
    
def get_l_or_r():
    azi_jetson = int(tx_data_vals[1])
    azi_arduino = int(rx_data_vals[0])
    # old logic
#    a = (azi_jetson+180)%360
#    print('left or right function a = ' + str(a))
#    if(azi_jetson > 180):
#        if((azi_arduino > azi_jetson) or (azi_arduino < a)):
#            tx_data_vals[6] = 'l'
#        else:
#            tx_data_vals[6] = 'r'
#    else:
#        if((azi_arduino < azi_jetson) or (azi_arduino > a)):
#            tx_data_vals[6] = 'l'
#        else:
#            tx_data_vals[6] = 'r'

    # new logic
    azi_diff = (azi_arduino-azi_jetson + 180 + 360) % 360 - 180
    if(azi_diff > 0):
        tx_data_vals[6] = 'l'
    else:
        tx_data_vals[6] = 'r'
    
#    print('Left or Right: ' + tx_data_vals[6])

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
        tx_data = str(tx_data_vals[0] + "," + tx_data_vals[1] + "," + tx_data_vals[2] + "," + tx_data_vals[3] + "," + tx_data_vals[4] + "," + tx_data_vals[5] + "," + tx_data_vals[6] + "," + tx_data_vals[7])
#        tx_data = tx_data_vals[0:1]
        ser.write(tx_data.encode())
        # Empty IO buffers
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        rx_data_vals[0] = str(read_buffer)

def main():    
    # Open new thread for bluetooth comm
    try:
        _thread.start_new_thread(bluetooth_magnetometer, ())
    except:
        print('Error opening new thread.')

	# parse the command line
    parser = argparse.ArgumentParser(description="Locate objects in a live camera stream using an object detection DNN.", formatter_class=argparse.RawTextHelpFormatter, epilog=jetson.inference.detectNet.Usage() + jetson.utils.videoSource.Usage() + jetson.utils.videoOutput.Usage() + jetson.utils.logUsage())

    parser.add_argument("input_URI", type=str, default="", nargs='?', help="URI of the input stream")
    parser.add_argument("output_URI", type=str, default="", nargs='?', help="URI of the output stream")
    parser.add_argument("--network", type=str, default="ssd-mobilenet-v2", help="pre-trained model to load (see below for options)")
    parser.add_argument("--overlay", type=str, default="box,labels,conf", help="detection overlay flags (e.g. --overlay=box,labels,conf)\nvalid combinations are:  'box', 'labels', 'conf', 'none'")
    parser.add_argument("--threshold", type=float, default=0.5, help="minimum detection threshold to use") 

    is_headless = ["--headless"] if sys.argv[0].find('console.py') != -1 else [""]

    try:
        opt = parser.parse_known_args()[0]
    except:
        print("")
        parser.print_help()
        sys.exit(0)

    # create video output object 
    output = jetson.utils.videoOutput(opt.output_URI, argv=sys.argv+is_headless)
	    
    # load the object detection network
    net = jetson.inference.detectNet(opt.network, sys.argv, opt.threshold)

    # create video sources
    input = jetson.utils.videoSource(opt.input_URI, argv=sys.argv)
    clear()
    
    clear_counter = 0
    detect = [0, 0]
    coordinates = [0, 0, 0, 0]
    relative_loc = ''
    
    # process frames until the user exits
    while True:
        # capture the next image
        img = input.Capture()

        # detect objects in the image (with overlay)
        detections = net.Detect(img, overlay=opt.overlay)

        detect = ky_fire_detect(net, detections)
        if(detect[0] != 0 and detect[1] != 0):
            coordinates = get_coordinates(detect)
            jetson.utils.cudaDrawLine(img, (coordinates[0],coordinates[1]), (coordinates[2],coordinates[3]), (255,0,200,200), 5)
            relative_loc = set_relative_loc(coordinates)
            tx_data_vals[0] = "y"
            tx_data_vals[1] = str(get_angle(coordinates))
            get_l_or_r()
        else:
            tx_data_vals[0] = "n"
            tx_data_vals[1] = "361"

        # render the image
        output.Render(img)

        # update the title bar
        output.SetStatus("{:s} | Network {:.0f} FPS".format(opt.network, net.GetNetworkFPS()))

        if(clear_counter >= 10):
            clear_counter = 0
            clear()
            print("detected {:d} objects in image".format(len(detections)))
            for detection in detections:
	            print(net.GetClassDesc(detection.ClassID))	
            print("Vehicle Coordinates = (" + str(coordinates[0]) + ", " + str(coordinates[1]) + ")")
            print("Lit Candle Coordinates = (" + str(coordinates[2]) + ", " + str(coordinates[3]) + ")")
            print("Arduino azimuth: " + str(rx_data_vals[0]))
            print("Angle that truck needs to face = " + str(tx_data_vals[1]))
            print(relative_loc)
            tx_data = tx_data_vals[0] + ","+ tx_data_vals[1]
            print(str(tx_data))
            print(str(tx_data_vals))
        else:
            clear_counter = clear_counter + 1

        # exit on input/output EOS
        if not input.IsStreaming() or not output.IsStreaming():
            break

main()

