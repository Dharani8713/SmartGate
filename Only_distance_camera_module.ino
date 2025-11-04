#include <ArduCAM.h>
#include <Wire.h>
#include <SPI.h>
#include "memorysaver.h"
// 🔧 Pin Configuration
#define CS_PIN 7           // Camera Chip Select pin
#define TRIG_PIN 9         // Ultrasonic Trigger pin
#define ECHO_PIN 10        // Ultrasonic Echo pin
#define LED_PIN 6          // LED Indicator pin

ArduCAM myCAM(OV2640, CS_PIN);

void setup() {
  Serial.begin(115200);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(LED_PIN, OUTPUT);

  // Initialize camera
  Wire.begin();
  SPI.begin();
  myCAM.set_format(JPEG);
  myCAM.InitCAM();
  myCAM.OV2640_set_JPEG_size(OV2640_640x480);
  delay(1000);

  Serial.println("✅ Distance + Camera Module Ready");
}

void loop() {
  long duration;
  int distance;

  // Measure distance using HC-SR04
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  duration = pulseIn(ECHO_PIN, HIGH);
  distance = (duration * 0.034) / 2; // convert to cm

  // If object within 50 cm → capture image
  if (distance > 0 && distance < 50) {
    Serial.println("🚗 Vehicle Detected");
    digitalWrite(LED_PIN, HIGH);
    delay(1000);

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
    digitalWrite(LED_PIN, LOW);
    delay(5000);
  }

  delay(500);
}
