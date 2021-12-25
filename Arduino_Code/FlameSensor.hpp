#pragma once
#include <Arduino.h>
#include <SoftwareSerial.h>

class FlameSensor{
// private:
public:
  // constructor
  FlameSensor(){};

  // flame sensors initialization
  void initialize();
  // returns the left flame sensor reading
  // returns a 1 for fire detected, 0 for no fire detected 
  int get_LFS();
  // returns the middle flame sensor reading
  // returns a 1 for fire detected, 0 for no fire detected
  int get_MFS();
  // returns the right flame sensor reading
  // returns a 1 for fire detected, 0 for no fire detected
  int get_RFS();   
};
