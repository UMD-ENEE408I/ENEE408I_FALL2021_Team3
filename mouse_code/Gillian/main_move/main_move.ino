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

const unsigned int BUF_THRESHOLD = 550; //for G: 550, for C: 600, for D: 710

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

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  adc1.begin(ADC_1_CS);  
  adc2.begin(ADC_2_CS);  

  pinMode(M1_IN1, OUTPUT);
  pinMode(M1_IN2, OUTPUT);
  pinMode(M2_IN1, OUTPUT);
  pinMode(M2_IN2, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  //forward code -- PID controller

  readBar();
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
  delay(10);
  
  //turn left code
  /*
  int completedTurnL = 0; //flag
  int completedTurnR = 0; //flag
  int leftPWM;
  while (!completedTurnL){
    turn_left(leftPWM);
    completedTurnR = 0; //reset flag
    delay(10);
    stop_move();
    readBar();
    if (arr[6] == true)  //centered on straight path
      completedTurnL = 1;
    else if (arr[5] == true || arr[4] == true || arr[3] == true || arr[2] == true || arr[1] == true || arr[0] == true){ //turned too far to the left, need to turn right
      while (!completedTurnR){
        turn_right(rightPWM);
        delay(10);
        stop_move();
        readBar();
        if (arr[6] == true){  //centered on straight path
          completedTurnR = 1; //raise flag
          completedTurnL = 1; //raise flag
        } else if (arr[7] == true || arr[8] == true || arr[9] == true || arr[10] == true || arr[11] == true || arr[12] == true){ //turned far to the right, need to let left
          completedTurnR = 1; //raise flag
        } 
      }
    }
  }
  */
}
