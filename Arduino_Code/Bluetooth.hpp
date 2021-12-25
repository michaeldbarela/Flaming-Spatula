#pragma once
#include <Arduino.h>
#include <SoftwareSerial.h>

// Pins
#define RX 10
#define TX 11

class Bluetooth{
private:
	// Data received from nano
	String BT_data;
	// Bluetooth object
	SoftwareSerial BT_serial;

public:
	// Constructor
	Bluetooth(): BT_serial(RX, TX){
		// Sets the baud rate to 57600
		BT_serial.begin(57600);
		// Need the timeout or else the readString() function hangs for 1 second
		BT_serial.setTimeout(100);
	};

	// Initialize the connection with an acknowledgement message
	void initialize();
	// Transmit this particular data to the jetson nano
	//	0: data transmitted to nano
	void transmit(String);
	// Gets RX data from nano and sends TX data to nano
	//	0: magnetometer azimuth data
	void rxtx_data(int);
	// Parse the data to get necessary values
	String parse_data(); 
};
