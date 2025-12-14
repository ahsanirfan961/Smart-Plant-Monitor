# Firebase Service

## Purpose
This service manages all interactions with Firebase Realtime Database:
- Stores sensor readings
- Stores actuator commands
- Manages user data and settings
- Provides real-time data sync

## Functionality

1. **Data Storage**: Saves sensor data to Firebase
2. **Real-time Sync**: Publishes updates for dashboard
3. **Historical Data**: Maintains time-series data
4. **Query Support**: Provides filtered data access
5. **Authentication**: Manages Firebase auth

## Configuration

### Environment Variables
```bash
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY=your-private-key
FIREBASE_CLIENT_EMAIL=your-client-email
FIREBASE_DATABASE_URL=https://your-project.firebaseio.com
LOG_LEVEL=INFO
```

### Firebase Structure

```
/smart-plant-iot/
├── sensors/
│   ├── current/          # Latest readings
│   ├── history/          # Time-series data
│   └── stats/            # Statistics
├── actuators/
│   ├── pump/
│   ├── fan/
│   └── grow_light/
├── users/
│   └── {user_id}/
├── settings/
│   └── thresholds/
└── events/
    └── alerts/
```

## Files

- `main.py`: Entry point
- `firebase_manager.py`: Firebase operations
- `data_sync.py`: Real-time sync handler
- `requirements.txt`: Dependencies

## Running

```bash
pip install -r requirements.txt
python main.py
```

## Data Models

### Sensor Reading
```json
{
  "timestamp": 1702400000000,
  "temperature": 24.5,
  "humidity": 65.2,
  "soil_moisture": 61,
  "light_intensity": 450
}
```

### Actuator Status
```json
{
  "timestamp": 1702400000000,
  "pump": "ON",
  "fan": "OFF",
  "grow_light": "ON"
}
```
