// This program receives packet from the mouse
// sends it via serial to the Jetson's python program
// waits for the Jetson's python program to send a response
// sends the response back to the mouse

#include <SPI.h>
#include "RF24.h"

RF24 radio(7, 8); // 7 = CE, 8 = CSN

uint8_t mouse_address[] = "mouseN";
uint8_t jetson_address[] = "jetNN";
uint8_t channel = 44; // (0-127) each team should use a different channel(s)

// Max possible size is 32 bytes (this packet is 32 bytes)
typedef struct packet {
  float a_float;
  int32_t a_signed_int;
  uint8_t a_two_d_array[3][8];
} packet_t;

uint8_t magic_serial_header[4] = {0x8B, 0xEA, 0x27, 0x55};

packet_t send_packet = {0.0, 0, 0};
packet_t receive_packet;

void setup() {
  Serial.begin(115200);
  while (!Serial); // Wait for serial over USB
  setup_radio();
}

void loop() {
  // Try to receive a packet
  if (radio.available()) {
    radio.read(&receive_packet, sizeof(packet_t));
    
    //Serial.print(receive_packet.a_float);
    //Serial.print(" ");
    //Serial.println(receive_packet.a_signed_int);

    // Send received packet to python script
    Serial.write(magic_serial_header, sizeof(magic_serial_header));
    Serial.write((uint8_t*)&receive_packet, sizeof(packet_t));

    // Python script is supposed to send a packet back immediately
    Serial.readBytes((uint8_t*)&send_packet, sizeof(packet_t));
    
    radio.stopListening();
  
    // In the default configuration this could delay 33ms if it fails
    // However when it works it takes 1-3ms
    unsigned long start = millis();
    if (radio.write(&send_packet, sizeof(packet_t))) {
      unsigned long end = millis();
      //Serial.print("reply succeeded took: ");
      //Serial.print(end-start);
      //Serial.println(" millis");
    } else {
      unsigned long end = millis();
      //Serial.print("reply failed took: ");
      //Serial.print(end-start);
      //Serial.println(" millis");
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

  while (!radio.begin()) {
    Serial.println("Radio hardware did not initialize");
    delay(200);
  }

  radio.setAutoAck(true);
  radio.setChannel(channel);                      // 2400 Mhz + channel number (0-125), default is 76
  radio.setPALevel(RF24_PA_MAX);             // Could set lower
  radio.setPayloadSize(sizeof(packet_t));
  radio.openWritingPipe(jetson_address);     // TX always uses pipe 0
  radio.openReadingPipe(1, mouse_address);   // set RX to use pipe 1
  radio.startListening();                    // put radio in RX mode

  Serial.println("Radio hardware initialized");
}
