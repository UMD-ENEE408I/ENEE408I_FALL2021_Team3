const unsigned int M1_IN_1 = 2;
const unsigned int M1_IN_2 = 3;
const unsigned int M2_IN_1 = 5;
const unsigned int M2_IN_2 = 4;

const unsigned int M1_I_SENSE = A1;
const unsigned int M2_I_SENSE = A0;

const float M_I_COUNTS_TO_A = (3.3 / 1024.0) / 0.120;

const unsigned int PWM_VALUE = 20;

void M1_backward() {
  analogWrite(M1_IN_1, PWM_VALUE);
  analogWrite(M1_IN_2, 0);
}

void M1_forward() {
  analogWrite(M1_IN_1, 0);
  analogWrite(M1_IN_2, PWM_VALUE);
}

void M1_stop() {
  analogWrite(M1_IN_1, 0);
  analogWrite(M1_IN_2, 0);
}

void M2_backward() {
  analogWrite(M2_IN_1, PWM_VALUE);
  analogWrite(M2_IN_2, 0);
}

void M2_forward() {
  analogWrite(M2_IN_1, 0);
  analogWrite(M2_IN_2, PWM_VALUE);
}

void M2_stop() {
  analogWrite(M2_IN_1, 0);
  analogWrite(M2_IN_2, 0);
}

void setup() {
  pinMode(M1_IN_1, OUTPUT);
  pinMode(M1_IN_2, OUTPUT);
  pinMode(M2_IN_1, OUTPUT);
  pinMode(M2_IN_2, OUTPUT);
}

void loop() {
  M1_stop();
  M2_stop();

  delay(5000);
  
  M1_forward();
  M2_forward();

  for(int i = 0; i < 500; i++) { 
    int M1_I_counts = analogRead(M1_I_SENSE);
    int M2_I_counts = analogRead(M2_I_SENSE);

    Serial.print(M1_I_counts);
    Serial.print("\t");
    Serial.print(M1_I_counts * M_I_COUNTS_TO_A);
    Serial.print("\t");
    Serial.print(M2_I_counts);
    Serial.print("\t");
    Serial.print(M2_I_counts * M_I_COUNTS_TO_A);
    Serial.println();
    delay(1);
  }


  M2_backward();
  delay(500);
}
