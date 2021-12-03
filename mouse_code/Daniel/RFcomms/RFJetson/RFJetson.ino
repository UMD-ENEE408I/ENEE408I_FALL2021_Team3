
// This program receives packet from the mouse
// sends it via serial to the Jetson's python program
// waits for the Jetson's python program to send a response
// sends the response back to the mouse

#include <SPI.h>
#include "RF24.h"

RF24 radio(7, 8); // 7 = CE, 8 = CSN

uint8_t mouse_address[] = "mouseN";
uint8_t jetson_address[] = "jetNN";
uint8_t channel = 99; // (0-127) each team should use a different channel(s)

// Max possible size is 32 bytes (this packet is 32 bytes)
typedef struct packet {
  //float a_float;
  //int32_t a_signed_int;
  //uint8_t a_two_d_array[3][8];
  byte movementCommand; // 0 stop, 1 forward, 2 left, 3 right
  int distance;
  byte response;
} packet_t;

uint8_t magic_serial_header[4] = {0x8B, 0xEA, 0x27, 0x55};

packet_t send_packet = {0, 0, 0};
packet_t receive_packet = {0, 0, 0};

void setup() {
  Serial.begin(115200);
  while (!Serial); // Wait for serial over USB
  setup_radio();
}

void loop() {
// Make a packet and try to send it
// In the default configuration this could delay 33ms if it fails
// However when it works it takes 1-3ms
radio.stopListening();
send_packet.movementCommand = 0;
send_packet.distance = 20;
send_packet.response = 2;
unsigned long start = millis();
bool success = radio.write(&send_packet, sizeof(packet_t));
unsigned long end = millis();

if (success) {
  unsigned long end = millis();
  Serial.print("send succeeded took: ");
  Serial.print(end-start);
  Serial.println(" millis");
} else {
  unsigned long end = millis();
  Serial.print("send failed took: ");
  Serial.print(end-start);
  Serial.println(" millis");
}

// Try to receive a packet (the Jetson should send a response)
radio.startListening();
start = millis();
success = receivePacket(&receive_packet); // This will wait 10 milliseconds (can change)
end = millis();
if (success) {
  Serial.print("Received: ");
  Serial.print(receive_packet.movementCommand);
  Serial.print(" took ");
  Serial.print(end - start);
  Serial.println(" millis");

  if(receive_packet.response == 4){
    Serial.println("got ok response");
  } 
  
} else {
  Serial.print("Receive failed took ");
  Serial.print(end - start);
  Serial.println(" millis");
}

delay(10);

  
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
