//Uses IMU accelerometer to determine current velocity

//#include <Encoder.h>
#include <Arduino_LSM9DS1.h>
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
float curAccelXM1 = 0;
float curAccelYM1 = 0;
float curAccelZM1 = 0;
//float prevAccelM2 = 0;
float targetVel = 0.5; //vel in m/s
float prevVelM1 = 0;
//float prevVelM2 = 0;
float errorM1 = 0;
float integralM1 = 0;
float derivM1 = 0;
float prevErrorM1 = 0;

//Encoder enc1(M1_ENCA, M1_ENCB);
//Encoder enc2(M2_ENCA, M2_ENCB);

void M1_forward(unsigned int PWM) {
  analogWrite(M1_IN1, 0);
  analogWrite(M1_IN2, PWM);
}

void M1_stop() {
  analogWrite(M1_IN1, 0);
  analogWrite(M1_IN2, 0);
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  adc1.begin(ADC_1_CS);  
  adc2.begin(ADC_2_CS);  

  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (1);
  }

  pinMode(M1_IN1, OUTPUT);
  pinMode(M1_IN2, OUTPUT);
  pinMode(M2_IN1, OUTPUT);
  pinMode(M2_IN2, OUTPUT);
  M1_forward(35); //M1 forward at PWM = 35 
  delay(5000);
  //prevReadM1 = enc1.read();
  prevTime = micros();
  //M1_stop();
}

void loop() {
  /*
  //TODO: Add atomic block to update "prev" variables to be past "cur" variables
  ATOMIC(){
    prevReadM1 = curReadM1;
    prevReadM2 = curReadM2;
  }
*/
  
  long curTime = micros(); //time since Arduino started in microseconds
  if(IMU.accelerationAvailable()){
    IMU.readAcceleration(curAccelXM1, curAccelYM1, curAccelZM1); //reads acceleration in m/s^2
  }
  /*Serial.print("prevReadM1: ");
  Serial.print(prevReadM1);
  Serial.print("   curReadM1: ");
  Serial.print(curReadM1);
  Serial.println();*/
  //int curReadM2 = enc2.read();
  float deltaTime = ((float) (curTime - prevTime))/1.0e6; //delta T in seconds
  /*Serial.print("deltaT: ");
  Serial.print(deltaTime);
  Serial.println();*/
  float curAccelM1 = sqrt(pow(curAccelXM1,2)+pow(curAccelYM1,2)); //magnitude of acceleration
  /*Serial.print("curRotM1: ");
  Serial.print(curRotM1);
  Serial.println();*/
  //float curRotM2 = (curReadM2 - prevReadM2)/deltaTime;  //encoder counts/second

  //update stored values
  prevTime = curTime;
  prevReadM1 = curReadM1;
  prevReadM2 = curReadM2;

  //integrate acceleration to determine velocity
  float curVelM1 = prevVelM1 + curAccelM1*deltaTime;   //current measured velocity on M1
  Serial.println();
  Serial.print("curVel:");
  Serial.print(curVelM1);
  Serial.print(" ");
  //float curVelM2 = curRotM2/360*0.032*M_PI;   //current measured velocity on M2

  /*
  Serial.print(curVelM1);
  Serial.println();
  */

  //PID coeffs
  float Kp = 4;
  float Ki = 0.1;
  float Kd = 0;

  //error signal e(t)
  errorM1 = targetVel - curVelM1;
  /*Serial.print("errorM1:");
  Serial.print(errorM1);
  Serial.print(" ");*/
  //integral signal (add error under the curve)
  integralM1 = integralM1 + errorM1*deltaTime;
  /*Serial.print("integralM1:");
  Serial.print(integralM1);
  Serial.print(" ");*/
  //derivative signal
  derivM1 = (errorM1 - prevErrorM1)/deltaTime;
  /*
  Serial.print("derivM1:");
  Serial.print(derivM1);
  Serial.print(" ");*/

  //corrected signal u(t)
  float uM1 = Kp*errorM1 + Ki*integralM1 + Kd*derivM1;

  //update stored error value
  prevErrorM1 = errorM1;

  //adjust PWM
  M1_PWM = M1_PWM + uM1;
  if (M1_PWM > 255)
    M1_PWM = 255;
  else if (M1_PWM < 0)
    M1_PWM = 0;

  M1_forward(M1_PWM);

  Serial.print("targetVel:");
  Serial.print(targetVel);
  /*Serial.print("   ");
  Serial.print("uM1:");
  Serial.print(uM1);*/
  Serial.println(); 
  Serial.println();

  delay(10);
}
