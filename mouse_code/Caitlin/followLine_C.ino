#include <Adafruit_MCP3008.h>

Adafruit_MCP3008 adc1;
Adafruit_MCP3008 adc2;

const unsigned int ADC_1_CS = A3;
const unsigned int ADC_2_CS = A2;

const unsigned int M1_IN_1 = 2;   // M1 = left
const unsigned int M1_IN_2 = 3;
const unsigned int M2_IN_1 = 5;   // M2 = right
const unsigned int M2_IN_2 = 4;

const unsigned int M1_I_SENSE = A1;
const unsigned int M2_I_SENSE = A0;

const float M_I_COUNTS_TO_A = (3.3 / 1024.0) / 0.120;

const unsigned int PWM_VALUE = 50;

void M1_backward(unsigned int PWM) {
  analogWrite(M1_IN_1, PWM);
  analogWrite(M1_IN_2, 0);
}

void M1_forward(unsigned int PWM) {
  analogWrite(M1_IN_1, 0);
  analogWrite(M1_IN_2, PWM + 20);
}

void M1_stop() {
  analogWrite(M1_IN_1, 0);
  analogWrite(M1_IN_2, 0);
}

void M2_backward(unsigned int PWM) {
  analogWrite(M2_IN_1, PWM);
  analogWrite(M2_IN_2, 0);
}

void M2_forward(unsigned int PWM) {
  analogWrite(M2_IN_1, 0);
  analogWrite(M2_IN_2, PWM);
}

void M2_stop() {
  analogWrite(M2_IN_1, 0);
  analogWrite(M2_IN_2, 0);
}
void stop_move() {
  M1_stop();
  M2_stop();
}

void forward(unsigned int PWM) {
  M1_forward(PWM+10);
  M2_forward(PWM);
}

void turn_left(unsigned int PWM) {
  M1_forward(PWM);
  M2_forward(PWM+35);
}

void turn_right(unsigned int PWM) {
  M1_forward(PWM);
  M2_forward(PWM);
}

void backward(unsigned int PWM) {
  M1_backward(PWM);
  M2_backward(PWM+20);
}

int check_left(bool arr[]) {
  int count = 0;
  for(int i = 0; i < 6; i++) {
    if (arr[i] == true) {
      count = count + 1;
    }
  }

  return count;
}

int check_right(bool arr[]) {
  int count = 0;
  for(int i = 7; i < 13; i++) {
    if (arr[i] == true) {
      count = count + 1;
    }
  }

  return count;
}
void setup() {
  Serial.begin(115200);

  adc1.begin(ADC_1_CS);  
  adc2.begin(ADC_2_CS);  

  pinMode(M1_IN_1, OUTPUT);
  pinMode(M1_IN_2, OUTPUT);
  pinMode(M2_IN_1, OUTPUT);
  pinMode(M2_IN_2, OUTPUT);
}

void loop() {
  
  stop_move();
  
  int adc1_buf[8];
  int adc2_buf[8];

  bool arr[16];

  int t_start = micros();
  for (int i = 0; i < 8; i++) {
    adc1_buf[i] = adc1.readADC(i);
    adc2_buf[i] = adc2.readADC(i);
  }
  int t_end = micros();

//  for (int i = 0; i < 8; i++) {
//    Serial.print(adc1_buf[i]); Serial.print("\t");
//    Serial.print(adc2_buf[i]); Serial.print("\t");
//  }

  int count = 0;
  
  for (int i = 0; i < 8; i++) {
    if (adc1_buf[i] < 600) {
      arr[count] = true;
      Serial.print("AH"); Serial.print("\t");
    } else {
      arr[count] = false;
      Serial.print("--"); Serial.print("\t");
    }

    count = count + 1;

    if (adc2_buf[i] < 600) {
      arr[count] = true;
      Serial.print("AH"); Serial.print("\t");
    } else {
      arr[count] = false;
      Serial.print("--"); Serial.print("\t");
    }

    count = count + 1;
  }

  if (check_left(arr) > 3) {
      turn_right(35);
      delay(10);
    } else if (check_right(arr) > 3) {
      turn_left(35);
      delay(10);
    } else if (arr[6] == true) {
    forward(20);                    //20 too low
    } else if (arr[5] == true || arr[4] == true || arr[3] == true || 
    arr[2] == true || arr[1] == true || arr[0] == true) {
      turn_right(30);
    } else if (arr[7] == true || arr[8] == true || arr[9] == true ||
    arr[10] == true || arr[11] == true || arr[12] == true) {
      turn_left(25);
    } else {
      //backward(30);
      stop_move();
    }


  delay(10);


  Serial.print(t_end - t_start);
  Serial.println();


}
