//For C's mouse (different threshold and PWM values)
//Uses motor encoder to determine current velocity + positional set points
#include <Encoder.h>
//#include <SimplyAtomic.h>
#include <Adafruit_MCP3008.h>

Adafruit_MCP3008 adc1;
Adafruit_MCP3008 adc2;

const unsigned int ADC_1_CS = A3;
const unsigned int ADC_2_CS = A2;
const unsigned int RF_CS = A4;

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

int adc1_buf[8];
int adc2_buf[8];

bool arr[16];
const unsigned int BUF_THRESHOLD = 600; //for G: 550, for C: 600, for D: 710

int prevTime = 0;
int prevReadM1 = 0;
int prevReadM2 = 0;
float targetDeltaRead = 0; //desired change in position in encoder counts, will be const and det. by target vel
float targetRead;
float curVelM1, curVelM2;
float targetVel = 0.2; //vel in m/s
float errorM1 = 0;
float integralM1 = 0; //CHANGE THIS VALUE (either incr or decr, but keep it greater than 0)
float derivM1 = 0;
float prevErrorM1 = 0;
float errorM2 = 0;
float integralM2 = 0;
float derivM2 = 0;
float prevErrorM2 = 0;
float errorLimit = 150; //limit to ramp position up instead of trying to do so instantaneously
int stopFlag = 0; //flag for when motor is stopped

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

  pinMode(RF_CS, OUTPUT);
  digitalWrite(RF_CS, HIGH); // Without this the nRF24 will write to the SPI bus while the ADCs are also talking

  pinMode(M1_IN1, OUTPUT);
  pinMode(M1_IN2, OUTPUT);
  pinMode(M2_IN1, OUTPUT);
  pinMode(M2_IN2, OUTPUT);
  //M1_forward(35); //M1 forward at PWM = 35 
  delay(5000);
  prevReadM1 = enc1.read();
  prevReadM2 = -1*enc2.read();
  targetRead = 0;
  prevTime = micros();
}

void loop() {
  // put your main code here, to run repeatedly:
  long curTime = micros(); //time since Arduino started in microseconds
  int curReadM1 = enc1.read();
  int curReadM2 = -1*enc2.read();
  float deltaTime = ((float) (curTime - prevTime))/1.0e6; //delta T [s]
  targetDeltaRead = targetVel*deltaTime/(0.032*M_PI)*360; //target change in encoder position for desired velocity [counts]
  if (stopFlag == 0){  //only change target position if previous time doesn't have stopped motors
    targetRead = targetRead + targetDeltaRead; //target encoder position based on desired vel [counts]
  } else { //if motors were stopped at previous time, 
    targetRead = (curReadM1 + curReadM2)/2;
  }
  //if the stop flag is high, the targetRead won't change from the previous

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
  float KpM1 = 0.2;
  float KiM1 = 0.05;
  float KdM1 = 0.1;
  
  float KpM2 = 0.2;
  float KiM2 = 0.05;
  float KdM2 = 0.1;

  errorM1 = targetRead - curReadM1;
  if (errorM1 > errorLimit)
    errorM1 = errorLimit;
  integralM1 = integralM1 + errorM1*deltaTime;
  derivM1 = (errorM1 - prevErrorM1)/deltaTime;

  errorM2 = targetRead - curReadM2;
  if (errorM2 > errorLimit)
    errorM2 = errorLimit;
  integralM2 = integralM2 + errorM2*deltaTime;
  derivM2 = (errorM2 - prevErrorM2)/deltaTime;

  //corrected control signals u(t)
  float uM1 = 0;
  float uM2 = 0;
  if (stopFlag == 0){  //only have nonzero signal if previous time didn't have stopped motors
    uM1 = KpM1*errorM1 + KiM1*integralM1 + KdM1*derivM1;
    uM2 = KpM2*errorM2 + KiM2*integralM2 + KdM2*derivM2;
  }
  

  //update stored error value
  prevErrorM1 = errorM1;
  prevErrorM2 = errorM2;

  //adjust PWM on M1
  M1_PWM = uM1;
  if (M1_PWM > 255)
    M1_PWM = 255;
  else if (M1_PWM < 0)
    M1_PWM = 0;

  //adjust PWM on M2
  M2_PWM = uM2;
  if (M2_PWM > 255)
    M2_PWM = 255;
  else if (M2_PWM < 0)
    M2_PWM = 0;

  //follow the line
  int t_start = micros();
  for (int i = 0; i < 8; i++) {
    adc1_buf[i] = adc1.readADC(i);
    adc2_buf[i] = adc2.readADC(i);
  }
  int t_end = micros();

  int count = 0;
  for (int i = 0; i < 8; i++) {
    if (adc1_buf[i] < BUF_THRESHOLD) {
      arr[count] = true;
      Serial.print("AH"); Serial.print("\t");
    } else {
      arr[count] = false;
      Serial.print("--"); Serial.print("\t");
    }

    count = count + 1;

    if (adc2_buf[i] < BUF_THRESHOLD) {
      arr[count] = true;
      Serial.print("AH"); Serial.print("\t");
    } else {
      arr[count] = false;
      Serial.print("--"); Serial.print("\t");
    }

    count = count + 1;
  }
  

  stopFlag = 0; //reset flag before checking light bar
  if (arr[6] == true){
    Serial.print("forward");
  } else if (arr[5] == true || arr[4] == true || arr[3] == true || arr[2] == true || arr[1] == true || arr[0] == true){ //too far to the right --> turn left
    M1_PWM += 10;
    M2_PWM -= 10;
    Serial.print("turn left");
  } else if (arr[7] == true || arr[8] == true || arr[9] == true || arr[10] == true || arr[11] == true || arr[12] == true){ //too far to the left --> turn right
    M2_PWM += 10;
    M1_PWM -= 10;
    Serial.print("turn right");
  } else if (!(arr[0] || arr[1] || arr[2] || arr[3] || arr[4] || arr[5] || arr[6] || arr[7] || arr[8] || arr[9] || arr[10] || arr[11] || arr[12])){ //stop if can't see line
    M1_PWM = 0;
    M2_PWM = 0;
    stopFlag = 1;
    Serial.print("stop");
  }
  Serial.println();
  
  M1_forward(M1_PWM);
  M2_forward(M2_PWM);

  curVelM1 = (curReadM1 - prevReadM1)/deltaTime/360*0.032*M_PI;
  curVelM2 = (curReadM2 - prevReadM2)/deltaTime/360*0.032*M_PI;
  prevReadM1 = curReadM1;
  prevReadM2 = curReadM2;
  //prevTargetReadM1 = targetReadM1;
  //prevTargetReadM2 = targetReadM2;
  /*
  Serial.print("curVelM1:");
  Serial.print(curVelM1);
  Serial.print(" ");
  Serial.print("curVelM2:");
  Serial.print(curVelM2);
  Serial.print(" ");
  Serial.print("targetVel:");
  Serial.print(targetVel);*/
  //Serial.print(" ");
  /*
  Serial.print("curReadM1:");
  Serial.print(curReadM1);
  Serial.print(" ");
  Serial.print("curReadM2:");
  Serial.print(curReadM2);
  Serial.print(" ");
  Serial.print("targetRead:");
  Serial.print(targetRead);
  */
  /*Serial.print(" ");
  Serial.print("errorM1:");
  Serial.print(errorM1);
  Serial.print(" ");
  Serial.print("errorM2:");
  Serial.print(errorM2);*/
  Serial.println();

  delay(10);
}

void pidM1(){
  
}

void pidM2(){
  
}
