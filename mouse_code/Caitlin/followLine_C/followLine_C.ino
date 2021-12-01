/* Started by copying followLineG */

#include <Adafruit_MCP3008.h>

Adafruit_MCP3008 adc1;
Adafruit_MCP3008 adc2;

const unsigned int ADC_1_CS = A3;
const unsigned int ADC_2_CS = A2;
const unsigned int RF_CS = A4;

const unsigned int M1_IN_1 = 2;
const unsigned int M1_IN_2 = 3;
const unsigned int M2_IN_1 = 5;
const unsigned int M2_IN_2 = 4;

const unsigned int M1_I_SENSE = A1;
const unsigned int M2_I_SENSE = A0;

const float M_I_COUNTS_TO_A = (3.3 / 1024.0) / 0.120;

const unsigned int PWM_FWD = 25;  //forward
const unsigned int PWM_BWD = 30;  //backward
const unsigned int PWM_R = 30;    //right turn
const unsigned int PWM_L = 25;    //left turn
const unsigned int BUF_THRESHOLD = 600;

void M1_backward(unsigned int PWM) {
  analogWrite(M1_IN_1, PWM);
  analogWrite(M1_IN_2, 0);
}

void M1_forward(unsigned int PWM) {
  analogWrite(M1_IN_1, 0);
  analogWrite(M1_IN_2, PWM + 15);
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
  M1_forward(PWM-5);
  M2_forward(PWM+10);
}

void turn_left(unsigned int PWM) {
  M1_backward(PWM);
  M2_forward(PWM+10);
}

void turn_right(unsigned int PWM) {
  M1_forward(PWM+10);
  M2_backward(PWM);
}

void backward(unsigned int PWM) {
  M1_backward(PWM);
  M2_backward(PWM+10);
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

  pinMode(RF_CS, OUTPUT);
  digitalWrite(RF_CS, HIGH); // Without this the nRF24 will write to the SPI bus while the ADC's are also talking

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

  //Serial print AH if sees white line, else print --
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

  /*
  if (check_left(arr) > 3) {
      turn_right(40);
      delay(10);
    } else if (check_right(arr) > 3) {
      turn_left(40);
      delay(10);
    } else if (arr[6] == true) {
    forward(50);
    } else if (arr[5] == true || arr[4] == true || arr[3] == true || 
    arr[2] == true || arr[1] == true || arr[0] == true) {
      turn_right(30);
    } else if (arr[7] == true || arr[8] == true || arr[9] == true ||
    arr[10] == true || arr[11] == true || arr[12] == true) {
      turn_left(30);
    } else {
      backward(30);
    }
  */
  if (check_left(arr) > 3) {
      turn_right(PWM_R);
      delay(10);
  } else if (check_right(arr) > 3) {
      turn_left(PWM_L);
      delay(10);
  } else if (arr[6] == true) {
    forward(PWM_FWD);
  } else if (arr[5] == true || arr[4] == true || arr[3] == true || arr[2] == true || arr[1] == true || arr[0] == true){
    turn_right(PWM_R);
  } else if (arr[7] == true || arr[8] == true || arr[9] == true || arr[10] == true || arr[11] == true || arr[12] == true){
    turn_left(PWM_L);
  } else
    backward(PWM_BWD);

  delay(10);


  Serial.print(t_end - t_start);
  Serial.println();

}


/* C's original code
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

const unsigned int PWM_FWD = 20;  //forward
const unsigned int PWM_BWD = 30;  //backward
const unsigned int PWM_R = 25;    //right turn
const unsigned int PWM_L = 35;    //left turn

void M1_backward(unsigned int PWM) {
  analogWrite(M1_IN_1, PWM);
  analogWrite(M1_IN_2, 0);
  /*
  Serial.print("M1_backward\tM1_IN_1: ");
  Serial.print(M1_IN_1);
  Serial.print("\t");
  Serial.print("M1_IN_2: ");
  Serial.print(M1_IN_2);
  Serial.println();

}

void M1_forward(unsigned int PWM) {
  analogWrite(M1_IN_1, 0);
  analogWrite(M1_IN_2, PWM + 10);
  /*
  Serial.print("M1_forward\tM1_IN_1: ");
  Serial.print(M1_IN_1);
  Serial.print("\t");
  Serial.print("M1_IN_2: ");
  Serial.print(M1_IN_2);
  Serial.println();
  
}

void M1_stop() {
  analogWrite(M1_IN_1, 0);
  analogWrite(M1_IN_2, 0);
  /*
  Serial.print("M1_stop\tM1_IN_1: ");
  Serial.print(M1_IN_1);
  Serial.print("\t");
  Serial.print("M1_IN_2: ");
  Serial.print(M1_IN_2);
  Serial.println();
  
}

void M2_backward(unsigned int PWM) {
  analogWrite(M2_IN_1, PWM);
  analogWrite(M2_IN_2, 0);
  /*
  Serial.print("M2_backward\tM2_IN_1: ");
  Serial.print(M2_IN_1);
  Serial.print("\t");
  Serial.print("M2_IN_2: ");
  Serial.print(M2_IN_2);
  Serial.println();
  
}

void M2_forward(unsigned int PWM) {
  analogWrite(M2_IN_1, 0);
  analogWrite(M2_IN_2, PWM);
  /*
  Serial.print("M2_forward\tM2_IN_1: ");
  Serial.print(M2_IN_1);
  Serial.print("\t");
  Serial.print("M2_IN_2: ");
  Serial.print(M2_IN_2);
  Serial.println();
  
}

void M2_stop() {
  analogWrite(M2_IN_1, 0);
  analogWrite(M2_IN_2, 0);
  /*
  Serial.print("M2_stop\tM2_IN_1: ");
  Serial.print(M2_IN_1);
  Serial.print("\t");
  Serial.print("M2_IN_2: ");
  Serial.print(M2_IN_2);
  Serial.println();
  
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
  M2_backward(PWM+10);
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
      turn_right(PWM_R);
      delay(7);
    } else if (check_right(arr) > 3) {
      turn_left(PWM_L);
      delay(7);
    } else if (arr[6] == true) {
      forward(PWM_FWD);               //20 too low
    } else if (arr[5] == true || arr[4] == true || arr[3] == true || 
    arr[2] == true || arr[1] == true || arr[0] == true) {
      turn_right(PWM_R);
    } else if (arr[7] == true || arr[8] == true || arr[9] == true ||
    arr[10] == true || arr[11] == true || arr[12] == true) {
      turn_left(PWM_L);
    } else {
      backward(PWM_BWD);
      //stop_move();
    }


  delay(7);


  Serial.print(t_end - t_start);
  Serial.println();


}
*/
