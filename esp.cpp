#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "YourWiFiName";
const char* password = "YourWiFiPassword";
String serverName = "http://192.168.1.100:5000/api/alerts"; // Flask server URL

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  Serial.println("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nWiFi Connected!");
}

void loop() {
  if (Serial.available()) {
    String data = Serial.readStringUntil('\n');
    data.trim();

    if (data == "STARTIMG") {
      Serial.println("Receiving image...");
      // Image handling part would be here
    }
    else if (data == "ENDIMG") {
      HTTPClient http;
      http.begin(serverName);
      http.addHeader("Content-Type", "application/json");
      String json = "{\"message\":\"Vehicle Detected\"}";
      int httpResponseCode = http.POST(json);

      if (httpResponseCode > 0) {
        String response = http.getString();
        Serial.println(response);
      }
      http.end();
    }
  }
}
