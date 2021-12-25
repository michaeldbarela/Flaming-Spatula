#pragma once
#include <Arduino.h>
#include <SoftwareSerial.h>

class Ultrasonic{
// private:
public:
  // constructor
  Ultrasonic(){};

  // ultrasonic sensors initialization
  void initialize();
  int UltraSensor(int, int);
  // returns the left ultrasonic sensor reading (in cm)
  int get_LUS();
  // returns the midle ultrasonic sensor reading (in cm)
  int get_MUS();
  // returns the left ultrasonic sensor reading (in cm)
  int get_RUS();
};
