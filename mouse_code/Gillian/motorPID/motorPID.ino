#include <Encoder.h>
#include <SimplyAtomic.h>
#include <Adafruit_MCP3008.h>

Adafruit_MCP3008 adc1;
Adafruit_MCP3008 adc2;

const unsigned int ADC_1_CS = A3;
const unsigned int ADC_2_CS = A2;

//interrupt pins
const unsigned int M1_IN1 = 2;
const unsigned int M1_IN2 = 3;
const unsigned int M2_IN1 = 4;
const unsigned int M2_IN2 = 5;

//encoder pins
const unsigned int M1_ENCA = 6;
const unsigned int M1_ENCB = 7;
const unsigned int M2_ENCA = 8;
const unsigned int M2_ENCB = 9;

int M1_PWM = 25;

int prevTime = 0;
int prevReadM1 = 0;
int prevReadM2 = 0;
int targetVel = 0.3; //vel in m/s
//float prevVelM1 = 0;
//float prevVelM2 = 0;
float errorM1 = 0;
float integralM1 = 0;
float derivM1 = 0;
float prevErrorM1 = 0;

Encoder enc1(M1_ENCA, M1_ENCB);
Encoder enc2(M2_ENCA, M2_ENCB);

void M1_forward(unsigned int PWM) {
  analogWrite(M1_IN1, 0);
  analogWrite(M1_IN2, PWM);
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
  M1_forward(35); //M1 forward at PWM = 25 
  delay(1000);
}

void loop() {
  // put your main code here, to run repeatedly:
  /*
  //TODO: Add atomic block to update "prev" variables to be past "cur" variables
  ATOMIC(){
    prevReadM1 = curReadM1;
    prevReadM2 = curReadM2;
  }
*/
  
  long curTime = micros(); //time since Arduino started in microseconds
  int curReadM1 = enc1.read();
  int curReadM2 = enc2.read();
  float deltaTime = ((float) (curTime - prevTime))/1.0e6; //delta T in seconds
  prevTime = curTime;
  float curRotM1 = (curReadM1 - prevReadM1)/deltaTime;  //encoder counts/second
  float curRotM2 = (curReadM2 - prevReadM2)/deltaTime;  //encoder counts/second
  prevReadM1 = curReadM1;
  prevReadM2 = curReadM2;

  //convert counts/sec to vel in m/s
  float curVelM1 = curRotM1/360*0.032*M_PI;   //current measured velocity on M1
  float curVelM2 = curRotM2/360*0.032*M_PI;   //current measured velocity on M2

  /*
  Serial.print(curVelM1);
  Serial.println();
  */

  //PID coeffs
  float Kp = 10;
  float Ki = 0;
  float Kd = 0;

  //error signal e(t)
  errorM1 = targetVel - curVelM1;
  //integral signal (add error under the curve)
  integralM1 = integralM1 + errorM1*deltaTime;
  //derivative signal
  derivM1 = (errorM1 - prevErrorM1)/deltaTime;

  //corrected signal u(t)
  float uM1 = Kp*errorM1 + Ki*integralM1 + Kd*derivM1;

  //adjust PWM
  M1_PWM = M1_PWM + uM1;
  if (M1_PWM > 255)
    M1_PWM = 255;
  else if (M1_PWM < 0)
    M1_PWM = 0;

  M1_forward(M1_PWM);

  Serial.print(targetVel);
  Serial.print("   ");
  Serial.print(uM1);
  Serial.println();
}
