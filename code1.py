int pirPin = 2;       // PIR sensor output pin
int ledPin = 13;      // LED output pin
int pirState = LOW;   // Start with no motion detected
int val = 0;          // Variable for reading the pin status

void setup() {
  pinMode(ledPin, OUTPUT);
  pinMode(pirPin, INPUT);
  Serial.begin(9600);
}

void loop() {
  val = digitalRead(pirPin);  // Read input value
  if (val == HIGH) {          // Check if motion detected
    digitalWrite(ledPin, HIGH); // Turn LED on
    if (pirState == LOW) {
      Serial.println("Motion detected!");
      pirState = HIGH;
    }
  } else {
    digitalWrite(ledPin, LOW); // Turn LED o

