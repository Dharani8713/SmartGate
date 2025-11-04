#include <ArduCAM.h>
#include <Wire.h>
#include <SPI.h>
#include <Servo.h>
#include "memorysaver.h"

#define CS_PIN 7           // Camera Chip Select pin
#define TRIG_PIN 9         // Ultrasonic trigger pin
#define ECHO_PIN 10        // Ultrasonic echo pin
#define LED_PIN 6          // LED indicator pin
#define SERVO_PIN 5        // Servo motor pin (for gate)

ArduCAM myCAM(OV2640, CS_PIN);
Servo gateServo;

void setup() {
  Serial.begin(115200);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(LED_PIN, OUTPUT);
  gateServo.attach(SERVO_PIN);
  gateServo.write(0); // Gate closed

  Wire.begin();
  SPI.begin();

  myCAM.set_format(JPEG);
  myCAM.InitCAM();
  myCAM.OV2640_set_JPEG_size(OV2640_640x480);
  delay(1000);

  Serial.println("Camera & System Ready");
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
  distance = (duration * 0.034) / 2; // cm

  if (distance < 50 && distance > 0) { // Vehicle detected
    Serial.println("Vehicle Detected");
    delay(1000);

    // --- Capture image from ArduCAM ---
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

    // --- Wait for Python Response ---
    while (!Serial.available());
    String response = Serial.readStringUntil('\n');
    response.trim();

    if (response == "OPEN_GATE") {
      digitalWrite(LED_PIN, HIGH);
      Serial.println("Authorized Vehicle - Opening Gate...");
      gateServo.write(90); // Open
      delay(4000);
      gateServo.write(0);  // Close
      digitalWrite(LED_PIN, LOW);
      Serial.println("Gate Closed");
    }
    else if (response == "CLOSE_GATE") {
      Serial.println("Unauthorized or Blocked Vehicle - Access Denied");
      digitalWrite(LED_PIN, HIGH);
      delay(3000);
      digitalWrite(LED_PIN, LOW);
    }
  }

  delay(1000);
}
