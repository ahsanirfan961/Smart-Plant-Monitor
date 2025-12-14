# MQTT Broker Configuration

## Overview
This directory contains the MQTT broker configuration using Mosquitto, a lightweight open-source MQTT broker.

The broker is containerized using Docker for easy deployment and isolation.

## Mosquitto Configuration

### Port Configuration
- **Port 1883**: Standard MQTT (unencrypted)
- **Port 9001**: WebSocket protocol (for web clients)

### Default Settings
- **Persistence**: Disabled (for simulation)
- **Authentication**: None (localhost only)
- **Max Connections**: 100
- **QoS Support**: 0, 1, 2

## Running Mosquitto

### Via Docker Compose (Recommended)
```bash
docker-compose up -d mosquitto
```

### Via Docker directly
```bash
docker run -d \
  --name mosquitto \
  -p 1883:1883 \
  -p 9001:9001 \
  -v $(pwd)/mosquitto.conf:/mosquitto/config/mosquitto.conf \
  eclipse-mosquitto
```

### Via Docker Compose Full Setup
See `docker-compose.yml` in the root directory

## Testing MQTT Broker

### Using mosquitto_pub/mosquitto_sub
```bash
# Subscribe to all topics
mosquitto_sub -h localhost -t "plant-iot/#" -v

# Publish test message
mosquitto_pub -h localhost -t "plant-iot/sensors/temperature" -m '{"temp": 24.5}'
```

### Using VSMqtt in VS Code
1. Open Command Palette (Ctrl+Shift+P)
2. Search for "MQTT: Create MQTT Client"
3. Connect to `mqtt://localhost:1883`
4. Subscribe to topics: `plant-iot/#`

## Topic Structure

```
plant-iot/
├── sensors/
│   ├── temperature         # JSON: {temperature, unit, timestamp}
│   ├── humidity           # JSON: {humidity, unit, timestamp}
│   ├── soil-moisture      # JSON: {moisture, moisture_percent, timestamp}
│   └── light              # JSON: {light, light_percent, timestamp}
├── actuators/
│   ├── pump               # Command topic: {"action": "ON/OFF"}
│   ├── fan                # Command topic: {"action": "ON/OFF"}
│   └── grow-light         # Command topic: {"action": "ON/OFF"}
├── status/
│   ├── actuators          # JSON: {pump, fan, grow_light, uptime}
│   └── device             # JSON: {device_id, status, rssi}
├── analytics/
│   ├── predictions        # ML predictions: {soil_dryness_eta, recommendation}
│   └── health            # Plant health score
├── control/
│   └── all                # Emergency control: {"enable": true/false}
└── events/
    ├── alerts             # System alerts
    └── errors             # Error messages
```

## Message Format Examples

### Temperature Sensor Data
```json
{
  "temperature": 24.5,
  "unit": "celsius",
  "timestamp": 1702400000000
}
```

### Soil Moisture Data
```json
{
  "moisture": 2500,
  "unit": "adc_0-4095",
  "moisture_percent": 61,
  "timestamp": 1702400000000
}
```

### Actuator Command
```json
{
  "action": "ON"
}
```

### Actuator Status
```json
{
  "pump": "ON",
  "fan": "OFF",
  "grow_light": "ON",
  "rssi": -45,
  "uptime": 123456789
}
```

## Docker Network

When using Docker Compose, services connect via:
- **Service Name**: `mosquitto`
- **Internal Port**: `1883`
- **External Port**: `1883` (mapped)

Example Python connection:
```python
client = mqtt.Client()
client.connect("mosquitto", 1883, 60)  # Service name from docker-compose
```

## Troubleshooting

### Broker won't start
```bash
docker-compose logs mosquitto
```

### Can't connect from host
- Check port mappings: `docker ps`
- Test connectivity: `telnet localhost 1883`
- Verify firewall rules

### MQTT messages not flowing
1. Check broker logs: `docker logs mosquitto`
2. Verify topic subscriptions match publish topics
3. Ensure QoS levels are compatible

## Files

- `mosquitto.conf`: Main configuration file
- `docker-compose.yml`: Container orchestration (in root)
- This README

## Security Notes

For production, consider:
- Enable authentication (username/password)
- Use TLS/SSL encryption (port 8883)
- Restrict network access
- Implement ACL (Access Control Lists)
