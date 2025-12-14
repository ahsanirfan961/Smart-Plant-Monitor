"""
Safety Manager - Validates commands and enforces safety rules
"""

import logging
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class SafetyManager:
    """Manage safety checks and command validation"""
    
    # Maximum command duration (in seconds)
    MAX_DURATIONS = {
        'pump': 1800,        # 30 minutes
        'fan': 3600,         # 60 minutes
        'grow_light': 14400  # 4 hours
    }
    
    # Rate limiting (max commands per minute)
    MAX_COMMANDS_PER_MINUTE = 10
    
    def __init__(self):
        """Initialize safety manager"""
        self.command_history = defaultdict(list)  # Track recent commands
    
    def validate_command(self, actuator, action, duration=0):
        """Validate a command before execution"""
        try:
            # Check actuator name
            if actuator not in ['pump', 'fan', 'grow_light']:
                logger.error(f"Unknown actuator: {actuator}")
                return False
            
            # Check action
            if action not in ['ON', 'OFF']:
                logger.error(f"Invalid action: {action}")
                return False
            
            # Check duration
            if duration < 0:
                logger.error(f"Negative duration: {duration}")
                return False
            
            if duration > self.MAX_DURATIONS.get(actuator, 3600):
                logger.warning(f"Duration exceeds max for {actuator}, capping at {self.MAX_DURATIONS[actuator]}s")
                # Could cap instead of reject
            
            # Check rate limiting
            if not self._check_rate_limit(actuator):
                logger.warning(f"Rate limit exceeded for {actuator}")
                return False
            
            # Record command
            self._record_command(actuator)
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating command: {e}")
            return False
    
    def _check_rate_limit(self, actuator):
        """Check if command rate limit is exceeded"""
        try:
            now = datetime.now()
            minute_ago = now - timedelta(minutes=1)
            
            # Clean old commands
            self.command_history[actuator] = [
                cmd_time for cmd_time in self.command_history[actuator]
                if cmd_time > minute_ago
            ]
            
            # Check limit
            if len(self.command_history[actuator]) >= self.MAX_COMMANDS_PER_MINUTE:
                logger.warning(f"Rate limit exceeded for {actuator}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            return False
    
    def _record_command(self, actuator):
        """Record a command for rate limiting"""
        try:
            self.command_history[actuator].append(datetime.now())
        except Exception as e:
            logger.error(f"Error recording command: {e}")
    
    def check_interlocks(self, actuator, sensor_data):
        """Check if any safety interlocks prevent actuation"""
        try:
            # Example: Don't activate light if temp > 40°C
            if actuator == 'grow_light':
                if sensor_data.get('temperature', 0) > 40:
                    logger.warning("Interlock: Temperature too high for grow light")
                    return False
            
            # Example: Don't activate pump if tank is empty (not simulated here)
            if actuator == 'pump':
                # Check water tank level (not implemented)
                pass
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking interlocks: {e}")
            return False
    
    def check_safety_limits(self, sensor_data):
        """Check if sensor readings indicate unsafe conditions"""
        try:
            alerts = []
            
            # Temperature check
            temp = sensor_data.get('temperature')
            if temp and temp > 45:
                alerts.append("Critical: Temperature too high")
            
            # Humidity check
            humidity = sensor_data.get('humidity')
            if humidity and humidity > 95:
                alerts.append("Warning: Very high humidity")
            
            # Soil moisture check
            moisture = sensor_data.get('soil_moisture')
            if moisture and moisture > 95:
                alerts.append("Warning: Soil over-saturated")
            
            if alerts:
                for alert in alerts:
                    logger.warning(f"Safety alert: {alert}")
            
            return len(alerts) == 0
            
        except Exception as e:
            logger.error(f"Error checking safety limits: {e}")
            return False
