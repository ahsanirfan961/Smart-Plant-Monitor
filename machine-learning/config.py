"""
Configuration and constants for ML module
"""

# Actuator Control Thresholds
TEMPERATURE_HIGH_THRESHOLD = 30.0  # °C - Turn on fan
TEMPERATURE_CRITICAL_THRESHOLD = 35.0  # °C - Emergency cooling

MOISTURE_LOW_THRESHOLD = 35.0  # % - Turn on pump
MOISTURE_CRITICAL_THRESHOLD = 25.0  # % - Emergency watering

LIGHT_LOW_THRESHOLD = 25.0  # % - Turn on grow light
LIGHT_OPTIMAL_THRESHOLD = 40.0  # % - Optimal light level

HUMIDITY_LOW_THRESHOLD = 40.0  # % - May need humidifier
HUMIDITY_HIGH_THRESHOLD = 80.0  # % - May need dehumidifier/fan

# Ideal Ranges for Plant Health
IDEAL_TEMPERATURE_RANGE = (20, 28)  # °C
IDEAL_HUMIDITY_RANGE = (50, 75)  # %
IDEAL_MOISTURE_RANGE = (40, 70)  # %
IDEAL_LIGHT_RANGE = (30, 80)  # %

# Model Parameters
ACTUATOR_MODEL_PATH = "models/actuator_classifier.pkl"
TREND_MODEL_PATH = "models/trend_model.pkl"

# Training Data Size
TRAINING_SAMPLES = 1000
TEST_SPLIT_RATIO = 0.2

# Prediction Parameters
PREDICTION_CONFIDENCE_THRESHOLD = 0.7
MAX_FORECAST_HOURS = 24
FORECAST_INTERVAL_MINUTES = 30

# Feature Names
FEATURE_NAMES = [
    'temperature',
    'humidity',
    'soil_moisture',
    'light_intensity'
]

TARGET_ACTUATORS = [
    'fan',
    'pump',
    'light'
]

# Logging
LOG_LEVEL = 'INFO'
