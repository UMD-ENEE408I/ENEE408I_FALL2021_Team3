
// This program sends a packet to the Jetson
// and waits for a response from the Jetson

#include <SPI.h>
#include "RF24.h"

const unsigned int ADC_1_CS = A3;
const unsigned int ADC_2_CS = A2;

RF24 radio(0, A4, 1000000); // D0 = CE, A4 = CSN, spi_speed = 1MHz (default 10 Mhz is too fast)
// Use 1 Mhz, 10 MHz is too fast (based on oscilloscope)

uint8_t mouse_address[] = "mouseN";
uint8_t jetson_address[] = "jetNN";
uint8_t channel = 60; // (0-127) each team should use a different channel(s)

// Max possible size is 32 bytes (this packet is 32 bytes)
typedef struct packet {
//  float a_float;
//  int32_t a_signed_int;
//  uint8_t a_two_d_array[3][8];
  byte movementCommand; // 0 stop, 1 forward, 2 left, 3 right
  int distance;
  byte response;
} packet_t;

packet_t send_packet = {0, 0, 0};
packet_t receive_packet = {0, 0, 0};

void setup() {
  pinMode(ADC_1_CS, OUTPUT);
  pinMode(ADC_2_CS, OUTPUT);

  digitalWrite(ADC_1_CS, HIGH); // Without this the ADC's write
  digitalWrite(ADC_2_CS, HIGH); // to the SPI bus while the nRF24 is!!!!

  Serial.begin(115200);
  while (!Serial); // Wait for serial over USB
  
  setup_radio();

}

void loop() {
  // Try to receive a packet
  if (radio.available()) {
    radio.read(&receive_packet, sizeof(packet_t));
    
    if(receive_packet.movementCommand == 0){
      Serial.println("stop movement");
    } else if (receive_packet.movementCommand == 1){
      Serial.println("move forward");
    } else if (receive_packet.movementCommand == 2){
      Serial.println("move left");
      // save time for distance calc
    } else if (receive_packet.movementCommand == 3){
      Serial.println("move right");
      // save time for distance calc
    } else {
      // error
      Serial.println("error unknown movement command");
    }

    // Send received packet to python script
    // Serial.write(magic_serial_header, sizeof(magic_serial_header));
    // Serial.write((uint8_t*)&receive_packet, sizeof(packet_t));

    // // Python script is supposed to send a packet back immediately
    // Serial.readBytes((uint8_t*)&send_packet, sizeof(packet_t));

    send_packet.response = 4;
    
    radio.stopListening();
  
    // In the default configuration this could delay 33ms if it fails
    // However when it works it takes 1-3ms
    unsigned long start = millis();
    if (radio.write(&send_packet, sizeof(packet_t))) {
      unsigned long end = millis();
      Serial.print("reply succeeded took: ");
      Serial.print(end-start);
      Serial.println(" millis");
    } else {
      unsigned long end = millis();
      Serial.print("reply failed took: ");
      Serial.print(end-start);
      Serial.println(" millis");
    }

    // Switch back to RX before entering the main loop
    radio.startListening();
  }
}

#define MAX_PACKET_SIZE 32 // maximum packet size for radio
void setup_radio() {
  if (sizeof(packet_t) > MAX_PACKET_SIZE) {
    Serial.println("sizeof(packet_t) is too big for radio to send in one chunk");
    while(true); // halt forever
  }
  
  SPI.begin();

  while(!radio.isChipConnected()) {
    Serial.println("Can't talk to radio via SPI");
    delay(200);
  }

  while (!radio.begin(&SPI)) {
    Serial.println("Radio hardware did not initialize");
    while(1) {};
  }

  radio.setAutoAck(true);
  radio.setChannel(channel);                 // 2400 Mhz + channel number (0-125), default is 76
  radio.setPALevel(RF24_PA_MAX);             // Could set lower
  radio.setPayloadSize(sizeof(packet_t));
  radio.openWritingPipe(mouse_address);      // TX always uses pipe 0
  radio.openReadingPipe(1, jetson_address);  // set RX to use pipe 1
  radio.stopListening();                     // put radio in TX mode

  Serial.println("Radio hardware initialized");
}

bool receivePacket(packet_t* packet_p) {
  unsigned long start = micros();
  unsigned long timeout_micros = 10000;

  // Wait for packet until timeout
  while(!radio.available()) {
    if (micros() - start > timeout_micros) {
      return false;
    }
  }

  // Success, radio has data available
  radio.read(packet_p, sizeof(packet_t));

  return true;
}
