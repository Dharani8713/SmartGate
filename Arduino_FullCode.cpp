#include <ArduCAM.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>
#include "memorysaver.h"

#define CS_PIN 7           // Camera Chip Select pin
#define TRIG_PIN 9         // Ultrasonic trigger pin
#define ECHO_PIN 10        // Ultrasonic echo pin
#define LED_PIN 6          // LED indicator pin
#define MOTOR_PIN 5        // Motor control pin (for gate)

ArduCAM myCAM(OV2640, CS_PIN);

void setup() {
  Serial.begin(115200);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(LED_PIN, OUTPUT);
  pinMode(MOTOR_PIN, OUTPUT);

  Wire.begin();
  SPI.begin();

  myCAM.set_format(JPEG);
  myCAM.InitCAM();
  myCAM.OV2640_set_JPEG_size(OV2640_640x480);
  delay(1000);

  Serial.println("Camera Ready");
}

void loop() {
  long duration, distance;

  // --- Measure distance using ultrasonic sensor ---
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  duration = pulseIn(ECHO_PIN, HIGH);
  distance = (duration * 0.034) / 2; // distance in cm

  if (distance < 50) { // Vehicle detected within 50 cm
    Serial.println("Vehicle Detected");
    delay(1000);

    // --- Capture image ---
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
    delay(3000);
  }

  // --- Listen for response from Python ---
  if (Serial.available()) {
    String response = Serial.readStringUntil('\n');
    response.trim();

    if (response == "AUTHORIZED") {
      digitalWrite(LED_PIN, HIGH);
      digitalWrite(MOTOR_PIN, HIGH);   // Open gate
      Serial.println("Gate Opening for Authorized Vehicle...");
      delay(5000);
      digitalWrite(MOTOR_PIN, LOW);    // Close gate
      digitalWrite(LED_PIN, LOW);
      Serial.println("Gate Closed");
    } 
    else if (response == "UNAUTHORIZED") {
      digitalWrite(LED_PIN, HIGH);
      Serial.println("Unauthorized Vehicle - Access Denied");
      delay(3000);
      digitalWrite(LED_PIN, LOW);
    }
  }
}