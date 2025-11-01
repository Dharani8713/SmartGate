#include <ArduCAM.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>
#include "memorysaver.h"

#define CS_PIN 7     
#define TRIG_PIN 9   
#define ECHO_PIN 10  

ArduCAM myCAM(OV2640, CS_PIN);

void setup() {
  Serial.begin(115200);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

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

  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  duration = pulseIn(ECHO_PIN, HIGH);
  distance = (duration * 0.034) / 2;

  Serial.print("Distance: ");
  Serial.println(distance);

  if (distance < 50) { 
    Serial.println("Vehicle Detected");
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
    delay(5000); 
  }
}