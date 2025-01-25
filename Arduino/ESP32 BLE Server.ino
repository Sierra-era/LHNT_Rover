#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
// UUIDs
#define SERVICE_UUID           "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define CHARACTERISTIC_UUID    "beb5483e-36e1-4688-b7f5-ea07361b26a8"
// Forward declarations
void function1();
void function2();
void function3();
void function4();
void function5();
class MyCharacteristicCallbacks : public BLECharacteristicCallbacks {
  void onWrite(BLECharacteristic *pCharacteristic) {
    // Convert std::string to Arduino String
    String rxValue = String(pCharacteristic->getValue().c_str());
    if (rxValue.length() > 0) {
      Serial.print("Received Value: ");
      Serial.println(rxValue);
      // Compare against "1", "2", ..., "5"
      if (rxValue == "1") {
        function1();
      } else if (rxValue == "2") {
        function2();
      } else if (rxValue == "3") {
        function3();
      } else if (rxValue == "4") {
        function4();
      } else if (rxValue == "5") {
        function5();
      }
    }
  }
};
void setup() {
  Serial.begin(115200);
  Serial.println("Starting BLE work!");
  // Initialize BLE and set the device name
  const char* deviceName = "ESP32 BLE Server";
  BLEDevice::init(deviceName);
  // Get the MAC address of the ESP32
  String macAddress = BLEDevice::getAddress().toString().c_str();
  // Print the MAC address and device name to the Serial Monitor
  Serial.print("Device Name: ");
  Serial.println(deviceName);
  Serial.print("ESP32 MAC Address: ");
  Serial.println(macAddress);
  // Create BLE Server
  BLEServer *pServer = BLEDevice::createServer();
  // Create the BLE Service
  BLEService *pService = pServer->createService(SERVICE_UUID);
  // Create a BLE Characteristic
  BLECharacteristic *pCharacteristic = pService->createCharacteristic(
                                        CHARACTERISTIC_UUID,
                                        BLECharacteristic::PROPERTY_READ |
                                        BLECharacteristic::PROPERTY_WRITE
                                      );
  // Set a default value
  pCharacteristic->setValue("Hello from ESP32");
  // Set the callback to handle client writes
  pCharacteristic->setCallbacks(new MyCharacteristicCallbacks());
  // Start the service
  pService->start();
  // Start advertising
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setScanResponse(true);
  pAdvertising->setMinPreferred(0x06);  // helps with iPhone connections issues
  pAdvertising->setMinPreferred(0x12);
  BLEDevice::startAdvertising();
  Serial.println("Characteristic defined! Waiting for a client to write values (1-5)...");
}
void loop() {
  delay(2000);
}
// Dummy functions
void function1() { Serial.println("Function 1 triggered!"); }
void function2() { Serial.println("Function 2 triggered!"); }
void function3() { Serial.println("Function 3 triggered!"); }
void function4() { Serial.println("Function 4 triggered!"); }
void function5() { Serial.println("Function 5 triggered!"); }
