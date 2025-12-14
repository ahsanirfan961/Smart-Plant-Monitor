# Development Guide

## 🛠️ Setting Up Development Environment

### Prerequisites
- VS Code
- Python 3.9+
- Node.js 16+
- Git
- Docker (optional, for containers)

### Clone or Initialize Repository
```bash
cd smart-plant-iot-system
git init
git add .
git commit -m "Initial Smart Plant IoT System"
```

---

## 🔄 Development Workflow

### 1. Wokwi Simulation Development

**File**: `wokwi-simulation/code.ino`

Modify sensor reading intervals, GPIO pins, or WiFi settings:

```cpp
// Change sensor read interval
const unsigned long SENSOR_INTERVAL = 5000;  // 5 seconds

// Add new sensor
#define NEW_SENSOR_PIN 32
int newSensorValue = analogRead(NEW_SENSOR_PIN);
```

**Testing**:
- Open diagram.json in Wokwi
- Edit code.ino
- Click Run/Restart
- Monitor Serial output

---

### 2. Service Development

#### Sensor Data Service
**File**: `services/sensor-data-service/main.py`

Add new data validation:
```python
# In data_processor.py, add to RANGES
'new_sensor': (min_val, max_val)

# In on_message() callback
elif topic == "plant-iot/sensors/new-sensor":
    sensor_data['new_sensor'] = payload.get('value')
```

#### Actuator Control Service
**File**: `services/actuator-control/main.py`

Add new actuator:
```python
# In handle functions
def handle_new_actuator_command(payload):
    action = payload.get('action').upper()
    if action == 'ON':
        control_logic.activate_new_actuator()
    elif action == 'OFF':
        control_logic.deactivate_new_actuator()
    publish_status('new_actuator')
```

#### Analytics Service
**File**: `services/data-analytics/predictor.py`

Improve ML models:
```python
# Add new predictor class
class NewPredictor:
    def predict(self, data):
        # Implement prediction logic
        pass

# In main.py
predictor = NewPredictor()
predictions = predictor.predict(sensor_data)
```

---

### 3. Dashboard Development

#### Frontend
**File**: `dashboard/frontend/index.html`

Add new UI component:
```html
<!-- New gauge section -->
<div class="gauge-card">
    <h3>New Metric</h3>
    <div class="gauge">
        <canvas id="newGauge"></canvas>
    </div>
    <div class="value" id="newValue">--</div>
</div>
```

**File**: `dashboard/frontend/js/dashboard.js`

Add gauge initialization:
```javascript
// In initializeGauges()
gauges.new = createLinearGauge('newGauge', {
    min: 0,
    max: 100,
    value: 50,
    color: '#your-color'
});

// In updateSensorData()
gauges.new.update(sensorData.new_metric);
```

#### Backend API
**File**: `dashboard/backend-api/server.js`

Add new API endpoint:
```javascript
app.get('/api/new-endpoint', (req, res) => {
    res.json({
        data: systemState.new_data
    });
});
```

---

## 🧪 Testing Strategies

### Unit Testing

**Python Services**:
```bash
pip install pytest pytest-cov

# Test sensor data service
pytest services/sensor-data-service/test_processor.py -v
```

**Node.js Dashboard**:
```bash
npm test
```

### Integration Testing

Test full data flow:
```bash
# Terminal 1: Start MQTT
docker-compose up -d mosquitto

# Terminal 2: Subscribe to all topics
mosquitto_sub -h localhost -t "plant-iot/#" -v

# Terminal 3: Publish test data
mosquitto_pub -h localhost -t "plant-iot/sensors/temperature" \
  -m '{"temperature": 30, "unit": "celsius", "timestamp": 1702400000000}'

# Terminal 4: Check dashboard updates
open http://localhost:3000
```

### Load Testing

Test with high message frequency:
```python
# Create test script
import paho.mqtt.client as mqtt
import json
import time

client = mqtt.Client()
client.connect("localhost", 1883)

for i in range(100):
    payload = json.dumps({"temperature": 20 + i % 10})
    client.publish("plant-iot/sensors/temperature", payload)
    time.sleep(0.1)
```

---

## 📝 Code Style Guide

### Python
- Follow PEP 8
- Use type hints where possible
- Comment complex logic
- Use logging instead of print()

```python
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

def process_data(data: Dict) -> Optional[bool]:
    """
    Process sensor data with validation.
    
    Args:
        data: Dictionary containing sensor readings
        
    Returns:
        True if valid, False otherwise
        
    Raises:
        ValueError: If critical data is missing
    """
    logger.info(f"Processing data: {data}")
    return True
```

### JavaScript
- Use const/let, avoid var
- Use arrow functions
- Add JSDoc comments
- Use meaningful variable names

```javascript
/**
 * Update sensor gauge with new value
 * @param {Object} gauge - Gauge object
 * @param {number} value - New value
 */
const updateGauge = (gauge, value) => {
    gauge.value = value;
    gauge.draw();
};
```

---

## 🐛 Debugging

### Debug Python Services

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add breakpoints
import pdb
pdb.set_trace()

# Use VS Code debugger
# Add .vscode/launch.json configuration
```

### Debug MQTT Communication

```bash
# Use MQTT.fx or mqttfx GUI tool
# Or verbose mosquitto_sub
mosquitto_sub -h localhost -t "plant-iot/#" -v -d
```

### Debug Dashboard

```javascript
// Open browser console (F12)
console.log('Debug message:', data);

// Use debugger
debugger;  // Execution pauses here

// Check network tab for WebSocket messages
```

---

## 📦 Dependency Management

### Python
```bash
# Update requirements.txt
pip install --upgrade package_name
pip freeze > requirements.txt

# Install from requirements
pip install -r requirements.txt
```

### Node.js
```bash
# Update packages
npm update

# Install new package
npm install package-name --save

# List dependencies
npm list --depth=0
```

---

## 🔐 Security Best Practices

### Configuration
- Never commit secrets to git
- Use environment variables
- Create `.env` file with gitignore

```bash
# .env
MQTT_USERNAME=user
MQTT_PASSWORD=secret
FIREBASE_KEY=...
```

```python
# Access via os.getenv()
username = os.getenv('MQTT_USERNAME')
```

### MQTT
- Enable authentication in production
- Use TLS/SSL encryption
- Implement ACL (Access Control Lists)

### API
- Validate all inputs
- Use HTTPS in production
- Implement rate limiting

---

## 📊 Performance Optimization

### Reduce MQTT Traffic
```python
# Aggregate data before publishing
if sensor_change > THRESHOLD:
    client.publish(topic, payload)
```

### Optimize Database Queries
```javascript
// Use indexes for faster queries
db.collection('sensors').createIndex({'timestamp': -1})
```

### Optimize Dashboard
- Use lazy loading for charts
- Debounce rapid updates
- Cache historical data

```javascript
// Debounce updates
const debounce = (func, delay) => {
    let timeoutId;
    return (...args) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func(...args), delay);
    };
};
```

---

## 🚀 Deployment Checklist

- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Docker images built
- [ ] Documentation updated
- [ ] Logs properly configured
- [ ] Error handling implemented
- [ ] Performance tested
- [ ] Security review completed

---

## 📚 Additional Resources

- [MQTT Documentation](https://mqtt.org/)
- [Express.js Guide](https://expressjs.com/)
- [Python Logging](https://docs.python.org/3/library/logging.html)
- [Chart.js Documentation](https://www.chartjs.org/)
- [Socket.IO Guide](https://socket.io/docs/)

---

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and test
3. Commit: `git commit -am 'Add feature'`
4. Push: `git push origin feature/your-feature`
5. Create Pull Request

---

## 📞 Support

For development questions:
1. Check existing code comments
2. Review documentation
3. Check issue tracker
4. Ask team members
