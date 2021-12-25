#include "Motor.hpp"

// Interrupt function for adding to posi variable by checking encb value. Rotary encoder
//	logic is what makes this useful.
void Motor::readEncoder(){
	int b = digitalRead(encb);
	if(b > 0){
		posi++;
	}else{
		posi--;
	}
}

// Intialize the motor with the parameters.
//	param[0]: Proportional constant
// 	param[1]: Derivative constant
//	param[2]: Integral constant
//	param[3]: Max PWM (0 to 255)
void Motor::initialize(float param [4]){
	pinMode(enca,INPUT);
	pinMode(encb,INPUT);
	pinMode(pwm,OUTPUT);
	pinMode(in1,OUTPUT);
	pinMode(in2,OUTPUT);
	setParams(param[0], param[1], param[2], param[3]);
}

// A function to set the parameters on the PID algo
//	0: Proportional constant
//	1: Derivative constant
//	2: Integral constant
//	3: Max PWM (0 to 255)
void Motor::setParams(float kpIn, float kdIn, float kiIn, float umaxIn){
	kp = kpIn; 
	kd = kdIn; 
	ki = kiIn;
	umax = umaxIn;
}

// PID algorithm
//	0: target position for the motor
//	1: adjustment to PWM speed
void Motor::PID_algorithm(int t, float adjust_pwm) {
	// set target position
	int target;
	ATOMIC_BLOCK(ATOMIC_RESTORESTATE){
		target = posi + t;
	}

	// time difference
	long currT = micros();
	float deltaT = ((float) (currT - prevT))/( 1.0e6 );
	prevT = currT;

	// Read the position in an atomic block to avoid a potential misread
	int pos;
	ATOMIC_BLOCK(ATOMIC_RESTORESTATE){
		pos = posi;
	}

	int pwr, dir;
	// evaluate the control signal
	evalu(pos, target, deltaT, pwr, dir);
	pwr = pwr * adjust_pwm;
	// signal the motor
	setMotor(dir, pwr);
}

// Computes the control signal
//	0: Position of motor at time of function call
//	1: Position the motor should be at
//	2: Change in time
//	3: PWM speed (0 to 255)
//	4: Forward or backward  movement
void Motor::evalu(int value, int target, float deltaT, int &pwr, int &dir){
	// error
	int e = target - value;
	// derivative
	float dedt = (e-eprev)/(deltaT);
	// integral
	eintegral = eintegral + e*deltaT;
	// control signal
	float u = kp*e + kd*dedt + ki*eintegral;

	// motor power
	pwr = (int) fabs(u);
	if( pwr > umax ){
		pwr = umax;
	}

	// motor direction
	dir = 1;
	if(u<0){
		dir = -1;
	}

	// store previous error
	eprev = e;
}

// Sets the PWM on the motor
//	0: Forward or backward movement
// 	1: PWM speed (0 to 255)
void Motor::setMotor(int dir, int pwmVal){
	analogWrite(pwm,pwmVal);
	if(dir == 1){
		digitalWrite(in1,HIGH);
		digitalWrite(in2,LOW);
	}else if(dir == -1){
		digitalWrite(in1,LOW);
		digitalWrite(in2,HIGH);
	}else{
		digitalWrite(in1,LOW);
		digitalWrite(in2,LOW);
	}  
}
