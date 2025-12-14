# Actuator Control Service

## Purpose
This microservice subscribes to MQTT topics for actuator commands and publishes control signals. It manages:
- Water Pump (5V) - GPIO relay
- DC Fan (12V) - GPIO relay
- LED Grow Light - GPIO controlled

## Functionality

1. **Subscribes to command topics** for each actuator
2. **Validates commands** (security checks)
3. **Implements control logic** (interlocks, safeguards)
4. **Publishes status updates** after actuation
5. **Logs all operations** for audit trail
6. **Implements auto-control** based on sensor thresholds

## Configuration

### Environment Variables
```bash
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_USERNAME=          # Optional
MQTT_PASSWORD=          # Optional
AUTO_CONTROL=true       # Enable automatic control based on sensors
LOG_LEVEL=INFO
```

### Control Logic

#### Water Pump
- **Trigger**: Soil Moisture < 30%
- **Duration**: Until moisture > 70% or timeout (5 min)
- **Interlocks**: None

#### DC Fan
- **Trigger**: Temperature > 30°C
- **Duration**: Until temperature < 25°C
- **Interlocks**: None

#### LED Grow Light
- **Trigger**: Light Intensity < 20% or scheduled time
- **Duration**: Until conditions improve or schedule end
- **Interlocks**: Temperature check (won't activate if > 40°C)

## Data Flow

```
MQTT Command Topic
        ↓
Validate Command
        ↓
Check Interlocks
        ↓
Execute Control
        ↓
Update GPIO/Relay
        ↓
Publish Status
```

## Files

- `main.py`: Entry point
- `command_handler.py`: MQTT command processing
- `control_logic.py`: Actuator control implementation
- `safety.py`: Safety checks and interlocks
- `requirements.txt`: Python dependencies

## Running

```bash
pip install -r requirements.txt
python main.py
```

## Command Topics

### Subscribe Topics
- `plant-iot/actuators/pump`
- `plant-iot/actuators/fan`
- `plant-iot/actuators/grow-light`
- `plant-iot/control/all`

### Publish Topics
- `plant-iot/status/pump`
- `plant-iot/status/fan`
- `plant-iot/status/grow-light`
- `plant-iot/status/all`

## Command Format

```json
{
  "action": "ON",
  "duration": 300,
  "timestamp": 1702400000000
}
```

- **action**: "ON" or "OFF"
- **duration**: Optional, seconds (0 = indefinite)
- **timestamp**: Command timestamp

## Status Response

```json
{
  "actuator": "pump",
  "status": "ON",
  "uptime": 300,
  "last_command_timestamp": 1702400000000
}
```

## Safety Features

1. **Command validation**: Syntax checking
2. **Rate limiting**: Max 10 commands/minute per actuator
3. **Interlocks**: Prevent conflicting operations
4. **Watchdog timer**: Auto-shutoff after 30 minutes
5. **Audit logging**: All operations logged with timestamp
6. **Emergency stop**: `control/all` topic stops everything

## Error Handling

- Invalid JSON: Logged, command ignored
- Out-of-range durations: Capped or rejected
- MQTT connection loss: Queues commands, retries on reconnect
- Sensor read failures: Uses last known state

## Monitoring

Service logs include:
- Command received/executed
- Status changes
- Safety check results
- Connection status
- Performance metrics
