#include "Ultrasonic.hpp"

// pins
int trigPins[3] = {28,30,32};
int echoPins[3] = {29,31,33};

// sets initial state of trigPin
int trigState = LOW; 
// microsecond at which the pin was last written
unsigned long previousMillis = 0; 

// global variables 
long duration, distance, left_us_distance, middle_us_distance, right_us_distance;

// ultrasonic sensors initialization 
void Ultrasonic::initialize()
{
 for (int i = 0; i < 3; i++)
 {
   pinMode(trigPins[i], OUTPUT);
   pinMode(echoPins[i], INPUT);
 }
}

int Ultrasonic::UltraSensor(int trigPin,int echoPin)
{
  
  unsigned long currentMillis = millis(); // time in milliseconds from which the code was started
  if (currentMillis-previousMillis >= 2) { 
    previousMillis = currentMillis;
    if (trigState == LOW){
      (trigState = HIGH);
    }
    else {
      (trigState = LOW);
    }
  }  
  duration = 0;
  digitalWrite(trigPin,trigState);
  duration = pulseIn(echoPin, HIGH, 4000);
  distance = (duration/2) / 29.1;
}

// returns the left ultrasonic sensor reading (in cm)
int Ultrasonic::get_LUS()
{
  UltraSensor(trigPins[1], echoPins[1]);
  left_us_distance = distance;
  return left_us_distance;
}

// returns the middle ultrasonic sensor reading (in cm)
int Ultrasonic::get_MUS()
{
  UltraSensor(trigPins[2], echoPins[2]);
  middle_us_distance = distance;
  return middle_us_distance;
}

// returns the right ultrasonic sensor reading (in cm)
int Ultrasonic::get_RUS()
{
  UltraSensor(trigPins[3], echoPins[3]);
  right_us_distance = distance;
  return right_us_distance;
}
