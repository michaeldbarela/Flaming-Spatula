#include "Magnetometer.hpp"

// Initialize the magnetometer (call during setup)
void Magnetometer::initialize(){
	magneto_compass.init();
	// Calibration done prior via other arduino program
	magneto_compass.setCalibration(-1352, 1488, -1262, 1597, -1728, 1365);
}

// Use QMC... library to get x, y, z values from magnetometer
//	0: x-value
//	1: y-value
//	2: z-value
void Magnetometer::get_xyz(int *x, int *y, int *z){
	(*x) = magneto_compass.getX();
	(*y) = magneto_compass.getY();
	(*z) = magneto_compass.getZ();
}

// Use QMC... library to get azimuth (0 to 360 degrees) from magnetometer
//	then adjust it to match nano orientation.
unsigned int Magnetometer::get_azimuth(){
	magneto_compass.read();
	// These values were detemined though testing. Keeps range from 0 to 360 degrees.
	unsigned int azimuth = magneto_compass.getAzimuth();
	if(azimuth >= 183){
		azimuth = azimuth - 183;
	}else{
		azimuth = azimuth + 177;
	}
	return azimuth;
}
