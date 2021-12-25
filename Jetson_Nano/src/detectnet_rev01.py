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

# detectnet
import jetson.inference
import jetson.utils
from os import system, name
import math
import argparse
import sys

# magnetometer
import py_qmc5883l
from time import sleep
sensor = py_qmc5883l.QMC5883L()

# bluetooth
import miniterm
#bluetooth_comm = miniterm.main()

def clear():
	_ = system('clear')

def ky_fire_detect(net, detections):
	detect = [0, 0]
	for detection in detections:
		if('ky' == net.GetClassDesc(detection.ClassID)):
			detect[0] = detection
		if('fire' == net.GetClassDesc(detection.ClassID)):
			detect[1] = detection
	#print(detect)
	#print(net.GetClassDesc(detect[0].ClassID))
	#print(net.GetClassDesc(detect[1].ClassID))
	return detect

def get_coordinates(detect):
	x1 = detect[0].Center[0]
	y1 = detect[0].Center[1]
	x2 = detect[1].Center[0]
	y2 = detect[1].Center[1] 
	return x1, y1, x2, y2

#def set_relative_loc(coordinates):
#	direction = 'not detected'
#	angle = 0
#	relative_loc = [direction, angle]
#	third_point = [coordinates[0],coordinates[3]]
#	a_dot_b = coordinates[0]*third_point[0] + coordinates[1]*third_point[1]
#	mag_a = math.sqrt(coordinates[0]**2+coordinates[1]**2)
#	mag_b = math.sqrt(third_point[0]**2+third_point[1]**2)
#	x = a_dot_b/(mag_a*mag_b)
#	angle = math.acos(x)
#	angle = angle*(180/math.pi)
#	print(angle)
#	return relative_loc

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
		
def get_magnetometer_jet():
	m = sensor.get_magnet()
	print(m)
	angle = math.atan2(m[1], m[0])

	if(angle > 2*math.pi):
	 	angle = angle - 2*math.pi
	if(angle < 0):
		angle = angle + 2*math.pi

	angle = angle*(180/math.pi) + 11.60

	print(angle)
	# sleep(0.1)

def main():
	# parse the command line
	parser = argparse.ArgumentParser(description="Locate objects in a live camera stream using an object detection DNN.", 
		                             formatter_class=argparse.RawTextHelpFormatter, epilog=jetson.inference.detectNet.Usage() +
		                             jetson.utils.videoSource.Usage() + jetson.utils.videoOutput.Usage() + jetson.utils.logUsage())

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

	clear_counter = 0
	detect = [0, 0]
	coordinates = [0, 0, 0, 0]
#	relative_loc = ['not detected', 0]
	relative_loc = ''
	# process frames until the user exits
	# magnetometer calibration
	sensor.calibration = [[1.139841045215691, -0.035190940226347944, 843.0365014520114], 			[-0.035190940226347944, 1.0088557853104163, 4722.011426906752], [0.0, 0.0, 1.0]]
	while True:
		# capture the next image
		img = input.Capture()

		# detect objects in the image (with overlay)
		detections = net.Detect(img, overlay=opt.overlay)

		# print the detections
		# print("detected {:d} objects in image".format(len(detections)))
		
		#if(len(detections) > 1):
			#x1 = detections[0].Center[0]
			#y1 = detections[0].Center[1]
			#x2 = detections[1].Center[0]
			#y2 = detections[1].Center[1]
			#jetson.utils.cudaDrawLine(img, (x1,y1), (x2,y2), (255,0,200,200), 5)
			#for detection in detections:
			#	print(detection.Center[0])
			#	print(detection.Center[1])
			#	jetson.utils.cudaDrawLine(img, (25,150), (325,15), (255,0,200,200), 10)
		
		detect = ky_fire_detect(net, detections)
		if(detect[0] != 0 and detect[1] != 0):
			coordinates = get_coordinates(detect)
			jetson.utils.cudaDrawLine(img, (coordinates[0],coordinates[1]), (coordinates[2],coordinates[3]), (255,0,200,200), 5)
			relative_loc = set_relative_loc(coordinates)

		# render the image
		output.Render(img)

		
		# image_array = jetson.utils.cudaToNumpy(img)
		# pil_image = Image.fromarray(image_array, 'RGB')
		# pil_image.save("test.jpg")


		# update the title bar
		output.SetStatus("{:s} | Network {:.0f} FPS".format(opt.network, net.GetNetworkFPS()))

		# print out performance info
		# net.PrintProfilerTimes()
		
		if(clear_counter >= 10):
			clear_counter = 0
			clear()
			print("detected {:d} objects in image".format(len(detections)))
			for detection in detections:
				# print(detection)
				print(net.GetClassDesc(detection.ClassID))				
			print(relative_loc)
			get_magnetometer_jet()
			#bluetooth_comm = miniterm.main()
		else:
			clear_counter = clear_counter + 1

		# exit on input/output EOS
		if not input.IsStreaming() or not output.IsStreaming():
			break

main()

