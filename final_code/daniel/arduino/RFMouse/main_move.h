#include <Encoder.h>
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

Encoder enc1(M1_ENCA, M1_ENCB);
Encoder enc2(M2_ENCA, M2_ENCB);

int adc1_buf[8];
int adc2_buf[8];
bool arr[16];
int numLitRight = 0;
int numLitLeft = 0;

const unsigned int BUF_THRESHOLD = 710; //for G: 560, for C: 600, for D: 710
//float distTune = 135/145; //for G: , for C: 135/145, for D: 15/16
int command_int = 0; //for testing, REMOVE IN FINAL CODE

//PID vars
int M1_PWM = 0;
int M2_PWM = 0;
int prevTime = 0;
int prevReadM1 = 0;
int prevReadM2 = 0;
float targetDeltaRead = 0; //desired change in position in encoder counts, will be const and det. by target vel
float targetReadM1, targetReadM2;
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

void M1_forward(unsigned int PWM) {
  analogWrite(M1_IN1, 0);
  analogWrite(M1_IN2, PWM);
}

void M1_backward(unsigned int PWM) {
  analogWrite(M1_IN1, PWM);
  analogWrite(M1_IN2, 0);
}

void M1_stop() {
  analogWrite(M1_IN1, 0);
  analogWrite(M1_IN2, 0);
}

void M2_forward(unsigned int PWM) {
  analogWrite(M2_IN1, 0);
  analogWrite(M2_IN2, PWM);
}

void M2_backward(unsigned int PWM) {
  analogWrite(M2_IN1, PWM);
  analogWrite(M2_IN2, 0);
}

void M2_stop() {
  analogWrite(M2_IN1, 0);
  analogWrite(M2_IN2, 0);
}

void turn_left(unsigned int PWM) {
  M1_backward(PWM);
  M2_forward(PWM+2);
}

void turn_right(unsigned int PWM) {
  M1_forward(PWM);
  //M2_backward(PWM+3);
  M2_backward(PWM);
}

void stop_move() {
  M1_stop();
  M2_stop();
}

//count number of lit right sensors and lit left sensors
void countArr(){
  numLitRight = 0;
  numLitLeft = 0;
  for (int i = 0; i<=5; i++){
    if (arr[i] == true)
      numLitRight++;
  }
  for (int i = 7; i<=12; i++){
    if (arr[i] == true)
      numLitLeft++;
  }
}

void command_right_pid(){
  targetVel = 0.1;
  int passedIR8 = 0; //flag
  int completedTurnR = 0; //flag
  prevReadM1 = enc1.read();
  prevReadM2 = enc2.read();
  int initialReadM2 = prevReadM2; //M2 encoder(0)
  targetReadM1 = prevReadM1;
  targetReadM2 = prevReadM2;
  prevTime = micros();
  int ogComTime = prevTime;
  while (!completedTurnR){
    long curTime = micros(); //time since Arduino started in microseconds
    int curReadM1 = enc1.read();
    int curReadM2 = enc2.read();
    float deltaTime = ((float) (curTime - prevTime))/1.0e6; //delta T [s]
    targetDeltaRead = targetVel*deltaTime/(0.032*M_PI)*360; //target change in encoder position for desired velocity [counts]
    if (stopFlag == 0){  //only change target position if previous time doesn't have stopped motors
      targetReadM1 = targetReadM1 + targetDeltaRead; //target encoder position based on desired vel [counts]
      targetReadM2 = targetReadM2 + targetDeltaRead;
    } else { //if motors were stopped at previous time, 
      //don't change targetReadM1 or targetReadM2;
    }
    //if the stop flag is high, the targetRead won't change from the previous
    prevTime = curTime;

    float KpM1 = 0.2;
    float KiM1 = 0.05;
    float KdM1 = 0.1;
  
    float KpM2 = 0.2;
    float KiM2 = 0.05;
    float KdM2 = 0.1;

    errorM1 = targetReadM1 - curReadM1;
    if (errorM1 > errorLimit)
      errorM1 = errorLimit;
    integralM1 = integralM1 + errorM1*deltaTime;
    derivM1 = (errorM1 - prevErrorM1)/deltaTime;
  
    errorM2 = targetReadM2 - curReadM2; //negate for backwards
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
        //Serial.print("AH"); Serial.print("\t");
      } else {
        arr[count] = false;
        //Serial.print("--"); Serial.print("\t");
      }
      count = count + 1;
  
      if (adc2_buf[i] < BUF_THRESHOLD) {
        arr[count] = true;
        //Serial.print("AH"); Serial.print("\t");
      } else {
        arr[count] = false;
        //Serial.print("--"); Serial.print("\t");
      }
      count = count + 1;
    }
    //Serial.println();
    M1_forward(M1_PWM);
    M2_backward(M2_PWM);
    delay(10);
    
    long checkBarTime = micros(); //time at which IR sensors were checked
    if (arr[7] == true && passedIR8 == 0){
      passedIR8 = 1;
    } else if (arr[7] == true && (checkBarTime - ogComTime > 300000)){  //if turn has executed for >1s, check if centered on straight path to ensure it's past any forward paths
      completedTurnR = 1;
      //Serial.println("centered");
    }
  }
  stop_move();
}

void command_left_pid(){
  targetVel = 0.1;
  int passedIR5 = 0; //flag
  int completedTurnL = 0; //flag
  prevReadM1 = -1*enc1.read();
  prevReadM2 = -1*enc2.read();
  int initialReadM2 = prevReadM2; //M2 encoder(0)
  targetReadM1 = prevReadM1;
  targetReadM2 = prevReadM2;
  prevTime = micros();
  int ogComTime = prevTime;
  while (!completedTurnL){
    long curTime = micros(); //time since Arduino started in microseconds
    int curReadM1 = -1*enc1.read();
    int curReadM2 = -1*enc2.read();
    float deltaTime = ((float) (curTime - prevTime))/1.0e6; //delta T [s]
    targetDeltaRead = targetVel*deltaTime/(0.032*M_PI)*360; //target change in encoder position for desired velocity [counts]
    targetReadM1 = targetReadM1 + targetDeltaRead; //target encoder position based on desired vel [counts]
    targetReadM2 = targetReadM2 + targetDeltaRead;
    //if the stop flag is high, the targetRead won't change from the previous
    prevTime = curTime;

    float KpM1 = 0.2;
    float KiM1 = 0.05;
    float KdM1 = 0.1;
  
    float KpM2 = 0.2;
    float KiM2 = 0.05;
    float KdM2 = 0.1;

    errorM1 = targetReadM1 - curReadM1;
    if (errorM1 > errorLimit)
      errorM1 = errorLimit;
    integralM1 = integralM1 + errorM1*deltaTime;
    derivM1 = (errorM1 - prevErrorM1)/deltaTime;
  
    errorM2 = targetReadM2 - curReadM2; //negate for backwards
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
        //Serial.print("AH"); Serial.print("\t");
      } else {
        arr[count] = false;
        //Serial.print("--"); Serial.print("\t");
      }
      count = count + 1;
  
      if (adc2_buf[i] < BUF_THRESHOLD) {
        arr[count] = true;
        //Serial.print("AH"); Serial.print("\t");
      } else {
        arr[count] = false;
        //Serial.print("--"); Serial.print("\t");
      }
      count = count + 1;
    }
    //Serial.println();
    M1_backward(M1_PWM);
    M2_forward(M2_PWM);
    delay(10);
    
    long checkBarTime = micros(); //time at which IR sensors were checked
    if (arr[7] == true && passedIR5 == 0){
      passedIR5 = 1;
    } else if (arr[7] == true && (checkBarTime - ogComTime > 300000)){  //if turn has executed for >1s, check if centered on straight path to ensure it's past any forward paths
      completedTurnL = 1;
      //Serial.println("centered");
    }
  }
  stop_move();
}

void command_forward(double dist){ //move forward by specified distance (in m)
  //long commandStartTime = micros();
  //long commandCurTime = commandStartTime;
  //long commandDeltaTime = dist*1.0e6/targetVel*1.1; //idk why this needs the additional scaling factor but it works
  int completedForward = 0;
  prevReadM1 = enc1.read();
  prevReadM2 = -1*enc2.read();
  targetReadM1 = prevReadM1;
  targetReadM2 = prevReadM2;
  float targetFinalReadM1 = dist/(0.032*M_PI)*360*15/16+prevReadM1; //multiply by G: 30/33, C and D: 15/16 to adjust for miscalculation
  float targetFinalReadM2 = dist/(0.032*M_PI)*360*15/16+prevReadM2; //multiply by G: 30/33, C and D: 15/16 to adjust for miscalculation
  prevTime = micros();
  while (!completedForward){  //PID loop
    long curTime = micros(); //time since Arduino started in microseconds
    int curReadM1 = enc1.read();
    int curReadM2 = -1*enc2.read();
    float deltaTime = ((float) (curTime - prevTime))/1.0e6; //delta T [s]
    targetDeltaRead = targetVel*deltaTime/(0.032*M_PI)*360; //target change in encoder position for desired velocity [counts]
    targetReadM1 = targetReadM1 + targetDeltaRead; //target encoder position based on desired vel [counts]
    targetReadM2 = targetReadM2 + targetDeltaRead;
    //if the stop flag is high, the targetRead won't change from the previous
    prevTime = curTime;

    float KpM1 = 0.2;
    float KiM1 = 0.05;
    float KdM1 = 0.1;
  
    float KpM2 = 0.2;
    float KiM2 = 0.05;
    float KdM2 = 0.1;

    errorM1 = targetReadM1 - curReadM1;
    if (errorM1 > errorLimit)
      errorM1 = errorLimit;
    integralM1 = integralM1 + errorM1*deltaTime;
    derivM1 = (errorM1 - prevErrorM1)/deltaTime;
  
    errorM2 = targetReadM2 - curReadM2;
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
    Serial.println();
  
    //stopFlag = 0; //reset flag before checking light bar
    countArr();
    if ((arr[5] == true || arr[4] == true || arr[3] == true || arr[2] == true || arr[1] == true || arr[0] == true) ){ //too far to the right --> turn left (numLitRight<=2 for not a right corner) && numLitRight <= 2
      M1_PWM += 10;
      M2_PWM -= 10;
    } else if ((arr[7] == true || arr[8] == true || arr[9] == true || arr[10] == true || arr[11] == true || arr[12] == true)){ //too far to the left --> turn right (numLitLeft<=2 for not a left corner)  && numLitLeft <= 2
      M2_PWM += 10;
      M1_PWM -= 10;
    } /*else if (!(arr[0] || arr[1] || arr[2] || arr[3] || arr[4] || arr[5] || arr[6] || arr[7] || arr[8] || arr[9] || arr[10] || arr[11] || arr[12])){ //stop if can't see line
      M1_PWM = 0;
      M2_PWM = 0;
      stopFlag = 1;
    }*/
    
    M1_forward(M1_PWM);
    M2_forward(M2_PWM);

    delay(10);
    curReadM1 = enc1.read();
    curReadM2 = -1*enc2.read();
    if (curReadM1 >= targetFinalReadM1 || curReadM2 >= targetFinalReadM2)
      completedForward = 1;
    //commandCurTime = micros();
    //Serial.println(commandCurTime - commandStartTime);
    /*Serial.print(curReadM1);
    Serial.print("\t");
    Serial.print(targetFinalReadM1);
    Serial.print("\t\t");
    Serial.print(curReadM2);
    Serial.print("\t");
    Serial.print(targetFinalReadM2);
    Serial.println();*/
  }
  stop_move();
}
