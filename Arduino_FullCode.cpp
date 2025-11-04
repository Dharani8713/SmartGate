#include <ArduCAM.h>
#include <Wire.h>
#include <SPI.h>
#include <Servo.h>
#include "memorysaver.h"

#define CS_PIN 7
#define TRIG_PIN 9
#define ECHO_PIN 10
#define PIR_PIN 8
#define GREEN_LED 6
#define RED_LED 4
#define SERVO_PIN 5

ArduCAM myCAM(OV2640, CS_PIN);
Servo gateServo;

void setup() {
  Serial.begin(115200);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(PIR_PIN, INPUT);
  pinMode(GREEN_LED, OUTPUT);
  pinMode(RED_LED, OUTPUT);

  gateServo.attach(SERVO_PIN);
  gateServo.write(0); // Gate closed position

  Wire.begin();
  SPI.begin();
  myCAM.set_format(JPEG);
  myCAM.InitCAM();
  myCAM.OV2640_set_JPEG_size(OV2640_640x480);
  delay(1000);

  Serial.println("Camera & Sensors Ready");
}

void loop() {
  long duration, distance;
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  duration = pulseIn(ECHO_PIN, HIGH);
  distance = (duration * 0.034) / 2; // in cm

  int motion = digitalRead(PIR_PIN);

  if (distance < 100 && motion == HIGH) {
    Serial.println("Vehicle Detected");

    // Capture Image
    myCAM.flush_fifo();
    myCAM.clear_fifo_flag();
    myCAM.start_capture();
    while (!myCAM.get_bit(ARDUCHIP_TRIG, CAP_DONE_MASK));

    Serial.println("STARTIMG");

    uint8_t temp;
    myCAM.CS_LOW();
    myCAM.set_fifo_burst();
    while (myCAM.read_fifo_burst(&temp, 1)) {
      Serial.write(temp);
    }
    myCAM.CS_HIGH();

    Serial.println("ENDIMG");
    delay(2000);
  }

  // Check for command from ESP32
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command == "AUTHORIZED") {
      digitalWrite(GREEN_LED, HIGH);
      gateServo.write(90); // Open gate
      delay(5000);
      gateServo.write(0);  // Close gate
      digitalWrite(GREEN_LED, LOW);
      Serial.println("Gate Closed");
    } else if (command == "UNAUTHORIZED") {
      digitalWrite(RED_LED, HIGH);
      delay(3000);
      digitalWrite(RED_LED, LOW);
    }
  }
}
