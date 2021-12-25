import py_qmc5883l
import math
from os import system, name
from time import sleep

sensor = py_qmc5883l.QMC5883L()
#print(sensor.get_bearing())
#sensor.declination = 11.60
#print(sensor.get_bearing())

#sensor.calibration = [[1.139841045215691, -0.035190940226347944, 843.0365014520114], 			[-0.035190940226347944, 1.0088557853104163, 4722.011426906752], [0.0, 0.0, 1.0]]
sensor.declination = 11.60
#sensor.calibration = [[1.0949618278189537, 0.11913629789872908, -40.241010471353405], [0.1191362978987291, 1.1494648723914076, 45.03506458466989], [0.0, 0.0, 1.0]]
#sensor.calibration = [[2.756901236137457, -0.042039201436829, -745.9331375252375], [-0.042039201436829, 1.0010059156548445, 472.23058960629913], [0.0, 0.0, 1.0]]
sensor.calibration = [[1.5552220845488176, 0.3947498845160558, 78.49449159546141], [0.3947498845160558, 1.2806579126838358, -228.80020595386833], [0.0, 0.0, 1.0]]

def clear():
	_ = system('clear')

while True:
	clear()
	m = sensor.get_magnet()
	print(m)
	angle = math.atan2(m[1], m[0])

	if(angle > 2*math.pi):
	 	angle = angle - 2*math.pi
	if(angle < 0):
		angle = angle + 2*math.pi

	angle = angle*(180/math.pi)

	print(angle)
	sleep(0.1)
