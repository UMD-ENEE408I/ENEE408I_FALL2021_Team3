#include <ArduinoBLE.h>
#include <Arduino_LSM9DS1.h>

float gx, gy, gz;  //global vars for gyroscope values

BLEService motorService("0fe79935-cd39-480a-8a44-06b70f36f248");
BLEService IMUGyroService("1eb0db8f-1c34-4168-8daf-0cd5d8d07fe6");  //send IMU data to serial

// create switch characteristic and allow remote device to read and write
BLEUnsignedIntCharacteristic motorCharacteristic("0fe79935-cd39-480a-8a44-06b70f36f249", BLERead | BLEWrite);
BLEFloatCharacteristic IMUGyroXCharacteristic("1eb0db8f-1c34-4168-8daf-0cd5d8d07fe7", BLERead);
BLEFloatCharacteristic IMUGyroYCharacteristic("985beab5-3fd8-4019-a2a1-a1d5c9ca2159", BLERead);
//BLEFloatCharacteristic IMUGyroZCharacteristic();

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

  BLE.setAdvertisedService(IMUGyroService);
  IMUGyroService.addCharacteristic(IMUGyroXCharacteristic);
  IMUGyroService.addCharacteristic(IMUGyroYCharacteristic);
  BLE.addService(IMUGyroService);

  BLE.setEventHandler(BLEConnected, blePeripheralConnectHandler);
  BLE.setEventHandler(BLEDisconnected, blePeripheralDisconnectHandler);

  // assign event handlers for characteristic
  //motorCharacteristic.setEventHandler(BLEWritten, motorCharacteristicWritten);
  //motorCharacteristic.setValue(1);

  //event handler for IMU Gyro x characteristic
  IMUGyroXCharacteristic.setEventHandler(BLEWritten, IMUCharacteristicWritten);
  //set initial value
  IMUGyroXCharacteristic.setValue(0);
  //event handler for IMU Gyro y characteristic
  IMUGyroYCharacteristic.setEventHandler(BLEWritten, IMUCharacteristicWritten);
  //set initial value
  IMUGyroYCharacteristic.setValue(0);

  //start advertising
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
  Serial.print("Gyr: ");
  Serial.print(gx);
  Serial.print('\t');
  Serial.print(gy);
  Serial.print('\t');
  Serial.print(gz);
  Serial.print('\t');
  Serial.println();
  IMUGyroXCharacteristic.writeValue(gx);
  IMUGyroYCharacteristic.writeValue(gy);
  delay(100);
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

//print values written from server
void IMUCharacteristicWritten(BLEDevice central, BLECharacteristic characteristic){
  Serial.print("IMUCharacteristicWritten: ");
  unsigned int v = IMUGyroXCharacteristic.value();
  Serial.print("value: ");
  Serial.println(v);
}

//get gyroscope values
void getIMUGyro(){
  if(IMU.gyroscopeAvailable()){
    IMU.readGyroscope(gx, gy, gz);
  }
}
