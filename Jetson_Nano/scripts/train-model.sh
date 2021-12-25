#!/bin/bash

while getopts a:b: flag
do
	case "${flag}" in
		a) data_directory=${OPTARG};;
		b) model_directory=${OPTARG};;
	esac
done

cd /home/jetson-nano/jetson-inference/python/training/detection/ssd

python3 train_ssd.py --dataset-type=voc --data=/home/jetson-nano/jetson-inference/python/training/detection/ssd/data/$data_directory --model-dir=/home/jetson-nano/jetson-inference/python/training/detection/ssd/models/$model_directory --batch-size=4 --epochs=200

python3 onnx_export.py --model-dir=/home/jetson-nano/jetson-inference/python/training/detection/ssd/models/$model_directory


cd /home/jetson-nano/Desktop/scripts
