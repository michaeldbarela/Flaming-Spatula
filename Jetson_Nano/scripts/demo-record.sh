#!/bin/bash

#ffmpeg -video_size 1919x1079 -framerate 30 -f x11grab -i :0.0+1,1 /home/jetson-nano/Desktop/demo2-jetson.mkv

ffmpeg -video_size 1919x1079 -framerate 30 -f x11grab -i :0.0+1,1 /home/jetson-nano/Desktop/demo2-jetson.mkv
