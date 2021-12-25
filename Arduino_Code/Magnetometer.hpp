#pragma once
#include <Arduino.h>
#include <QMC5883LCompass.h>
#include <Wire.h>
#include <math.h>

class Magnetometer{
private:	
	// magnetometer object
	QMC5883LCompass magneto_compass;

public:
	// Constructor
	Magnetometer(){};

	// Initialize the magnetometer (call during setup)
	void initialize();
	// Use QMC... library to get x, y, z values from magnetometer
	//	0: x-value
	//	1: y-value
	//	2: z-value
	void get_xyz(int*, int*, int*);
	// Use QMC... library to get azimuth (0 to 360 degrees) from magnetometer
	//	then adjust it to match nano orientation.
	unsigned int get_azimuth();
};
