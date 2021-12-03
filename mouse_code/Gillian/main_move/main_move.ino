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

const unsigned int BUF_THRESHOLD = 600; //for G: 560, for C: 600, for D: 710
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

void readBar(){
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
}

//make a left turn on command
void command_left() {
  int PWM_L = 35; //ADJUST THIS
  int PWM_R = 35; //ADJUST THIS
  //turn_left(leftPWM);
  //delay(10000);
  //turn left code
  long ogComTime = micros(); //time at which original turn command was given
  int completedTurnL = 0; //flag
  int completedTurnR = 0; //flag
  while (!completedTurnL){
    //Serial.println("turning left");
    turn_left(PWM_L);
    completedTurnR = 0; //reset flag
    delay(10);
    //Serial.println("stop move");
    stop_move();
    //Serial.println("reading bar");
    readBar();
    long checkBarTime = micros(); //time at which IR sensors were checked
    if (arr[5] == true && (checkBarTime - ogComTime > 500000)){  //if turn has executed for >0.7s, check if centered on straight path to ensure it's past any forward paths
      completedTurnL = 1;
      //Serial.println("centered");
    }/*else if (arr[5] == true || arr[4] == true || arr[3] == true || arr[2] == true || arr[1] == true || arr[0] == true){ //turned too far to the left, need to turn right
      while (!completedTurnR){
        Serial.println("turning right");
        turn_right(rightPWM);
        delay(10);
        Serial.println("stop move (right)");
        stop_move();
        Serial.println("reading bar (right)");
        readBar();
        if (arr[6] == true){  //centered on straight path
          Serial.println("centered (right)");
          completedTurnR = 1; //raise flag
          completedTurnL = 1; //raise flag
        } else if (arr[7] == true || arr[8] == true || arr[9] == true || arr[10] == true || arr[11] == true || arr[12] == true){ //turned far to the right, need to let left
          Serial.println("too far right");
          completedTurnR = 1; //raise flag
        } 
      }
    }*/
  }
  //Serial.println("done turning left");
  stop_move();
  //delay(1000);
}

void command_right(){
  targetVel = 0.1;
  int PWM_R = 38; //ADJUST THIS
  //int PWM_L = 35; //ADJUST THIS
  //turn_right(PWM_R);
  
  //right turn code
  long ogComTime = micros(); //time at which original turn command was given
  int passedIR8 = 0; //flag
  int completedTurnR = 0; //flag
  while (!completedTurnR){
    //Serial.println("turning right");
    turn_right(PWM_R);
    delay(10);
    //Serial.println("stop move");
    stop_move();
    //Serial.println("reading bar");
    readBar();
    long checkBarTime = micros(); //time at which IR sensors were checked
    if (arr[7] == true && passedIR8 == 0){
      passedIR8 = 1;
    } else if (arr[7] == true && (checkBarTime - ogComTime > 200000)){  //if turn has executed for >0.5s, check if centered on straight path to ensure it's past any forward paths
      completedTurnR = 1;
      //Serial.println("centered");
    }
  }
  //Serial.println("done turning right");
  stop_move();
  //delay(1000);
}

void command_right_pwm(){
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

void command_left_pwm(){
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
  long commandStartTime = micros();
  long commandCurTime = commandStartTime;
  long commandDeltaTime = dist*1.0e6/targetVel*1.1; //idk why this needs the additional scaling factor but it works
  prevReadM1 = enc1.read();
  prevReadM2 = -1*enc2.read();
  targetReadM1 = prevReadM1;
  targetReadM2 = prevReadM2;
  prevTime = micros();
  while (commandCurTime - commandStartTime < commandDeltaTime){  //PID loop
    long curTime = micros(); //time since Arduino started in microseconds
    int curReadM1 = enc1.read();
    int curReadM2 = -1*enc2.read();
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
  
    stopFlag = 0; //reset flag before checking light bar
    if (arr[5] == true || arr[4] == true || arr[3] == true || arr[2] == true || arr[1] == true || arr[0] == true){ //too far to the right --> turn left
      M1_PWM += 10;
      M2_PWM -= 10;
    } else if (arr[7] == true || arr[8] == true || arr[9] == true || arr[10] == true || arr[11] == true || arr[12] == true){ //too far to the left --> turn right
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
    commandCurTime = micros();
    //Serial.println(commandCurTime - commandStartTime);
  }

  stop_move();
}

void setup() {
  Serial.begin(115200);
  adc1.begin(ADC_1_CS);  
  adc2.begin(ADC_2_CS);  

  pinMode(RF_CS, OUTPUT);
  digitalWrite(RF_CS, HIGH); // Without this the nRF24 will write to the SPI bus while the ADCs are also talking

  pinMode(M1_IN1, OUTPUT);
  pinMode(M1_IN2, OUTPUT);
  pinMode(M2_IN1, OUTPUT);
  pinMode(M2_IN2, OUTPUT);
}

void loop() {
  //forward code -- PID controller
  /*delay(6000);
  command_forward(0.15);
  delay(5000);
  command_forward(0.15);
  delay(5000);
  command_forward(0.15);
  delay(5000);
  command_right();
  delay(5000);
  command_forward(0.15);
  delay(8000);*/
  /*if (command_int == 0){
    delay(6000);
    command_forward(0.15);
    delay(5000);
  } else if (command_int == 1){
    
  } else if (command_int == 2){
    
  }*/
  //readBar();
  /*
  for (int i = 0; i < 8; i++) {
    if (adc1_buf[i] < BUF_THRESHOLD) {
      Serial.print("AH"); Serial.print("\t");
    } else {
      Serial.print("--"); Serial.print("\t");
    }

    if (adc2_buf[i] < BUF_THRESHOLD) {
      Serial.print("AH"); Serial.print("\t");
    } else {
      Serial.print("--"); Serial.print("\t");
    }
  }
  Serial.println();
  delay(10);
  */
  //command_left();
  delay(6000);
  command_left_pwm();
}
