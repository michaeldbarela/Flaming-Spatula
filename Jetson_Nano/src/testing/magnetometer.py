import smbus2
from time import sleep
import math
from os import system, name

# qmc5883l registers
X_axis_H = 0x01
Y_axis_H = 0x03
Z_axis_H = 0x05
Device_Address = 0x0d
# needed for calculations
declination = 11.60
# declination = 1
pi = math.pi

def clear():
	_ = system('clear')

def Magnetometer_Init():
	# setup in continuous mode
	bus.write_byte_data(Device_Address, 0x0B, 0x01)
	bus.write_byte_data(Device_Address, 0x09, 0x1D)

def read_raw_data(addr):
	high = bus.read_byte_data(Device_Address, addr)
	low = bus.read_byte_data(Device_Address, addr-1)
	value = ((high<<8) | low)
	#value = bus.read_word_data(Device_Address, addr-1)	
	if(value > 32768):
		value = value - 65536
	return value

bus = smbus2.SMBus(1)
Magnetometer_Init()
while True:
	clear()
	x = read_raw_data(X_axis_H)
	y = read_raw_data(Y_axis_H)
	z = read_raw_data(Z_axis_H)

	print("Raw Data x = %x" %x)
	print("Raw Data y = %x" %y)
	print("Raw Data z = %x" %z)
	heading = math.atan2(y, x) + declination
	print("Angle before correction = %f" %heading)	

	if(heading > 2*pi):
	 	heading = heading - 2*pi
	if(heading < 0):
		heading = heading + 2*pi


	heading_angle = int(heading * 180/pi)

	
	print("Heading Angle = %d" %heading_angle)
	sleep(0.1)
