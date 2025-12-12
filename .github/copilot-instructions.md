# GitHub Copilot Instructions: Smart Green IoT Farm Simulation

## Project Overview
You are working on **Smart Green**, an IoT-based environmental monitoring and automation system that simulates a smart farm using a "Digital Twin" approach. This is a software-only simulation designed to demonstrate IoT concepts without physical hardware.

### Core Technologies
- **Backend**: Python 3.9+ (Physics Engine, ML Models, MQTT Publisher)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript (Web Dashboard)
- **Communication**: MQTT (Telemetry), Firebase Realtime Database (Persistence)
- **ML**: scikit-learn (Linear Regression for predictive analytics)

## Task Management Workflow (MANDATORY)

### Use Shrimp Task Manager MCP
**This project MUST use the Shrimp Task Manager MCP for all development tasks.**

#### Task Planning Phase
1. When given a new feature or requirement, FIRST call the Shrimp Task Manager's planning tools:
   - Use `plan_task` to understand requirements
   - Use `analyze_task` to assess technical feasibility
   - Use `split_tasks` to break down complex work into manageable subtasks

#### Task Execution Flow (STRICT)
For EVERY task, follow this mandatory sequence:

1. **START**: Call `execute_task` tool with the task ID
   - This provides instructional guidance for the task
   - You MUST follow the guidance returned by the tool
   - The tool guides you; it does NOT execute for you

2. **IMPLEMENT**: Complete the actual programming work
   - Write/modify code according to the task requirements
   - Follow all coding standards (see below)
   - Test your implementation

3. **VERIFY**: Call `verify_task` tool with the task ID
   - This checks if the task meets completion criteria
   - Provides feedback and scores
   - Only proceed if verification passes

4. **COMPLETE**: Mark the task as completed in Shrimp
   - Update task status appropriately
   - Document any important notes

**NEVER skip the execute_task → implement → verify_task flow.**

## Coding Standards & Best Practices

### Python Backend Standards

#### File Organization
```
backend/
├── main.py                 # Entry point
├── physics_engine.py       # World simulation logic
├── ml_predictor.py         # Linear regression model
├── mqtt_client.py          # MQTT publisher
├── firebase_client.py      # Firebase integration
├── config.py               # Configuration constants
└── utils.py                # Shared utilities
```

#### Code Quality Requirements
1. **Type Hints**: ALL functions MUST have type annotations
   ```python
   def calculate_temperature(hour: int, minute: int) -> float:
       """Calculate temperature using sinusoidal curve."""
       pass
   ```

2. **Docstrings**: Use Google-style docstrings for all functions/classes
   ```python
   def predict_time_to_dry(data_buffer: List[Tuple[float, float]]) -> str:
       """Predict when soil moisture will reach critical threshold.
       
       Args:
           data_buffer: List of (time_index, moisture_level) tuples
           
       Returns:
           Formatted string like "2h 15m" indicating time to critical
           
       Raises:
           ValueError: If data_buffer has fewer than 2 points
       """
   ```

3. **Error Handling**: ALWAYS handle network disconnects gracefully
   - MQTT disconnections must not crash the simulation
   - Firebase read/write errors should be logged and retried
   - Use try-except blocks with specific exception types

4. **Constants**: Define ALL magic numbers in `config.py`
   ```python
   # Time scaling
   REAL_SECOND_TO_VIRTUAL_MINUTES = 6
   VIRTUAL_DAY_DURATION_SECONDS = 240
   
   # Physics constants
   BASE_TEMPERATURE_C = 20.0
   TEMPERATURE_AMPLITUDE_C = 10.0
   BASE_EVAPORATION_RATE = 0.5
   HEAT_STRESS_MULTIPLIER = 2.0
   HEAT_STRESS_THRESHOLD_C = 35.0
   
   # Thresholds
   MOISTURE_CRITICAL_THRESHOLD = 30.0
   MOISTURE_HEALTHY_THRESHOLD = 50.0
   ```

5. **Logging**: Use Python's logging module, not print statements
   ```python
   import logging
   logger = logging.getLogger(__name__)
   logger.info("Simulation started at virtual time 06:00")
   logger.warning(f"High temperature detected: {temp}°C")
   ```

### Frontend Standards

#### File Organization
```
frontend/
├── index.html              # Main dashboard
├── css/
│   ├── styles.css          # Main styles
│   ├── animations.css      # Sky/sun animations
│   └── components.css      # UI component styles
├── js/
│   ├── main.js             # App initialization
│   ├── mqtt_handler.js     # MQTT WebSocket client
│   ├── firebase_handler.js # Firebase integration
│   ├── ui_controller.js    # DOM manipulation
│   └── animations.js       # Sky gradient & sun movement
└── assets/
    ├── plant_healthy.png
    ├── plant_sagging.png
    └── plant_dead.png
```

#### JavaScript Standards
1. **Use ES6+ Features**: Arrow functions, const/let, template literals
2. **Modular Code**: Separate concerns into different files
3. **No jQuery**: Use vanilla JavaScript DOM methods
4. **Async/Await**: For Firebase and asynchronous operations
5. **Error Handling**: Always catch Promise rejections

### Data Schema Compliance

#### MQTT Payload (MUST MATCH EXACTLY)
```json
{
  "moisture": 74.5,
  "temperature": 26.2,
  "light_intensity": 800,
  "hour": 14,
  "minute": 30,
  "time_str": "14:30",
  "day_progress": 60.4,
  "is_day": true,
  "prediction": "2h 15m",
  "sprinkler_on": false
}
```

#### Firebase Structure (MUST MATCH EXACTLY)
```
plant_monitor/
├── actuators/
│   ├── sprinkler_state: boolean
│   ├── grow_light_state: boolean
│   └── fan_state: boolean
└── history_log/
    └── {push_id}/
        ├── time: string
        ├── moisture: float
        └── temperature: float
```

## Critical Physics Rules

### Time System
- **ALWAYS** use the ratio: 1 real second = 6 virtual minutes
- Virtual day cycles MUST complete in exactly 240 real seconds (4 minutes)
- Start time MUST be 06:00 AM virtual time

### Temperature Model
- Use sinusoidal curve: `T = 20 + 10 * sin(time_offset)`
- Peak temperature at 14:00 (2:00 PM)
- Add random noise: ±1.0°C
- Range: 10°C to 30°C (with noise can reach ~32°C)

### Moisture Logic (CRITICAL)
1. **Base evaporation**: 0.5% per tick (every real second)
2. **Heat stress**: If temperature > 35°C, evaporation rate DOUBLES (2x)
3. **Watering**: When sprinkler_state is true, ADD 3.0% per tick
4. **Clamp**: Always keep moisture between 0 and 100

### Day/Night Cycle
- **Day**: 06:00 to 18:00 (is_day = true)
- **Night**: 18:00 to 06:00 (is_day = false)
- Light intensity: High during day, low at night

### ML Prediction
- Train Linear Regression every virtual hour (every 10 real seconds)
- Use rolling buffer of (time_index, moisture_level) pairs
- Predict when moisture will reach 30% (critical threshold)
- Display as "Time to Empty: Xh Ym"

## Repository Structure Standards

### Required Files
```
Smart-Plant-Monitor/
├── .github/
│   └── copilot-instructions.md (this file)
├── backend/
│   ├── main.py
│   ├── physics_engine.py
│   ├── ml_predictor.py
│   ├── mqtt_client.py
│   ├── firebase_client.py
│   ├── config.py
│   ├── utils.py
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── css/
│   ├── js/
│   └── assets/
├── docs/
│   ├── srs.md
│   ├── architecture.md
│   ├── data-schemas.md
│   └── simulation-logic.md
├── data/
│   └── tasks.json (Shrimp Task Manager)
├── tests/
│   ├── test_physics.py
│   ├── test_ml.py
│   └── test_integration.py
├── .gitignore
├── README.md
└── LICENSE
```

### Git Commit Standards
- Use conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`
- Example: `feat(physics): implement heat stress multiplier for evaporation`
- Keep commits atomic and focused on single concerns

### Documentation Requirements
1. Update README.md when adding new features
2. Keep docs/ folder synchronized with code changes
3. Add inline comments for complex physics calculations
4. Document all API endpoints and data schemas

## Testing Requirements

### Unit Tests (MANDATORY)
1. **Physics Engine**: Test all environmental calculations
   - Temperature curve at different times
   - Moisture evaporation with/without heat stress
   - Sprinkler activation effects

2. **ML Model**: Test prediction accuracy
   - Edge cases (insufficient data)
   - Normal operation
   - Boundary conditions

3. **Integration**: Test MQTT and Firebase connectivity
   - Connection failures
   - Data format validation
   - Reconnection logic

### Test File Naming
- Format: `test_<module_name>.py`
- Use pytest framework
- Aim for >80% code coverage

## Common Pitfalls to Avoid

1. **Time Confusion**: Never mix real time with virtual time
2. **Magic Numbers**: Always use constants from config.py
3. **Hardcoded Values**: Make everything configurable
4. **Missing Error Handling**: MQTT/Firebase can fail; handle it
5. **Data Schema Mismatches**: Frontend expects exact MQTT payload format
6. **Sync Issues**: Frontend reads from Firebase; Python writes to it
7. **Memory Leaks**: Clear old ML buffer data after virtual day resets

## Performance Requirements

- **MQTT Update Rate**: Exactly 1 Hz (every 1 real second)
- **Firebase Writes**: Once per virtual hour (every 10 real seconds)
- **UI Latency**: Visual updates must appear within 2 seconds
- **Smooth Animations**: CSS transitions for sky gradient changes

## When Creating New Features

1. **ALWAYS start with Shrimp Task Manager**: Plan and analyze first
2. **Follow the execute → verify flow**: No exceptions
3. **Update documentation**: Keep docs/ in sync
4. **Write tests**: Before marking task complete
5. **Verify data schemas**: Match exactly what's documented
6. **Check physics rules**: Ensure simulation accuracy
7. **Test with both protocols**: MQTT and Firebase integration

## Remember

- This is an EDUCATIONAL IoT simulation project
- Code clarity is MORE important than performance optimization
- The system must demonstrate IoT concepts clearly
- All time-based logic is accelerated (Fast Clock)
- The "Digital Twin" dashboard is the primary deliverable

## Questions to Ask Before Implementation

1. Does this change affect the time scaling system?
2. Are all data schemas preserved?
3. Is error handling included for network operations?
4. Are physics rules correctly implemented?
5. Is the change compatible with both MQTT and Firebase?
6. Has the task been properly planned in Shrimp Task Manager?
7. Will this require frontend updates for visual consistency?

---

**Priority**: Follow the Shrimp Task Manager workflow strictly. Never implement without planning, and never mark complete without verification.
