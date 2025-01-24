/*
  Written by Sean Omodon
  October 29, 2024
  LHNT Rover Fall 2024
*/

// Made for a rover using one H-bridge motor driver to control 4 DC motors. 

// From HSI
#include <WiFi.h>
#include <WiFiUdp.h>
const char* ssid = "ESP32-LHNT";
const char* password = "longhorns";
WiFiUDP udp;
const int localUdpPort = 1234;  // Port for receiving

// Motor A
const int MOTOR_A_PIN_1 = 27;
const int MOTOR_A_PIN_2 = 26;
const int ENABLE_A_PIN = 14;

// Motor B
const int MOTOR_B_PIN_1 = 32;
const int MOTOR_B_PIN_2 = 33;
const int ENABLE_B_PIN = 25;

// Setting motor A PWM properties
const int FREQUENCY_A = 30000;
const int PWM_CHANNEL_A = 0;
const int RESOLUTION_A = 8;
int dutyCycleA = 190; // controls speed

// Setting motor B PWM properties
const int FREQUENCY_B = 30000;
const int PWM_CHANNEL_B = 0; // uses same channel as A. Can be changed if we want finer motor control.
const int RESOLUTION_B = 8;
int dutyCycleB = 190; // controls speed

void stopLeft() {
  digitalWrite(MOTOR_A_PIN_1, LOW);
  digitalWrite(MOTOR_A_PIN_2, LOW);
}

void stopRight() {
  digitalWrite(MOTOR_B_PIN_1, LOW);
  digitalWrite(MOTOR_B_PIN_2, LOW);
}

void leftForward() {
  digitalWrite(MOTOR_A_PIN_1, HIGH);
  digitalWrite(MOTOR_A_PIN_2, LOW);
}

void leftBackward() {
  digitalWrite(MOTOR_A_PIN_1, LOW);
  digitalWrite(MOTOR_A_PIN_2, HIGH);
}

void rightForward() {
  digitalWrite(MOTOR_B_PIN_1, HIGH);
  digitalWrite(MOTOR_B_PIN_2, LOW);
}

void rightBackward() {
  digitalWrite(MOTOR_B_PIN_1, LOW);
  digitalWrite(MOTOR_B_PIN_2, HIGH);
}

void forward() {
  leftForward();
  rightForward();
}

void backward() {
  leftBackward();
  rightBackward();
}

void turnLeft() {
  leftBackward();
  rightForward();
}

void turnRight() {
  leftForward();
  rightBackward();
}

void stopAll() {
  stopLeft();
  stopRight();
}

void processCommand() {
  Serial.print("Recieved: ");
  Serial.println(command);
  if (command == 1) {
    Serial.println("Moving forward.");
    forward();
  }
  else if (command == 0) {
    Serial.println("Stopping.");
    stopAll();
  }
  else if (command == 2) {
    Serial.println("Moving backward.");
    backward();
  }
  else if (command == 3) {
    Serial.println("Turning left.");
    turnLeft();
  }
  else if (command == 4) {
    Serial.println("Turning right.");
    turnRight();
  } 
}

void readInput() {
  // From HSI
  int packetSize = udp.parsePacket();
  if (packetSize) {
    // Allocate buffer to store received data
    char incomingPacket[255];
    int len = udp.read(incomingPacket, 255);
    if (len > 0) {
      incomingPacket[len] = '\0';  // Null-terminate the string
    }
    Serial.print("Received message: ");
    Serial.println(incomingPacket);
    // Convert received data to an integer and call the respective function
    int command = toInt(incomingPacket);
    processCommand();
}

void setup() {
  Serial.begin(115200);

  // Setting pin modes
  pinMode(MOTOR_A_PIN_1, OUTPUT);
  pinMode(MOTOR_A_PIN_2, OUTPUT);
  pinMode(ENABLE_A_PIN, OUTPUT);
  pinMode(MOTOR_B_PIN_1, OUTPUT);
  pinMode(MOTOR_B_PIN_2, OUTPUT);
  pinMode(ENABLE_B_PIN, OUTPUT);
  
  // configure LEDC PWM
  ledcAttachChannel(ENABLE_A_PIN, FREQUENCY_A, RESOLUTION_A, PWM_CHANNEL_A);
  ledcAttachChannel(ENABLE_B_PIN, FREQUENCY_B, RESOLUTION_B, PWM_CHANNEL_B);

  // set speed of motors
  ledcWrite(ENABLE_A_PIN, dutyCycleA);
  ledcWrite(ENABLE_B_PIN, dutyCycleB);

  // From HSI
  // Set up ESP32 as an access point
  WiFi.softAP(ssid, password);
  IPAddress IP = WiFi.softAPIP();
  Serial.print("Access Point IP: ");
  Serial.println(IP);
  // Start UDP server
  udp.begin(localUdpPort);

  Serial.print("Rover ready.");
}

void loop() {
  // check for new serial monitor input
  readInput();
}
