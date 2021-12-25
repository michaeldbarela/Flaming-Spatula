#!/bin/bash

while getopts a: flag 
do
	case "${flag}" in
		a) model_directory=${OPTARG};;
	esac
done

# open rfcomm port for bluetooth comm to hc-05
rfcomm bind 0 00:20:10:08:81:6D 1

#cd /home/jetson-nano/jetson-inference/build/aarch64/bin
cd /home/jetson-nano/Desktop/CECS490/src
# start detectnet script
python3 detectnet_rev04.py --model=/home/jetson-nano/jetson-inference/python/training/detection/ssd/models/$model_directory/ssd-mobilenet.onnx --labels=/home/jetson-nano/jetson-inference/python/training/detection/ssd/models/$model_directory/labels.txt --input-blob=input_0 --output-cvg=scores --output-bbox=boxes /dev/video2

rfcomm release 0

cd /home/jetson-nano/Desktop/CECS490/scripts
