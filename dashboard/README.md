# Web Dashboard

## Overview
Real-time web dashboard for monitoring the Smart Plant IoT system.

## Structure

- **frontend/**: HTML, CSS, JavaScript for UI
- **backend-api/**: Express.js server for API and MQTT bridge

## Features

1. **Real-time Gauges**: Temperature, Humidity, Moisture, Light
2. **Status Indicators**: Pump, Fan, Grow Light status
3. **Historical Charts**: 24-hour trends
4. **Predictions**: Soil dryness forecast, health score
5. **Alerts**: System alerts and anomalies
6. **Manual Controls**: Command actuators from dashboard

## Technologies

- Frontend: HTML5, CSS3, JavaScript, Chart.js, Gauge.js
- Backend: Express.js, MQTT client, Socket.IO
- Real-time: WebSocket via Socket.IO

## Running

### Start Backend
```bash
cd backend-api
npm install
npm start
# Server runs on http://localhost:3000
```

### Access Dashboard
Open browser to `http://localhost:3000`

## Dashboard Layout

```
┌─────────────────────────────────────────────────────┐
│  Smart Plant IoT Dashboard                    [Menu] │
├─────────────────────────────────────────────────────┤
│  SENSOR READINGS (Real-time Gauges)                 │
│  ┌──────────┬──────────┬──────────┬──────────┐     │
│  │   Temp   │ Humidity │ Moisture │  Light   │     │
│  │ 24.5°C   │  65.2%   │   61%    │  450Lux  │     │
│  └──────────┴──────────┴──────────┴──────────┘     │
├─────────────────────────────────────────────────────┤
│  ACTUATOR STATUS                                    │
│  ┌────────────────────────────────────────────┐    │
│  │ 💧 Pump: OFF  | 🌀 Fan: OFF | 💡 Light: OFF │    │
│  └────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────┤
│  PREDICTIONS & ALERTS                              │
│  ┌────────────────────────────────────────────┐    │
│  │ 🔮 Soil Dryness ETA: 12.5 hours           │    │
│  │ 🌿 Plant Health: 85/100 (Excellent)       │    │
│  │ ⚠️  High Temperature Alert                 │    │
│  └────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────┤
│  24-HOUR TRENDS (Charts)                           │
│  ┌─────────────────────────────────────────────┐  │
│  │ [Temperature Line Chart]                    │  │
│  │ [Moisture Line Chart]                       │  │
│  │ [Humidity Line Chart]                       │  │
│  └─────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────┤
│  MANUAL CONTROLS                                   │
│  ┌─ Pump ─┬─ Fan ─┬─ Grow Light ─┐                │
│  │ [ON] [OFF] │ [ON] [OFF] │ [ON] [OFF]│              │
│  └────────┴───────┴──────────┘                │
└─────────────────────────────────────────────────────┘
```

## API Endpoints

### GET /api/data
Returns current sensor and actuator data
```json
{
  "sensors": {
    "temperature": 24.5,
    "humidity": 65.2,
    "soil_moisture": 61,
    "light_intensity": 450
  },
  "actuators": {
    "pump": "OFF",
    "fan": "OFF",
    "grow_light": "OFF"
  }
}
```

### POST /api/command/:actuator
Send command to actuator
```bash
curl -X POST http://localhost:3000/api/command/pump \
  -H "Content-Type: application/json" \
  -d '{"action": "ON", "duration": 300}'
```

### GET /api/history
Get historical sensor data
```bash
curl http://localhost:3000/api/history?hours=24
```

### GET /api/predictions
Get latest predictions
```bash
curl http://localhost:3000/api/predictions
```

## Real-time Updates

Dashboard uses Socket.IO for real-time updates:
- Sensor data pushed every 2 seconds
- Actuator status updates instantly
- Alerts pushed when triggered

## Browser Compatibility

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
