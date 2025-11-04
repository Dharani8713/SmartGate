#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "YourWiFiName";         // ✅ replace with your WiFi name
const char* password = "YourWiFiPassword"; // ✅ replace with your WiFi password
String serverName = "http://192.168.1.100:5000/api/alerts"; // Flask server URL

String imageData = "";
float distance = 0.0;
bool capturing = false;

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  Serial.println("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\n✅ WiFi Connected!");
}

void loop() {
  // Listen for Serial messages from Arduino Uno
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    line.trim();

    // Start receiving image
    if (line == "STARTIMG") {
      imageData = "";
      capturing = true;
      Serial.println("📸 Start receiving image data...");
    }

    // End of image
    else if (line == "ENDIMG") {
      capturing = false;
      Serial.println("✅ Image data complete. Sending to Flask server...");
      sendToServer();
    }

    // Distance info
    else if (line.startsWith("DISTANCE:")) {
      distance = line.substring(9).toFloat();
      Serial.print("📏 Distance received: ");
      Serial.println(distance);
    }

    // Collect image Base64 data between markers
    else if (capturing) {
      imageData += line;
    }
  }
}

void sendToServer() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverName);
    http.addHeader("Content-Type", "application/json");

    // Create JSON payload
    String json = "{\"image\":\"" + imageData + "\", \"distance\":" + String(distance, 2) + "}";

    int httpResponseCode = http.POST(json);

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("📡 Server Response: " + response);
    } else {
      Serial.print("❌ Error Sending: ");
      Serial.println(httpResponseCode);
    }

    http.end();
  } else {
    Serial.println("⚠ WiFi Disconnected!");
  }
}
