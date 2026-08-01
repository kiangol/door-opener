#include <Arduino.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266WiFi.h>

// Copy config.h.example to config.h and set the installation-specific values.
#include "config.h"

namespace {

constexpr unsigned long SENSOR_DISCHARGE_MS = 500;
constexpr unsigned long SENSOR_TIMEOUT_COUNTS = 10000;
constexpr unsigned long WIFI_RETRY_INTERVAL_MS = 10000;

unsigned long lastActivation = 0;
unsigned long lastWiFiAttempt = 0;

unsigned long measureLightLevel() {
  unsigned long count = 0;

  pinMode(LDR_PIN, OUTPUT);
  digitalWrite(LDR_PIN, LOW);
  delay(SENSOR_DISCHARGE_MS);

  pinMode(LDR_PIN, INPUT);
  while (digitalRead(LDR_PIN) == LOW) {
    ++count;
    if (count >= SENSOR_TIMEOUT_COUNTS) {
      break;
    }

    // Keep the ESP8266 watchdog serviced if the sensor remains below the
    // input threshold for a long time.
    if ((count & 0xFF) == 0) {
      yield();
    }
  }

  return count;
}

bool shouldActivate(unsigned long value) {
  return value < ACTIVATION_THRESHOLD;
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

void sendHomeAssistantNotification(unsigned long value) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Skipping notification: Wi-Fi is not connected");
    return;
  }

  WiFiClient client;
  HTTPClient http;
  if (!http.begin(client, HOME_ASSISTANT_WEBHOOK_URL)) {
    Serial.println("Could not initialize Home Assistant HTTP client");
    return;
  }

  http.addHeader("Content-Type", "application/json");
  const String body = String("{\"value\":") + value + "}";
  const int status = http.POST(body);

  Serial.printf("Home Assistant response: %d\n", status);
  if (status > 0) {
    Serial.println(http.getString());
  } else {
    Serial.printf("Home Assistant request failed: %s\n", http.errorToString(status).c_str());
  }
  http.end();
}

}  // namespace

void setup() {
  Serial.begin(115200);
  delay(100);
  Serial.println();
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

  Serial.printf("LDR: %lu | %lu | average: %lu\n",
                firstReading, secondReading, average);

  if (shouldActivate(firstReading) && shouldActivate(secondReading)) {
    const unsigned long now = millis();
    if (lastActivation != 0 && now - lastActivation < RETRY_TIMEOUT_MS) {
      Serial.println("Skipping activation: retry timeout has not elapsed");
    } else {
      Serial.printf("Activating switch: %lu\n", average);
      sendHomeAssistantNotification(average);
      lastActivation = now;
    }
  }

  yield();
}
