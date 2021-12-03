#include <ArduinoBLE.h>

BLEService motorService("0fe79935-cd39-480a-8a44-06b70f36f248");

// create switch characteristic and allow remote device to read and write
BLEUnsignedIntCharacteristic motorCharacteristic("0fe79935-cd39-480a-8a44-06b70f36f249", BLERead | BLEWrite);

void setup() {
  Serial.begin(115200);


  if (!BLE.begin()) {
    Serial.println("starting BLE failed!");
    while (1);
  }

  // Set the connection interval to be as fast as possible (about 40 Hz)
  BLE.setConnectionInterval(0x0006, 0x0006);

  BLE.setLocalName("Mouse 1");
  BLE.setAdvertisedService(motorService);
  motorService.addCharacteristic(motorCharacteristic);
  BLE.addService(motorService);

  BLE.setEventHandler(BLEConnected, blePeripheralConnectHandler);
  BLE.setEventHandler(BLEDisconnected, blePeripheralDisconnectHandler);

  // assign event handlers for characteristic
  motorCharacteristic.setEventHandler(BLEWritten, motorCharacteristicWritten);
  motorCharacteristic.setValue(0);

  BLE.advertise();
  Serial.println("Waiting for connection");
}

void loop() {
  BLE.poll();
}

void blePeripheralConnectHandler(BLEDevice central) {
  Serial.print("Connected event, central: ");
  Serial.println(central.address());
}

void blePeripheralDisconnectHandler(BLEDevice central) {
  Serial.print("Disconnected event, central: ");
  Serial.println(central.address());
}

void motorCharacteristicWritten(BLEDevice central, BLECharacteristic characteristic) {
  Serial.print("motorCharacteristicWritten: ");
  unsigned int v = motorCharacteristic.value();
  short left = (short)((v>>0) & 0x0000FFFF); // Unpack 16 bit signed value (assume short is 16 bit)
  short right = (short)((v>>16) & 0x0000FFFF); // Unpack 16 bit signed value
  Serial.print(left);
  Serial.print(" ");
  Serial.println(right);
}
