# IoT-Based Smart Plant Environment Control System

## 🌱 Project Overview
A fully simulated IoT ecosystem for autonomous plant environment management using MQTT protocol, Firebase cloud storage, and machine learning predictions.

### **System Components**
- **Hardware (Simulated)**: ESP32 with sensors (FC-28, DHT11, LDR) and actuators (Water Pump, DC Fan, LED Grow Light)
- **Communication**: MQTT Protocol (Pub/Sub Model)
- **Cloud**: Firebase Realtime Database
- **Analytics**: Python ML Models (Linear Regression, Random Forest)
- **Dashboard**: Real-time web interface with Chart.js

---

## 📁 Project Structure

```
smart-plant-iot-system/
├── wokwi-simulation/          # ESP32 Wokwi simulation
├── mqtt-broker/                # Mosquitto MQTT broker config
├── services/
│   ├── sensor-data-service/   # Publishes sensor data via MQTT
│   ├── actuator-control/      # Subscribes and controls actuators
│   ├── firebase-service/      # Firebase integration
│   └── data-analytics/        # ML models & predictions
├── dashboard/
│   ├── frontend/              # HTML/CSS/JS dashboard
│   └── backend-api/           # Express.js API server
├── database/                   # Firebase schemas
├── docker-compose.yml         # Container orchestration
└── requirements.txt           # Python dependencies
```

---

## 🔄 System Data Flow

```
┌─────────────────────────────────────────┐
│   Wokwi ESP32 Simulation                │
│  (Sensors: DHT11, FC-28, LDR)          │
└──────────────────┬──────────────────────┘
                   │ MQTT Publish (WiFi Simulated)
                   │
        ┌──────────▼──────────┐
        │  MQTT Broker        │
        │  (Mosquitto)        │
        └──────┬──────────────┘
    ┌───────┬──┴──┬──────────┬──────────┐
    │       │     │          │          │
    ▼       ▼     ▼          ▼          ▼
  Sensor  Data  Firebase  Actuator  Predictive
  Storage Agg.  Sync      Control   Model
    │       │     │          │          │
    └───────┴─────┴──────────┴──────────┘
                   │
        ┌──────────▼──────────┐
        │ Web Dashboard       │
        │ (Real-time Charts)  │
        └─────────────────────┘
```

---

## 📊 MQTT Topics Structure

```
plant-iot/
├── sensors/
│   ├── soil-moisture    # 0-100 %
│   ├── temperature      # °C
│   ├── humidity         # %
│   └── light            # Lux or ADC value
├── actuators/
│   ├── pump             # ON/OFF
│   ├── fan              # ON/OFF
│   └── grow-light       # ON/OFF
├── analytics/
│   ├── predictions/soil-dryness  # ETA hours
│   └── health-status             # Overall status
└── events/
    ├── alerts           # System alerts
    └── diagnostics      # Diagnostic data
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 16+
- Docker & Docker Compose
- VS Code with Wokwi, MQTT Client extensions

### Quick Start
```bash
# Start MQTT broker
docker-compose up -d mosquitto

# Start services
python services/sensor-data-service/main.py
python services/actuator-control/main.py
python services/firebase-service/main.py
python services/data-analytics/main.py

# Start dashboard
cd dashboard/backend-api
npm install && npm start
```

---

## 📈 Key Features

1. **Multi-Parameter Sensing**: Real-time acquisition of environmental data
2. **Intelligent Actuation**: Automated response to environmental stress
3. **Predictive Analytics**: ML model forecasting soil dryness
4. **Real-time Dashboard**: Web UI with live gauges and charts
5. **Cloud Integration**: Firebase for persistent storage
6. **Data Analytics**: Descriptive and diagnostic analytics

---

## 🔧 Technology Stack

| Component | Technology |
|-----------|-----------|
| Simulation | Wokwi for ESP32 |
| IoT Communication | MQTT (Mosquitto) |
| Backend Services | Python 3.9 |
| Dashboard Frontend | HTML/CSS/JS + Chart.js |
| Dashboard API | Express.js (Node.js) |
| Cloud DB | Firebase Realtime |
| ML/Analytics | scikit-learn, pandas |
| Containerization | Docker & Docker Compose |

---

## 📝 Development Phases

- [ ] Phase 1: Wokwi simulation & MQTT broker setup
- [ ] Phase 2: Sensor data publisher service
- [ ] Phase 3: Actuator control subscriber service
- [ ] Phase 4: Firebase integration
- [ ] Phase 5: Web dashboard development
- [ ] Phase 6: ML model implementation
- [ ] Phase 7: Docker containerization
- [ ] Phase 8: System testing & validation

---

## 📚 Documentation
- [Wokwi Simulation Guide](./wokwi-simulation/README.md)
- [MQTT Configuration](./mqtt-broker/README.md)
- [Service Documentation](./services/README.md)
- [Dashboard Guide](./dashboard/README.md)

---

## 👥 Author
IoT Development Team - 2025

## 📄 License
MIT License
