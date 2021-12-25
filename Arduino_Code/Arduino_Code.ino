#include <math.h>
#include <SoftwareSerial.h>
#include <Wire.h>
#include <Servo.h>
#include "Bluetooth.hpp"
#include "Magnetometer.hpp"
#include "Motor.hpp"
#include "Ultrasonic.hpp"
#include "FlameSensor.hpp"

// global objects and variables
Bluetooth BT_serial;
Magnetometer magneto_compass;
Ultrasonic ultrasonic_sensor;
FlameSensor flame_sensor;
Servo myservo;

// global variables and pin for servo motor
// pos: orientation of the servo motor, initialized to 90 degrees (middle)
// aim counter: when it reaches 100, servo has locked on the fire
// target_acquired: flag to shoot the water
int pos = 90; 
int aim_counter = 0;
int target_acquired = 0;
int stop_car = 0;

int water1 = 40;
int water2 = 41;

// needed to instantiate the motors
int motor_pins [2][5] = {ENCA_0, ENCB_0, PWM_0, IN1_0, IN2_0, ENCA_1, ENCB_1, PWM_1, IN1_1, IN2_1};
// right motor, left motor
Motor motors [2] = {Motor(motor_pins[0]), Motor(motor_pins[1])};

// holds BT data that is received from the nano
String BT_data;
// holds the target position values meant for PID
//	0: current target0
//	1: current target1
unsigned long target[2] = {0,0};

// Interrupt cannot be called as a member function. This is a workaround.
// used for counting position of motor
void readEncoder_0(){
	motors[0].readEncoder();
}

// Interrupt cannot be called as a member function. This is a workaround.
// used for counting position of motor
void readEncoder_1(){
	motors[1].readEncoder();
}

// go forward
void go_forward(){
  /*
  target[0] = 408*5;
  target[1] = 408*5;
  pwm_pwr[0] = 1;
  pwm_pwr[1] = 0.8;
  */
  motors[0].PID_algorithm(-408*5, 1);
  motors[1].PID_algorithm(-408*5, 0.8);
}

// go left
void go_left(){
  /*
  target[0] = 408*5; 
  target[1] = -408*5;
  pwm_pwr[0] = 0.8;
  pwm_pwr[1] = 0.7;
  */
  motors[0].PID_algorithm(-408*5, 0.8);
  motors[1].PID_algorithm(408*5, 0.7);   
}

// go right
void go_right(){
  /*
  target[0] = -408*5; 
  target[1] = 408*5; 
  pwm_pwr[0] = 0.8;
  pwm_pwr[1] = 0.7;
  */
  motors[0].PID_algorithm(408*5, 0.8);
  motors[1].PID_algorithm(-408*5, 0.7);  
}

// go reverse
void go_reverse(){
  /*
  target[0] = 408*5;
  target[1] = 408*5;
  pwm_pwr[0] = 1;
  pwm_pwr[1] = 0.8;
  */
  motors[0].PID_algorithm(408*5, 1);
  motors[1].PID_algorithm(408*5, 0.8); 
}

// stop moving
void stop_moving(){
  motors[0].PID_algorithm(408*5, 0);
  motors[1].PID_algorithm(408*5, 0); 
}

// program initializations 
void setup(void){
	Serial.begin(115200);
	Serial.println("Attempting to initialize Bluetooth Communication");
	BT_serial.initialize();
	Serial.println("Bluetooth Communication Initialized");
	magneto_compass.initialize();
  ultrasonic_sensor.initialize();
  flame_sensor.initialize(); 
	float pid_vals [2][4] = {0.9, 0.1, 0, 255, 0.9, 0.1, 0, 255};
	motors[0].initialize(pid_vals[0]);
	attachInterrupt(digitalPinToInterrupt(ENCA_0), readEncoder_0, RISING);
	motors[1].initialize(pid_vals[1]);
	attachInterrupt(digitalPinToInterrupt(ENCA_1), readEncoder_1, RISING);
  //myservo.attach(9);
  //myservo.write(pos);
  pinMode(water1, OUTPUT);
  pinMode(water2, OUTPUT);
  pinMode(13, OUTPUT);
  
  digitalWrite(water1, HIGH);
  digitalWrite(water2, LOW);
}

// Logic flow should be:
//	1) Get BT Data
//    	* Works well, may need to update to also get truck detection
//  2) Get Ultrasonic Data
//    	* Add code
//  3) Get Flame Sensor Data
//    	* Add code
//  4) Determine target for PID algorithm
//		* Working on, nearly finished
//  5) Call PID Algorithm
//    	* Working on, nearly finished
//  6) Begin again at step 1
void loop(void){
	// holds slight adjustment for PWM speeds due to differences in motors
	// float pwm_pwr [2] = {1,0.8};
	// azimuth received from magnetometer
	int azimuth;
	// conversion of angle from nano and magnetometer azimuth to determine when to go straight
	int azi_diff;
	// following are the flags to be received from nano (parsed from BT_data)
	char fire_detected = 'n';
	char l_or_r = 'n';
	unsigned int azimuth_nano = 0;
	unsigned int x1, y1, x2, y2 = 0;
	unsigned int distance = 0;
  
  // ultrasonic sensor readings
  int LUS_detect;
  int MUS_detect;
  int RUS_detect;
  int US_detect;
  int LUS_binary;
  int MUS_binary;
  int RUS_binary;
  
  // flame sensor detection, (1) for yes (0) for no
  int LFS_detect;
  int MFS_detect;
  int RFS_detect;
  int FS_detect;
  
  // stop car flag
  
  
  // next state (FSM) for search and destroy (finding and extinguishing the fire)
  int search_and_destroy;
  
	// get magnetometer data
	azimuth = magneto_compass.get_azimuth();

	// send and receive magnetometer data to/from Jetson Nano
	BT_serial.rxtx_data(azimuth);
	// parse the data to extract all the flags
	fire_detected = BT_serial.parse_data().charAt(0);  
	azimuth_nano = BT_serial.parse_data().toInt();
	x1 = BT_serial.parse_data().toInt();
	y1 = BT_serial.parse_data().toInt();
	x2 = BT_serial.parse_data().toInt();
	y2 = BT_serial.parse_data().toInt();
	l_or_r = BT_serial.parse_data().charAt(0);
	distance = BT_serial.parse_data().toInt();

  // determine how much to turn based on the difference in degrees
  azi_diff = (azimuth - azimuth_nano + 180 + 360) % 360 - 180;
  azi_diff = abs(azi_diff);  

	// get ultrasonic data (in cm)
  LUS_detect = ultrasonic_sensor.get_LUS();
  MUS_detect = ultrasonic_sensor.get_MUS();
  RUS_detect = ultrasonic_sensor.get_RUS(); 
  
	// get flame sensor data (1 or 0 / high or low)
  LFS_detect = flame_sensor.get_LFS();
  MFS_detect = flame_sensor.get_MFS();
  RFS_detect = flame_sensor.get_RFS();
  
  // only considers objects detected within 2-10 cm
  // sets a value of 1 or 0
  LUS_binary = LUS_detect > 2 && LUS_detect < 10;
  MUS_binary = MUS_detect > 2 && MUS_detect < 10;
  RUS_binary = RUS_detect > 2 && RUS_detect < 10;

  // ultrasonic detection check and
  // flame sensor detection check
  US_detect = LUS_binary || MUS_binary || RUS_binary;
  FS_detect = LFS_detect || MFS_detect || RFS_detect;

  // stop car flag
  // if the ultrasonics detect the candle AND
  // the flame sensors detect the fire
  // the lit candle has been found
  if(US_detect && FS_detect == 1){
    stop_moving();
    stop_car = 1;
  }

  // check for switching between the 
  // ultrasonics for obstacle avoidance
  // and the flame sensors for aiming 
  if(!stop_car){
    search_and_destroy = stop_car*8 + LUS_binary*4 + MUS_binary*2 + RUS_binary;
  }else{
    search_and_destroy = stop_car*8 + LFS_detect*4 + MFS_detect*2 + RFS_detect;
  }

  if(target_acquired == 0){
    // FSM for search and destroy (finding and extinguishing the fire)
    // if the MSB is 0, the car hasn't stopped and must continue searching 
    // for the fire while avoiding obstacles using the ultrasonic sensors
    // if the MSB is 1, the car has stopped and must aim the turret on the fire
    // using the flame sensors
    switch(search_and_destroy){
      
      //     SLMR: stop bit, left sensor, middle sensor, right sensor
      case 0b0000: if(azi_diff < 15) go_forward();
                   else if(l_or_r == 'l') go_left();
                   else if(l_or_r == 'r') go_right();
                   break;
                 
                   // right sensor detects an object
      case 0b0001: go_reverse();
                   delay(1000);
                   go_left();
                   delay(1000);
                   go_forward();
                   delay(1000);
                   break;
                 
                   // middle sensor detects an object
      case 0b0010: go_reverse();
                   delay(1000);
                   go_left();
                   delay(1000);
                   go_forward();
                   delay(1000);
                   break;

                   // right & middle sensors detect an object
      case 0b0011: go_reverse();
                   delay(1000);
                   go_left();
                   delay(2000);
                   go_forward();
                   delay(2000);
                   break;
                 
                   // left sensor detects an object
      case 0b0100: go_reverse();
                   delay(1000);
                   go_right();
                   delay(1000);
                   go_forward();
                   delay(1000);
                   break;

                   // left & right sensors detect an object
      case 0b0101: go_reverse();
                   delay(1000);
                   go_left();
                   delay(2500);
                   go_forward();
                   delay(2500);
                   break;

                   // left & middle sensors detect an object
      case 0b0110: go_reverse();
                   delay(1000);
                   go_right();
                   delay(2000);
                   go_forward();
                   delay(2000);
                   break;

                   // all three sensors detect an object
      case 0b0111: go_reverse();
                   delay(1000);
                   go_left();
                   delay(2500);
                   go_forward();
                   delay(2500);
                   break;

                   // car has stopped, no fire currently detected
      case 0b1000: aim_counter = 0;
                   break;

                   // fire is on the right, so rotate right
      case 0b1001: aim_counter = 0;
                   //pos -=2;
                   go_right();
                   delay(1000);
                   stop_moving();
                   break;

                   // fire is in the middle
      case 0b1010: aim_counter += 1;
                   if(aim_counter >= 50) target_acquired = 1;
                   break;             

                   // fire is slightly on the right, so rotate right
      case 0b1011: aim_counter = 0;
                   //pos -= 1;
                   go_right();
                   delay(500);
                   stop_moving();
                   break;

                   // fire is on the left, so rotate left
      case 0b1100: aim_counter = 0;
                   //pos += 2;
                   go_left();
                   delay(1000);
                   stop_moving();
                   break;

                   // fire is in the middle
      case 0b1101: aim_counter += 1;
                   if(aim_counter >= 50) target_acquired = 1;
                   break;         

                   // fire is slightly on the left, so rotate left
      case 0b1110: aim_counter = 0;
                   //pos += 1;
                   go_left();
                   delay(500);
                   stop_moving();
                   break;    
                 
                   // fire is in the middle
      case 0b1111: aim_counter += 1;
                   if(aim_counter >= 50) target_acquired = 1;
                   break;

      default: Serial.println("default");
    }
  }
  

  // updates the position of the turret
  //delay(10);
  //myservo.write(pos);

  // checks if the turret has successfuly locked on to the fire
  else if(target_acquired == 1){
    //Serial.println("SPRAY RATATATATATATA!");
    analogWrite(13, 255);
  }
  
	// Print all of the data (debugging purposes)
	Serial.println("----- New Set of Data -----");
	Serial.print("Azimuth from Arduino: ");
	Serial.println(azimuth);
	Serial.print("Fire Detected: ");
	Serial.println(fire_detected);
	Serial.print("Azimuth needed to point to from Jetson Nano: ");
	Serial.println(azimuth_nano);
	Serial.print("Distance from vehicle to fire: ");
	Serial.println(distance);
	Serial.print("x-coordinates and y-coordinates: ");
	Serial.println("x = (" + String(x1) + ", " + String(y1) + "), y = (" + String(x2) + ", " + String(y2) + ")");
	Serial.print("Left or Right: ");
	Serial.println(l_or_r);
	Serial.print("The truck will turn by this many degrees: ");
	Serial.println(azi_diff);
	Serial.print("The truck will turn with this target: ");
	Serial.println(target[1]);
	
	// PID Algorithm
	// motors[0].PID_algorithm(-target[0], pwm_pwr[0]);
	// motors[1].PID_algorithm(-target[1], pwm_pwr[1]);
}
