#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <ArduinoJson.h>

// ============ WiFi Configuration ============
const char* ssid = "Wokwi-GUEST";
const char* password = "";

// ============ MQTT Configuration ============
// Wokwi gateway IP - connects to MQTT broker running in Docker
const char* mqtt_server = "192.168.240.1";  // Wokwi gateway (correct for simulation)
const int mqtt_port = 1883;

// ============ Pin Definitions ============
#define DHTPIN 4
#define DHTTYPE DHT22
#define SOIL_MOISTURE_PIN 34
#define LIGHT_PIN 35
#define PUMP_PIN 5
#define FAN_PIN 18
#define GROW_LIGHT_PIN 19

// ============ Global Objects ============
DHT dht(DHTPIN, DHTTYPE);
WiFiClient espClient;
PubSubClient client(espClient);

// ============ Global Variables ============
unsigned long lastSensorRead = 0;
unsigned long lastMqttPublish = 0;
const unsigned long SENSOR_INTERVAL = 2000;  // 2 seconds
const unsigned long MQTT_INTERVAL = 2000;    // 2 seconds

// Sensor smoothing - 5-sample rolling average
#define SMOOTHING_SIZE 5
float tempBuffer[SMOOTHING_SIZE] = {0.0};
float humidityBuffer[SMOOTHING_SIZE] = {0.0};
int moistureBuffer[SMOOTHING_SIZE] = {0};
int lightBuffer[SMOOTHING_SIZE] = {0};
int bufferIndex = 0;

// Deduplication - store combined sensor string to prevent duplicate publishes
String lastPublishedSensorString = "";

float temperature = 0.0;
float humidity = 0.0;
int soilMoisture = 0;
int lightIntensity = 0;

bool pumpStatus = false;
bool fanStatus = false;
bool growLightStatus = false;

// ============ Function Prototypes ============
void setup_wifi();
void setup_mqtt();
void reconnect_mqtt();
void callback(char* topic, byte* payload, unsigned int length);
void read_sensors();
void publish_sensor_data();
void publish_status();
void control_actuators();

// ============ Sensor Smoothing Helper Functions ============
float getSmoothedFloat(float* buffer, int size) {
  float sum = 0.0;
  for (int i = 0; i < size; i++) {
    sum += buffer[i];
  }
  return sum / size;
}

int getSmoothedInt(int* buffer, int size) {
  long sum = 0;
  for (int i = 0; i < size; i++) {
    sum += buffer[i];
  }
  return sum / size;
}

// ============ Deduplication Helper Function ============
// Creates a combined string of all sensor values for deduplication
String createSensorString() {
  String sensorString = "";
  sensorString += "T:";
  sensorString += (int)temperature;  // Use integer part to avoid float precision issues
  sensorString += "H:";
  sensorString += (int)humidity;
  sensorString += "M:";
  sensorString += soilMoisture;
  sensorString += "L:";
  sensorString += lightIntensity;
  return sensorString;
}

// Check if sensor data has changed since last published reading
boolean hasSensorDataChanged() {
  String currentSensorString = createSensorString();
  
  if (currentSensorString != lastPublishedSensorString) {
    lastPublishedSensorString = currentSensorString;
    Serial.printf("[Dedup] Sensor data changed: %s - will publish\n", currentSensorString.c_str());
    return true;
  }
  
  Serial.println("[Dedup] No change - skipping publish");
  return false;
}

// ============ Setup ============
void setup() {
  Serial.begin(115200);
  delay(2000);
  Serial.println("\n\nStarting Smart Plant IoT System...");
  
  // Initialize pins
  pinMode(PUMP_PIN, OUTPUT);
  pinMode(FAN_PIN, OUTPUT);
  pinMode(GROW_LIGHT_PIN, OUTPUT);
  
  // Initialize all actuators as OFF
  digitalWrite(PUMP_PIN, LOW);
  digitalWrite(FAN_PIN, LOW);
  digitalWrite(GROW_LIGHT_PIN, LOW);
  
  // Initialize DHT sensor
  dht.begin();
  delay(2000);
  
  // Connect to WiFi and MQTT
  setup_wifi();
  setup_mqtt();
  
  Serial.println("Setup Complete!");
}

// ============ Main Loop ============
void loop() {
  // Maintain MQTT connection
  if (!client.connected()) {
    reconnect_mqtt();
  }
  client.loop();
  
  // Read sensors at interval
  unsigned long currentTime = millis();
  if (currentTime - lastSensorRead >= SENSOR_INTERVAL) {
    read_sensors();
    lastSensorRead = currentTime;
  }
  
  // Publish data at interval
  if (currentTime - lastMqttPublish >= MQTT_INTERVAL) {
    publish_sensor_data();
    publish_status();
    control_actuators();
    lastMqttPublish = currentTime;
  }
  
  delay(100);  // Small delay to prevent blocking
}

// ============ WiFi Setup ============
void setup_wifi() {
  delay(10);
  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  Serial.println();
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("WiFi connected");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("Failed to connect WiFi (continuing with MQTT simulation)");
  }
}

// ============ MQTT Setup ============
void setup_mqtt() {
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
}

// ============ MQTT Reconnect ============
void reconnect_mqtt() {
  int attempts = 0;
  while (!client.connected() && attempts < 3) {
    Serial.print("Attempting MQTT connection...");
    
    // Create unique client ID
    String clientId = "ESP32-";
    clientId += String(random(0xffff), HEX);
    
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      
      // Subscribe to command topics
      client.subscribe("plant-iot/actuators/pump");
      client.subscribe("plant-iot/actuators/fan");
      client.subscribe("plant-iot/actuators/grow-light");
      client.subscribe("plant-iot/control/all");
      
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
    attempts++;
  }
}

// ============ MQTT Callback ============
void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived on topic: ");
  Serial.println(topic);
  
  // Parse JSON payload
  StaticJsonDocument<200> doc;
  DeserializationError error = deserializeJson(doc, payload, length);
  
  if (error) {
    Serial.print("JSON parse error: ");
    Serial.println(error.f_str());
    return;
  }
  
  // Handle pump commands
  if (strcmp(topic, "plant-iot/actuators/pump") == 0) {
    if (doc["action"] == "ON") {
      pumpStatus = true;
      digitalWrite(PUMP_PIN, HIGH);
      Serial.println("Pump turned ON");
    } else if (doc["action"] == "OFF") {
      pumpStatus = false;
      digitalWrite(PUMP_PIN, LOW);
      Serial.println("Pump turned OFF");
    }
  }
  
  // Handle fan commands
  else if (strcmp(topic, "plant-iot/actuators/fan") == 0) {
    if (doc["action"] == "ON") {
      fanStatus = true;
      digitalWrite(FAN_PIN, HIGH);
      Serial.println("Fan turned ON");
    } else if (doc["action"] == "OFF") {
      fanStatus = false;
      digitalWrite(FAN_PIN, LOW);
      Serial.println("Fan turned OFF");
    }
  }
  
  // Handle grow light commands
  else if (strcmp(topic, "plant-iot/actuators/grow-light") == 0) {
    if (doc["action"] == "ON") {
      growLightStatus = true;
      digitalWrite(GROW_LIGHT_PIN, HIGH);
      Serial.println("Grow Light turned ON");
    } else if (doc["action"] == "OFF") {
      growLightStatus = false;
      digitalWrite(GROW_LIGHT_PIN, LOW);
      Serial.println("Grow Light turned OFF");
    }
  }
  
  // Handle global control
  else if (strcmp(topic, "plant-iot/control/all") == 0) {
    bool enable = doc["enable"];
    digitalWrite(PUMP_PIN, enable ? HIGH : LOW);
    digitalWrite(FAN_PIN, enable ? HIGH : LOW);
    digitalWrite(GROW_LIGHT_PIN, enable ? HIGH : LOW);
    pumpStatus = fanStatus = growLightStatus = enable;
    Serial.printf("All actuators turned %s\n", enable ? "ON" : "OFF");
  }
}

// ============ Read Sensors ============
void read_sensors() {
  // Read DHT22 (Temperature & Humidity)
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  
  // Store in buffers for smoothing
  if (!isnan(h)) {
    humidityBuffer[bufferIndex] = h;
  }
  if (!isnan(t)) {
    tempBuffer[bufferIndex] = t;
  }
  
  // Read ADC sensors
  moistureBuffer[bufferIndex] = analogRead(SOIL_MOISTURE_PIN);
  lightBuffer[bufferIndex] = analogRead(LIGHT_PIN);
  
  // Move to next buffer position
  bufferIndex = (bufferIndex + 1) % SMOOTHING_SIZE;
  
  // Get smoothed (averaged) values
  temperature = getSmoothedFloat(tempBuffer, SMOOTHING_SIZE);
  humidity = getSmoothedFloat(humidityBuffer, SMOOTHING_SIZE);
  soilMoisture = getSmoothedInt(moistureBuffer, SMOOTHING_SIZE);
  lightIntensity = getSmoothedInt(lightBuffer, SMOOTHING_SIZE);
  
  Serial.printf("Sensors [Smoothed] - Temp: %.1f°C, Humidity: %.1f%%, Moisture: %d, Light: %d\n",
                temperature, humidity, soilMoisture, lightIntensity);
}

// ============ Publish Sensor Data ============
void publish_sensor_data() {
  if (!client.connected()) return;
  
  // Check if sensor data has changed using the deduplication function
  if (!hasSensorDataChanged()) {
    return;  // Data hasn't changed, skip publishing
  }
  
  char buffer[512];
  
  // Create AGGREGATED sensor data JSON (main format for backend)
  StaticJsonDocument<256> aggregatedDoc;
  aggregatedDoc["temperature"] = temperature;
  aggregatedDoc["humidity"] = humidity;
  aggregatedDoc["soil_moisture"] = soilMoisture;
  aggregatedDoc["soil_moisture_percent"] = map(soilMoisture, 1023, 0, 0, 100);
  aggregatedDoc["light_intensity"] = lightIntensity;
  aggregatedDoc["light_percent"] = map(lightIntensity, 0, 4095, 0, 100);
  aggregatedDoc["timestamp"] = millis();
  aggregatedDoc["device_id"] = "ESP32-Plant-01";
  aggregatedDoc["quality"] = "excellent";
  
  // Publish aggregated data (this is what backend expects)
  serializeJson(aggregatedDoc, buffer);
  client.publish("plant-iot/sensors/aggregated", buffer);
  Serial.printf("[MQTT] Published aggregated sensor data\n");
  
  // Also publish individual sensor topics (for backward compatibility)
  StaticJsonDocument<100> tempDoc;
  tempDoc["temperature"] = temperature;
  tempDoc["unit"] = "celsius";
  tempDoc["timestamp"] = millis();
  
  StaticJsonDocument<100> humidityDoc;
  humidityDoc["humidity"] = humidity;
  humidityDoc["unit"] = "percent";
  humidityDoc["timestamp"] = millis();
  
  StaticJsonDocument<100> moistureDoc;
  moistureDoc["moisture"] = soilMoisture;
  moistureDoc["unit"] = "adc_0-4095";
  moistureDoc["moisture_percent"] = map(soilMoisture, 1023, 0, 0, 100);
  moistureDoc["timestamp"] = millis();
  
  StaticJsonDocument<100> lightDoc;
  lightDoc["light"] = lightIntensity;
  lightDoc["unit"] = "adc_0-4095";
  lightDoc["light_percent"] = map(lightIntensity, 0, 4095, 0, 100);
  lightDoc["timestamp"] = millis();
  
  // Publish to MQTT
  char buffer[256];
  
  serializeJson(tempDoc, buffer);
  client.publish("plant-iot/sensors/temperature", buffer);
  
  serializeJson(humidityDoc, buffer);
  client.publish("plant-iot/sensors/humidity", buffer);
  
  serializeJson(moistureDoc, buffer);
  client.publish("plant-iot/sensors/soil-moisture", buffer);
  
  serializeJson(lightDoc, buffer);
  client.publish("plant-iot/sensors/light", buffer);
}

// ============ Publish Status ============
void publish_status() {
  if (!client.connected()) return;
  
  char buffer[256];
  
  // Publish pump status
  StaticJsonDocument<100> pumpStatusDoc;
  pumpStatusDoc["status"] = pumpStatus ? "ON" : "OFF";
  pumpStatusDoc["timestamp"] = millis();
  serializeJson(pumpStatusDoc, buffer);
  client.publish("plant-iot/status/pump", buffer);
  
  // Publish fan status
  StaticJsonDocument<100> fanStatusDoc;
  fanStatusDoc["status"] = fanStatus ? "ON" : "OFF";
  fanStatusDoc["timestamp"] = millis();
  serializeJson(fanStatusDoc, buffer);
  client.publish("plant-iot/status/fan", buffer);
  
  // Publish grow light status
  StaticJsonDocument<100> lightStatusDoc;
  lightStatusDoc["status"] = growLightStatus ? "ON" : "OFF";
  lightStatusDoc["timestamp"] = millis();
  serializeJson(lightStatusDoc, buffer);
  client.publish("plant-iot/status/grow-light", buffer);
  
  // Also publish aggregated status
  StaticJsonDocument<200> statusDoc;
  statusDoc["pump"] = pumpStatus ? "ON" : "OFF";
  statusDoc["fan"] = fanStatus ? "ON" : "OFF";
  statusDoc["grow_light"] = growLightStatus ? "ON" : "OFF";
  statusDoc["rssi"] = WiFi.RSSI();
  statusDoc["uptime"] = millis();
  serializeJson(statusDoc, buffer);
  client.publish("plant-iot/status/all", buffer);
}

// ============ Control Actuators (Local Logic) ============
void control_actuators() {
  // Auto-control based on sensor readings
  // This is optional; main control comes from MQTT commands
  
  // Example: Auto fan if temperature > 30°C
  if (temperature > 30 && !fanStatus) {
    Serial.println("Auto: Turning on fan (High temp)");
    // Could publish to self or just control directly
  }
  
  // Example: Auto pump if soil moisture < 30%
  int moisturePercent = map(soilMoisture, 1023, 0, 0, 100);
  if (moisturePercent < 30 && !pumpStatus) {
    Serial.println("Auto: Turning on pump (Low moisture)");
    // Could publish to self or just control directly
  }
}