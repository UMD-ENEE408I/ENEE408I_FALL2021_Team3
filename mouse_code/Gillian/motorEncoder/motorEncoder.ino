//EncoderTest from Mouse Examples
#include <Encoder.h>

const unsigned int M1_ENC_A = 6;
const unsigned int M1_ENC_B = 7;
const unsigned int M2_ENC_A = 8;
const unsigned int M2_ENC_B = 9;

Encoder enc1(M1_ENC_A, M1_ENC_B);
Encoder enc2(M2_ENC_A, M2_ENC_B);

void setup() {
  Serial.begin(115200);

  //analogWrite(2, 255);
  //analogWrite(3, 0);
  //analogWrite(4, 255);
  //analogWrite(5, 0);
}

void loop() {
  Serial.print(enc1.read());
  Serial.print("\t");
  Serial.print(enc2.read());
  Serial.println();
  delay(10);

}
