#include "FlameSensor.hpp"

// flame sensor connections
int left_flame_sensor = 22;
int middle_flame_sensor = 23;
int right_flame_sensor = 24;

// flame sensors initialization
void FlameSensor::initialize(){
  pinMode(left_flame_sensor, INPUT);
  pinMode(middle_flame_sensor, INPUT);
  pinMode(right_flame_sensor, INPUT);
}

// returns the left flame sensor reading
// returns a 1 for fire detected, 0 for no fire detected
int FlameSensor::get_LFS(){
  return (!digitalRead(left_flame_sensor));
}

// returns the middle flame sensor reading
// returns a 1 for fire detected, 0 for no fire detected
int FlameSensor::get_MFS(){
  return (!digitalRead(middle_flame_sensor));
}

// returns the right flame sensor reading
// returns a 1 for fire detected, 0 for no fire detected
int FlameSensor::get_RFS(){
  return (!digitalRead(right_flame_sensor));
}
