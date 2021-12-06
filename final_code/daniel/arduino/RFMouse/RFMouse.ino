//GILLIAN'S MOUSE

// This program receives packet from the mouse
// sends it via serial to the Jetson's python program
// waits for the Jetson's python program to send a response
// sends the response back to the mouse

#include <SPI.h>
#include "RF24.h"
#include "main_move.h"

//const unsigned int ADC_1_CS = A3;
//const unsigned int ADC_2_CS = A2;

RF24 radio(0, A4, 1000000); // D0 = CE, A4 = CSN, spi_speed = 1MHz (default 10 Mhz is too fast)
// Use 1 Mhz, 10 MHz is too fast (based on oscilloscope)


uint8_t mouse_address[] = "mouseN";
uint8_t jetson_address[] = "jetNN";
uint8_t channel = 42; // (0-127) each team should use a different channel(s)

// Max possible size is 32 bytes (this packet is 32 bytes)
typedef struct packet {
  int32_t command;
  int32_t distance;
} packet_t;

uint8_t magic_serial_header[3] = {0x8B, 0xEA, 0x27};

packet_t send_packet = {0, 0};
packet_t receive_packet;

void setup() {
  pinMode(ADC_1_CS, OUTPUT);
  pinMode(ADC_2_CS, OUTPUT);

  digitalWrite(ADC_1_CS, HIGH); // Without this the ADC's write
  digitalWrite(ADC_2_CS, HIGH); // to the SPI bus while the nRF24 is!!!!

  Serial.begin(115200);
  while (!Serial); // Wait for serial over USB
  setup_radio();

  Serial.begin(115200);
  adc1.begin(ADC_1_CS);  
  adc2.begin(ADC_2_CS);  

  pinMode(M1_IN1, OUTPUT);
  pinMode(M1_IN2, OUTPUT);
  pinMode(M2_IN1, OUTPUT);
  pinMode(M2_IN2, OUTPUT);

  Serial.println("HIII");
}

void loop() {
  // Try to receive a packet
  if (radio.available()) {
    radio.read(&receive_packet, sizeof(packet_t));

    Serial.print("Command: ");
    Serial.print(receive_packet.command);
    Serial.print(" ");
    Serial.println(receive_packet.distance);
    Serial.println(receive_packet.command == 1);

    if (receive_packet.command == 0){
      stop_move();
    }else if (receive_packet.command == 1){
      command_forward((double) ((double) receive_packet.distance)/100);
    }else if (receive_packet.command == 2){
      command_left_pid();
    }else if (receive_packet.command == 3){
      command_right_pid();
    }
    
    send_packet.command = 200;
    send_packet.distance = 200;
    
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
  radio.startListening();                     // put radio in TX mode

  Serial.println("Radio hardware initialized");
}
