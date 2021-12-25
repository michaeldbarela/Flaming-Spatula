#!/bin/bash

while getopts a:b: flag 
do
	case "${flag}" in
		a) data_directory=${OPTARG};;
		b) model_directory=${OPTARG};;
	esac
done

echo $1
echo $model_directory
echo $data_directory
