int pirPin = 2;        // PIR sensor output pin
int ledPin = 13;       // LED output pin
int pirState = LOW;    // Start with no motion detected
int val = 0;           // Variable for reading the pin status

void setup() {
  pinMode(ledPin, OUTPUT);   // Set LED pin as output
  pinMode(pirPin, INPUT);    // Set PIR pin as input
  Serial.begin(9600);        // Initialize serial communication
}

void loop() {
  val = digitalRead(pirPin);    // Read PIR sensor value

  if (val == HIGH) {            // Motion detected
    digitalWrite(ledPin, HIGH); // Turn LED ON
    if (pirState == LOW) {
      Serial.println("Motion detected!");
      pirState = HIGH;
    }
  } 
  else {                        // No motion
    digitalWrite(ledPin, LOW);  // Turn LED OFF
    if (pirState == HIGH) {
      Serial.println("Motion ended!");
      pirState = LOW;
    }
  }
}
