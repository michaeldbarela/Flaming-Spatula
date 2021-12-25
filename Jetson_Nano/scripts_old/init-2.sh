#!/bin/bash
# run with sudo

# Steps to fix any issues:
#   https://stackoverflow.com/questions/61981156/unable-to-locate-package-python-pip-ubuntu-20-04
#   The miniterm.py script needs python2 to be run as well as modules made for that version

# setup for BLE communication to HC-05

# one terminal 
# might need to setup with minicom -s also dmesg | grep tty
# minicom -D /dev/ttyACM0
# other terminal 
cd /home/michaeldbarela/Desktop/
rfcomm bind 0 00:20:10:08:81:6D 1
minicom -C flag_list.txt -D /dev/rfcomm0
# minicom -D /dev/rfcomm0

# some logic to get the data from file

# delete the file so that a new one can be made for a future run
rm flag_list.txt