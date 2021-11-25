//Uses motor encoder to determine current velocity + positional set points
#include <Encoder.h>
//#include <SimplyAtomic.h>
#include <Adafruit_MCP3008.h>

Adafruit_MCP3008 adc1;
Adafruit_MCP3008 adc2;

const unsigned int ADC_1_CS = A3;
const unsigned int ADC_2_CS = A2;

//interrupt pins
const unsigned int M1_IN1 = 2;
const unsigned int M1_IN2 = 3;
const unsigned int M2_IN1 = 5;
const unsigned int M2_IN2 = 4;

//encoder pins
const unsigned int M1_ENCA = 6;
const unsigned int M1_ENCB = 7;
const unsigned int M2_ENCA = 8;
const unsigned int M2_ENCB = 9;

int M1_PWM = 0;
int M2_PWM = 0;

int prevTime = 0;
int prevReadM1 = 0;
int prevReadM2 = 0;
float targetDeltaRead = 0; //desired change in position in encoder counts, will be const and det. by target vel
float curVelM1, curVelM2;
float targetVel = 0.3; //vel in m/s
//float prevVelM1 = 0;
//float prevVelM2 = 0;
float errorM1 = 0;
float integralM1 = 0;
float derivM1 = 0;
float prevErrorM1 = 0;
float errorM2 = 0;
float integralM2 = 0;
float derivM2 = 0;
float prevErrorM2 = 0;

Encoder enc1(M1_ENCA, M1_ENCB);
Encoder enc2(M2_ENCA, M2_ENCB);

void M1_forward(unsigned int PWM) {
  analogWrite(M1_IN1, 0);
  analogWrite(M1_IN2, PWM);
}

void M1_stop() {
  analogWrite(M1_IN1, 0);
  analogWrite(M1_IN2, 0);
}

void M2_forward(unsigned int PWM) {
  analogWrite(M2_IN1, 0);
  analogWrite(M2_IN2, PWM);
}

void M2_stop() {
  analogWrite(M2_IN1, 0);
  analogWrite(M2_IN2, 0);
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  adc1.begin(ADC_1_CS);  
  adc2.begin(ADC_2_CS);  

  pinMode(M1_IN1, OUTPUT);
  pinMode(M1_IN2, OUTPUT);
  pinMode(M2_IN1, OUTPUT);
  pinMode(M2_IN2, OUTPUT);
  //M1_forward(35); //M1 forward at PWM = 35 
  delay(5000);
  prevReadM1 = enc1.read();
  prevReadM2 = -1*enc2.read();
  prevTime = micros();
}

void loop() {
  // put your main code here, to run repeatedly:
  long curTime = micros(); //time since Arduino started in microseconds
  int curReadM1 = enc1.read();
  int curReadM2 = -1*enc2.read();
  float deltaTime = ((float) (curTime - prevTime))/1.0e6; //delta T [s]
  targetDeltaRead = targetVel*deltaTime/(0.032*M_PI)*360; //target change in encoder position for desired velocity [counts]
  targetReadM1 = curReadM1 + targetDeltaRead; //target encoder position based on desired vel [counts]
  targetReadM2 = curReadM2 + targetDeltaRead; //target encoder position based on desired vel [counts]

  /*
  float curRotM1 = (curReadM1 - prevReadM1)/deltaTime;  //encoder counts/second
  float curRotM2 = (curReadM2 - prevReadM2)/deltaTime;  //encoder counts/second
  //convert current measured velocity in counts/sec to vel in m/s
  curVelM1 = curRotM1/360*0.032*M_PI;   //current measured velocity on M1
  curVelM2 = curRotM2/360*0.032*M_PI;   //current measured velocity on M2
  */

  //update stored values
  prevTime = curTime;
  //prevReadM1 = curReadM1;
  //prevReadM2 = curReadM2;

  //PID coeffs
<<<<<<< Updated upstream
  float KpM1 = 5;
  float KiM1 = 0;
  float KdM1 = 0;
  
  float KpM2 = 5;
=======
  float KpM1 = 0;
  float KiM1 = 0;
  float KdM1 = 0;
  
  float KpM2 = 0;
>>>>>>> Stashed changes
  float KiM2 = 0;
  float KdM2 = 0;

  //error signal e(t)
  errorM1 = targetReadM1 - curReadM1;
  //integral signal (add error under the curve)
  integralM1 = integralM1 + errorM1*deltaTime;
  //derivative signal
  derivM1 = (errorM1 - prevErrorM1)/deltaTime;

  errorM2 = targetReadM2 - curReadM2;
  integralM2 = integralM2 + errorM2*deltaTime;
  derivM2 = (errorM2 - prevErrorM2)/deltaTime;

  //corrected control signals u(t)
  float uM1 = KpM1*errorM1 + KiM1*integralM1 + KdM1*derivM1;
  float uM2 = KpM2*errorM2 + KiM2*integralM2 + KdM1*derivM2;

  //update stored error value
  prevErrorM1 = errorM1;
  prevErrorM2 = errorM2;

  //adjust PWM on M1
  M1_PWM = M1_PWM + uM1;
  if (M1_PWM > 255)
    M1_PWM = 255;
  else if (M1_PWM < 0)
    M1_PWM = 0;

  //adjust PWM on M2
  M2_PWM = M2_PWM + uM2;
  if (M2_PWM > 255)
    M2_PWM = 255;
  else if (M2_PWM < 0)
    M2_PWM = 0;

  M1_forward(M1_PWM);
  M2_forward(M2_PWM);

  Serial.print("curVelM1:");
  Serial.print(curVelM1);
  Serial.print(" ");
  Serial.print("curVelM2:");
  Serial.print(curVelM2);
  Serial.print(" ");
  Serial.print("targetVel:");
  Serial.print(targetVel);
  Serial.println();

  delay(10);
}

void pidM1(){
  
}

void pidM2(){
  
}
