#include <ArduinoBLE.h>
#include <Arduino_LSM9DS1.h>

float gx, gy, gz;

BLEService motorService("0fe79935-cd39-480a-8a44-06b70f36f248");
BLEService sendIMUService("1eb0db8f-1c34-4168-8daf-0cd5d8d07fe6");  //send IMU data to serial

// create switch characteristic and allow remote device to read and write
BLEUnsignedIntCharacteristic motorCharacteristic("0fe79935-cd39-480a-8a44-06b70f36f249", BLERead | BLEWrite);
BLEUnsignedIntCharacteristic IMUCharacteristic("1eb0db8f-1c34-4168-8daf-0cd5d8d07fe6", BLERead);

void setup() {
  Serial.begin(115200);


  if (!BLE.begin()) {
    Serial.println("starting BLE failed!");
    while (1);
  }

  // Set the connection interval to be as fast as possible (about 40 Hz)
  BLE.setConnectionInterval(0x0006, 0x0006);

  BLE.setLocalName("dingus");
  BLE.setAdvertisedService(motorService);
  motorService.addCharacteristic(motorCharacteristic);
  BLE.addService(motorService);

  BLE.setAdvertisedService(sendIMUService);
  sendIMUService.addCharacteristic(IMUCharacteristic);
  BLE.addService(sendIMUService);

  BLE.setEventHandler(BLEConnected, blePeripheralConnectHandler);
  BLE.setEventHandler(BLEDisconnected, blePeripheralDisconnectHandler);

  // assign event handlers for characteristic
  //motorCharacteristic.setEventHandler(BLEWritten, motorCharacteristicWritten);
  //motorCharacteristic.setValue(1);
  
  IMUCharacteristic.setEventHandler(BLEWritten, IMUCharacteristicWritten);
  IMUCharacteristic.setValue(0);

  BLE.advertise();
  Serial.println("Waiting for connection");

  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (1);
  }
}

void loop() {
  BLE.poll();
  getIMUGyro();
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

//write gyroscope values
void IMUCharacteristicWritten(BLEDevice central, BLECharacteristic characteristic){
  Serial.print("IMUCharacteristicWritten: ");
  unsigned int v = IMUCharacteristic.value();
  
}

//get gyroscope values
void getIMUGyro(){
  
}
