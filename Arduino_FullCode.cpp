#include <ArduCAM.h>
#include <Wire.h>
#include <SPI.h>
#include "memorysaver.h"

#define CS_PIN 7
#define TRIG_PIN 9
#define ECHO_PIN 10
#define PIR_PIN 8
#define LED_PIN 6

ArduCAM myCAM(OV2640, CS_PIN);

void setup() {
  Serial.begin(115200);      // Communication with PC (optional)
  Serial1.begin(9600);       // Communication with ESP32
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(PIR_PIN, INPUT);
  pinMode(LED_PIN, OUTPUT);

  SPI.begin();
  myCAM.set_format(JPEG);
  myCAM.InitCAM();
  myCAM.OV2640_set_JPEG_size(OV2640_640x480);
  delay(1000);

  Serial.println("Arduino ready - Sensors active");
}

void loop() {
  long duration, distance;
  bool motion = digitalRead(PIR_PIN);

  // Measure distance
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  duration = pulseIn(ECHO_PIN, HIGH);
  distance = (duration * 0.034) / 2;

  if (distance < 50 && motion) {
    Serial.println("Vehicle Detected");
    digitalWrite(LED_PIN, HIGH);
    delay(500);

    // Capture image
    myCAM.flush_fifo();
    myCAM.clear_fifo_flag();
    myCAM.start_capture();
    while (!myCAM.get_bit(ARDUCHIP_TRIG, CAP_DONE_MASK));

    // Notify ESP32 that image is ready
    Serial1.println("VEHICLE_DETECTED");

    // Send image data
    Serial1.println("STARTIMG");
    uint8_t temp;
    myCAM.CS_LOW();
    myCAM.set_fifo_burst();
    while (myCAM.read_fifo_burst(&temp, 1)) {
      Serial1.write(temp);
    }
    myCAM.CS_HIGH();
    Serial1.println("ENDIMG");

    digitalWrite(LED_PIN, LOW);
    delay(3000);
  }

  delay(200);
}
