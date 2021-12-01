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

int adc1_buf[8];
int adc2_buf[8];
bool arr[16];

const unsigned int BUF_THRESHOLD = 560; //for G: 550, for C: 600, for D: 710

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
  M2_backward(PWM+3);
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

//make a full left turn on command
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
    Serial.print("turning left");
    Serial.println();
    turn_left(PWM_L);
    completedTurnR = 0; //reset flag
    delay(10);
    Serial.println("stop move");
    stop_move();
    Serial.println("reading bar");
    readBar();
    long checkBarTime = micros(); //time at which IR sensors were checked
    if (arr[5] == true && (checkBarTime - ogComTime > 500000)){  //if turn has executed for >0.7s, check if centered on straight path to ensure it's past any forward paths
      completedTurnL = 1;
      Serial.println("centered");
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
  
  Serial.println("done turning left");
  stop_move();
  //delay(1000);
}

void command_right(){
  int PWM_R = 36; //ADJUST THIS
  int PWM_L = 35; //ADJUST THIS
  //turn_right(PWM_R);
  
  //right turn code
  long ogComTime = micros(); //time at which original turn command was given
  int passedIR8 = 0; //flag
  int completedTurnR = 0; //flag
  while (!completedTurnR){
    Serial.println("turning right");
    turn_right(PWM_R);
    delay(10);
    Serial.println("stop move");
    stop_move();
    Serial.println("reading bar");
    readBar();
    long checkBarTime = micros(); //time at which IR sensors were checked
    if (arr[7] == true && passedIR8 == 0){
      passedIR8 = 1;
    } else if (arr[7] == true && (checkBarTime - ogComTime > 800000)){  //if turn has executed for >1s, check if centered on straight path to ensure it's past any forward paths
      completedTurnR = 1;
      Serial.println("centered");
    }
  }
  
  Serial.println("done turning right");
  stop_move();
  //delay(1000);
}

void setup() {
  Serial.begin(115200);
  adc1.begin(ADC_1_CS);  
  adc2.begin(ADC_2_CS);  

  pinMode(M1_IN1, OUTPUT);
  pinMode(M1_IN2, OUTPUT);
  pinMode(M2_IN1, OUTPUT);
  pinMode(M2_IN2, OUTPUT);
}

void loop() {
  //forward code -- PID controller

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
  //command_right();
  
}
