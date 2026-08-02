#include <Arduino.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266WiFi.h>

// Copy config.h.example to config.h and set the installation-specific values.
#include "config.h"

namespace {

constexpr unsigned long WIFI_RETRY_INTERVAL_MS = 10000;
constexpr unsigned long READING_POST_INTERVAL_MS = 20000;

unsigned long lastActivation = 0;
unsigned long lastWiFiAttempt = 0;
unsigned long lastReadingSent = 0;

void setActivationIndicator(bool active) {
  digitalWrite(LED_BUILTIN, active ? LOW : HIGH);
}

unsigned long measureLightLevel() {
  return 1024 - analogRead(A0);
}

bool shouldActivate(unsigned long value) {
  return value > ACTIVATION_THRESHOLD;
}

void connectToWiFi() {
  if (WiFi.status() == WL_CONNECTED) {
    return;
  }

  const unsigned long now = millis();
  if (lastWiFiAttempt != 0 && now - lastWiFiAttempt < WIFI_RETRY_INTERVAL_MS) {
    return;
  }

  lastWiFiAttempt = now;
  Serial.printf("Connecting to Wi-Fi: %s\n", WIFI_SSID);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  const unsigned long deadline = millis() + WIFI_CONNECT_TIMEOUT_MS;
  while (WiFi.status() != WL_CONNECTED && millis() < deadline) {
    delay(250);
    Serial.print('.');
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("Wi-Fi connected, IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("Wi-Fi connection failed");
  }
}

void sendHomeAssistantPost(const char* webhookUrl, unsigned long value,
                           const char* description) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.printf("Skipping %s: Wi-Fi is not connected\n", description);
    return;
  }

  WiFiClient client;
  HTTPClient http;
  if (!http.begin(client, webhookUrl)) {
    Serial.printf("Could not initialize Home Assistant client for %s\n", description);
    return;
  }

  http.addHeader("Content-Type", "application/json");
  const String body = String("{\"value\":") + value + "}";
  const int status = http.POST(body);

  Serial.printf("Home Assistant %s response: %d\n", description, status);
  if (status > 0) {
    Serial.println(http.getString());
  } else {
    Serial.printf("Home Assistant %s request failed: %s\n", description,
                  http.errorToString(status).c_str());
  }
  http.end();
}

}  // namespace

void setup() {
  Serial.begin(115200);
  delay(100);
  Serial.println();
  pinMode(LED_BUILTIN, OUTPUT);
  setActivationIndicator(false);
  Serial.printf("Starting door opener, threshold: %lu, retry timeout: %lu ms\n",
                ACTIVATION_THRESHOLD, RETRY_TIMEOUT_MS);

  WiFi.hostname(DEVICE_HOSTNAME);
  connectToWiFi();
}

void loop() {
  connectToWiFi();

  const unsigned long firstReading = measureLightLevel();
  const unsigned long secondReading = measureLightLevel();
  const unsigned long average = (firstReading + secondReading) / 2;

  Serial.printf("r1: %lu | r2: %lu | avg: %lu\n",
                firstReading, secondReading, average);

  const bool aboveActivationThreshold = shouldActivate(average);
  setActivationIndicator(aboveActivationThreshold);

  if (aboveActivationThreshold) {
    const unsigned long now = millis();
    if (lastActivation != 0 && now - lastActivation < RETRY_TIMEOUT_MS) {
      Serial.println("Skipping activation: retry timeout has not elapsed");
    } else {
      Serial.printf("Activating switch: %lu\n", average);
      sendHomeAssistantPost(HOME_ASSISTANT_WEBHOOK_URL, average, "activation");
      lastActivation = now;
    }
  }

  const unsigned long now = millis();
  if (now - lastReadingSent >= READING_POST_INTERVAL_MS) {
    sendHomeAssistantPost(READING_WEBHOOK_URL, average, "reading");
    lastReadingSent = now;
  }
  
  delay(1000);
}
