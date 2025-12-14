# Sensor Data Service

## Purpose
This microservice simulates sensor data acquisition from the ESP32 and publishes it to MQTT topics. It can run independently of the Wokwi simulation for testing.

## Functionality

1. **Reads sensor data** from MQTT (subscribed to ESP32 published data)
2. **Validates sensor readings** (range checking, outlier detection)
3. **Publishes aggregated data** to Firebase
4. **Maintains sensor history** for analytics
5. **Detects anomalies** in sensor readings

## Configuration

### Environment Variables
```bash
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_USERNAME=          # Optional
MQTT_PASSWORD=          # Optional
LOG_LEVEL=INFO
DATA_RETENTION=30       # days
ANOMALY_THRESHOLD=2     # sigma
```

### Sensor Ranges
- **Temperature**: -10 to 50°C
- **Humidity**: 20 to 95%
- **Soil Moisture**: 0 to 4095 (ADC) or 0-100%
- **Light Intensity**: 0 to 4095 (ADC) or 0-100%

## Data Flow

```
MQTT Sensors Topic
        ↓
Validate & Parse
        ↓
Anomaly Detection
        ↓
Aggregate Data
        ↓
Publish to Storage
        ↓
Firebase / Local DB
```

## Files

- `main.py`: Entry point
- `sensor_reader.py`: MQTT subscription handler
- `data_processor.py`: Data validation & processing
- `anomaly_detector.py`: Outlier detection
- `publisher.py`: Data publication handler
- `requirements.txt`: Python dependencies

## Running

```bash
# Install dependencies
pip install -r requirements.txt

# Run service
python main.py
```

## API/Topics

### Subscribed Topics
- `plant-iot/sensors/temperature`
- `plant-iot/sensors/humidity`
- `plant-iot/sensors/soil-moisture`
- `plant-iot/sensors/light`

### Published Topics
- `plant-iot/sensors/aggregated` - Combined sensor data
- `plant-iot/analytics/anomalies` - Detected anomalies
- `plant-iot/data/history` - Historical data

## Output Example

```json
{
  "timestamp": 1702400000000,
  "temperature": 24.5,
  "humidity": 65.2,
  "soil_moisture": 61,
  "light_intensity": 450,
  "quality": "good"
}
```

## Monitoring

Service logs include:
- MQTT connection status
- Sensor reading counts
- Validation results
- Anomaly detections
- Performance metrics

## Error Handling

- Reconnects to MQTT on failure
- Validates all incoming data
- Logs invalid readings
- Continues operation despite errors
