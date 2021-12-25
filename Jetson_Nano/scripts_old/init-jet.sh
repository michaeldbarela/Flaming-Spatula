#!/bin/bash

# change to directory with miniterm.py to start BLE comm
# cd /media/sf_micha/Desktop/CECS_490B/project
cd /media/sf_CECS_490B/Vehicle/src/mbarela

# run script from windows directory to begin everything
# gnome-terminal --window -- ./init.sh
konsole -e ./init.sh

# return to original directory where init.sh is located
# cd /home/michaeldbarela/Desktop/CECS_490
cd /media/sf_CECS_490B/Vehicle/src/mbarela

# sudo miniterm port=1 baudrate=57600
