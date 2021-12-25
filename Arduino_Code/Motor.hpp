#pragma once
#include <util/atomic.h> // For the ATOMIC_BLOCK macro
#include <Arduino.h>

// Pins
// motor 0
#define ENCA_0 2 // YELLOW
#define ENCB_0 8 // WHITE
#define PWM_0 5
#define IN2_0 53
#define IN1_0 52
// motor 1
#define ENCA_1 3 // YELLOW
#define ENCB_1 12 // WHITE
#define PWM_1 6
#define IN2_1 51
#define IN1_1 50
// Number of motors to use
#define NMOTORS 2

class Motor{
private:
	// pins declared as array constants
	int enca;
	int encb;
	int pwm;
	int in1;
	int in2;
	// Previous time used for PID algo
	long prevT;
	// Position on this motor
	volatile int posi;
	// PID and max PWM variables for PID algo
	float kp, kd, ki, umax;
	// Previous error and integral error
	float eprev, eintegral;

public:
	// Constructor
	Motor(int param[5]) : 
	kp(1), kd(0), ki(0), umax(255), eprev(0.0), eintegral(0.0) {
		enca = param[0];
		encb = param[1];
		pwm = param[2];
		in1 = param[3];
		in2 = param[4];
		posi = 0;
		prevT = 0;
	}

	// Interrupt function for adding to posi variable by checking encb value. Rotary encoder
	//	logic is what makes this useful.
	void readEncoder();
	// Intialize the motor with the parameters.
	//	param[0]: Proportional constant
	// 	param[1]: Derivative constant
	//	param[2]: Integral constant
	//	param[3]: Max PWM (0 to 255)
	void initialize(float param[4]);
	// A function to set the parameters on the PID algo
	//	0: Proportional constant
	//	1: Derivative constant
	//	2: Integral constant
	//	3: Max PWM (0 to 255)
	void setParams(float, float, float, float);
	// PID algorithm
	//	0: target position for the motor
	//	1: adjustment to PWM speed
	void PID_algorithm(int, float);
	// Computes the control signal
	//	0: Position of motor at time of function call
	//	1: Position the motor should be at
	//	2: Change in time
	//	3: PWM speed (0 to 255)
	//	4: Forward or backward  movement
	void evalu(int, int, float, int&, int&);
	// Sets the PWM on the motor
	//	0: Forward or backward movement
	// 	1: PWM speed (0 to 255)
	void setMotor(int, int);
};
