#include "Bluetooth.hpp"

// Initialize the connection with an acknowledgement message
void Bluetooth::initialize(){
	while(BT_data.equals("initialize\r\n") == 0){
		BT_data = BT_serial.readString();
	}
	transmit("ack");
}

// Transmit this particular data to the jetson nano
//	0: data transmitted to nano
void Bluetooth::transmit(String data){
	BT_serial.println(data);
}

// Gets RX data from nano and sends TX data to nano
//	0: magnetometer azimuth data
void Bluetooth::rxtx_data(int azimuth){
	// Transmit azimuth from arduino
	transmit(String(azimuth));
	// Receive all of the flags from the jetson nano
	BT_data = BT_serial.readString();
}

// Parse the data to get necessary values
String Bluetooth::parse_data(){
	unsigned int i = 0;
	while(i < BT_data.length()){
		if(BT_data.charAt(i) == ','){
			break;
		}else{
			i++;
		}
	}
	String parsed_data = BT_data.substring(0, i);
	BT_data.remove(0, i+1);
	return parsed_data;
}
