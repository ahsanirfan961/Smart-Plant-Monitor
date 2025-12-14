# Quick Start Guide

## 🚀 Prerequisites

- Docker & Docker Compose
- VS Code with Wokwi extension
- Git
- Python 3.9+ (for local development)
- Node.js 16+ (for local dashboard development)

---

## ⚡ Quick Start (Fastest Way)

### 1. Start MQTT Broker
```bash
cd smart-plant-iot-system
docker-compose up -d mosquitto
```

### 2. Start Wokwi Simulation
- Open `wokwi-simulation` folder in VS Code
- Open `diagram.json`
- Click the green play button in Wokwi extension

### 3. Start Services (Local Python)

In separate terminals:

```bash
# Terminal 1: Sensor Data Service
cd services/sensor-data-service
pip install -r requirements.txt
python main.py

# Terminal 2: Actuator Control Service
cd services/actuator-control
pip install -r requirements.txt
python main.py

# Terminal 3: Firebase Service
cd services/firebase-service
pip install -r requirements.txt
python main.py

# Terminal 4: Data Analytics Service
cd services/data-analytics
pip install -r requirements.txt
python main.py

# Terminal 5: Dashboard API
cd dashboard/backend-api
npm install
npm start
```

### 4. Access Dashboard
Open browser: **http://localhost:3000**

---

## 🐳 Full Docker Deployment

Start all services at once:

```bash
docker-compose up -d
```

Check logs:
```bash
docker-compose logs -f
```

Stop all services:
```bash
docker-compose down
```

---

## 📊 System Architecture Diagram

```
┌─────────────────────────────────────┐
│    Wokwi ESP32 Simulation           │
│ (Sensors: DHT11, FC-28, LDR)       │
└────────────────┬────────────────────┘
                 │ WiFi (Simulated)
                 │
        ┌────────▼────────┐
        │  MQTT Broker    │
        │  (Mosquitto)    │
        └────────┬────────┘
    ┌───────────┼───────────┬──────────┬──────────┐
    │           │           │          │          │
    ▼           ▼           ▼          ▼          ▼
  Sensor    Actuator   Firebase    Analytics   Dashboard
  Service   Service    Service     Service     (Node.js)
                                                  │
                                                  ▼
                                            Web Browser
                                          (Real-time UI)
```

---

## 🔧 Configuration

### MQTT Topics
```
plant-iot/
├── sensors/
│   ├── temperature
│   ├── humidity
│   ├── soil-moisture
│   └── light
├── actuators/
│   ├── pump
│   ├── fan
│   └── grow-light
└── predictions/
    ├── soil-dryness
    └── health-score
```

### Environment Variables

Create `.env` file in root:
```bash
MQTT_BROKER=localhost
MQTT_PORT=1883
LOG_LEVEL=INFO
AUTO_CONTROL=true
```

---

## 📱 Dashboard Features

### Real-time Monitoring
- Temperature, Humidity, Soil Moisture, Light Intensity gauges
- Actuator status (Pump, Fan, Light)
- 24-hour trend charts

### Predictions
- Soil dryness ETA (hours until watering needed)
- Plant health score (0-100)
- Automated recommendations

### Controls
- Manual ON/OFF buttons for each actuator
- Real-time status updates
- Alert notifications

---

## 🧪 Testing

### 1. Test MQTT Connection
```bash
# Subscribe to all topics
mosquitto_sub -h localhost -t "plant-iot/#" -v

# In another terminal, publish test data
mosquitto_pub -h localhost -t "plant-iot/sensors/temperature" \
  -m '{"temperature": 25.5, "unit": "celsius", "timestamp": 1702400000000}'
```

### 2. Test Dashboard API
```bash
# Get current data
curl http://localhost:3000/api/data

# Send command to pump
curl -X POST http://localhost:3000/api/command/pump \
  -H "Content-Type: application/json" \
  -d '{"action": "ON", "duration": 300}'

# Get predictions
curl http://localhost:3000/api/predictions
```

### 3. Test in Dashboard
1. Open http://localhost:3000
2. Check real-time gauge updates
3. Click "Turn ON" for any actuator
4. Verify status changes

---

## 📈 Data Flow Example

1. **Wokwi ESP32** reads sensors every 2 seconds
2. **Publishes** to MQTT: `plant-iot/sensors/temperature`, etc.
3. **Sensor Service** validates and aggregates data
4. **Firebase Service** stores in database
5. **Analytics Service** generates predictions
6. **Dashboard API** broadcasts via Socket.IO
7. **Web Dashboard** updates gauges in real-time

---

## 🔍 Troubleshooting

### MQTT not connecting
```bash
# Check if mosquitto is running
docker ps | grep mosquitto

# Check MQTT logs
docker logs smart-plant-mqtt

# Test MQTT manually
telnet localhost 1883
```

### Services not communicating
```bash
# Check Docker network
docker network ls
docker network inspect smart-plant-network

# View service logs
docker-compose logs sensor-service
docker-compose logs actuator-service
```

### Dashboard not updating
```bash
# Check API server
curl http://localhost:3000/api/status

# Check browser console (F12) for errors
# Check network tab for WebSocket connections
```

### Wokwi simulation issues
- Reload the diagram
- Check pin connections in diagram.json
- Verify code.ino syntax
- Check VS Code terminal for errors

---

## 📚 Documentation Files

- **[Main README](./README.md)** - Project overview
- **[Wokwi Guide](./wokwi-simulation/README.md)** - Simulation details
- **[MQTT Config](./mqtt-broker/README.md)** - Broker setup
- **[Services Docs](./services/)** - Individual service documentation
- **[Dashboard Guide](./dashboard/README.md)** - UI documentation

---

## 🚀 Next Steps

1. Modify sensor values in Wokwi to test system behavior
2. Adjust control thresholds in actuator-control/main.py
3. Train ML models with historical data in data-analytics/
4. Customize dashboard styling in frontend/css/style.css
5. Add more sensors or actuators to the system

---

## 📞 Support

For issues or questions:
1. Check logs: `docker-compose logs`
2. Test MQTT: Use mosquitto_sub/mosquitto_pub
3. Test API: Use curl or Postman
4. Check browser console: F12 Developer Tools
5. Review service code and comments

---

## 📄 License

MIT License

---

## 👥 Team

Smart Plant IoT Development Team - 2025
