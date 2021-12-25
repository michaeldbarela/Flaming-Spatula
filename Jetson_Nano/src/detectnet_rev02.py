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
ser = serial.Serial('/dev/rfcomm0', 57600, timeout=2)

# global variables
angle = [0]
angle_arduino = [0]

def clear():
    _ = system('clear')

def ky_fire_detect(net, detections):
    detect = [0, 0]
    for detection in detections:
        if('flaming_spatula' == net.GetClassDesc(detection.ClassID)):
            detect[0] = detection
        if('lit_candle' == net.GetClassDesc(detection.ClassID)):
            detect[1] = detection
    return detect

def get_coordinates(detect):
    x1 = detect[0].Center[0]
    y1 = detect[0].Center[1]
    x2 = detect[1].Center[0]
    y2 = detect[1].Center[1] 
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
    angle = math.degrees(angle)
    if(angle < 0):
        angle = angle + 360
    if(angle <= 270):
        angle = angle + 90
    else:
        angle = (angle + 90) - 360
    return angle

def bluetooth_magnetometer():
    print("Bluetooth Thread Opened")
    while(1):
        ser.write(b'magnetometer')
        sleep(1)
        ser.write(str(angle[0]).encode())
        sleep(1)
        if(ser.in_waiting > 0):
            read_buffer = ser.readline()
            angle_arduino[0] = int(read_buffer)
        ser.reset_input_buffer()
        ser.reset_output_buffer()
    print("Bluetooth Thread Closed")

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
            angle[0] = get_angle(coordinates)

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
            print("Arduino angle: " + str(angle_arduino[0]))		
            print("Angle that truck needs to face = " + str(angle[0]))	
            print(relative_loc)
            # Open new thread for bluetooth comm
#            try:
#                _thread.start_new_thread(bluetooth_magnetometer, (angle,))
#            except:
#                print('Error opening new thread.')
        else:
            clear_counter = clear_counter + 1

        # exit on input/output EOS
        if not input.IsStreaming() or not output.IsStreaming():
            break

main()

