"""
Control Logic - Implements actuator control
"""

import logging
import time

logger = logging.getLogger(__name__)


class ControlLogic:
    """Manage actuator control"""
    
    def __init__(self):
        """Initialize control logic"""
        self.actuator_timers = {
            'pump': {'start_time': None, 'duration': 0},
            'fan': {'start_time': None, 'duration': 0},
            'grow_light': {'start_time': None, 'duration': 0}
        }
    
    def activate_pump(self, duration=0):
        """Activate water pump"""
        try:
            # Simulate GPIO activation
            self.actuator_timers['pump'] = {
                'start_time': time.time(),
                'duration': duration
            }
            logger.info(f"Pump activated (duration: {duration}s)")
            # In real implementation, set GPIO 5 HIGH
        except Exception as e:
            logger.error(f"Error activating pump: {e}")
    
    def deactivate_pump(self):
        """Deactivate water pump"""
        try:
            self.actuator_timers['pump'] = {
                'start_time': None,
                'duration': 0
            }
            logger.info("Pump deactivated")
            # In real implementation, set GPIO 5 LOW
        except Exception as e:
            logger.error(f"Error deactivating pump: {e}")
    
    def activate_fan(self, duration=0):
        """Activate cooling fan"""
        try:
            self.actuator_timers['fan'] = {
                'start_time': time.time(),
                'duration': duration
            }
            logger.info(f"Fan activated (duration: {duration}s)")
            # In real implementation, set GPIO 18 HIGH
        except Exception as e:
            logger.error(f"Error activating fan: {e}")
    
    def deactivate_fan(self):
        """Deactivate cooling fan"""
        try:
            self.actuator_timers['fan'] = {
                'start_time': None,
                'duration': 0
            }
            logger.info("Fan deactivated")
            # In real implementation, set GPIO 18 LOW
        except Exception as e:
            logger.error(f"Error deactivating fan: {e}")
    
    def activate_light(self, duration=0):
        """Activate grow light"""
        try:
            self.actuator_timers['grow_light'] = {
                'start_time': time.time(),
                'duration': duration
            }
            logger.info(f"Grow light activated (duration: {duration}s)")
            # In real implementation, set GPIO 19 HIGH
        except Exception as e:
            logger.error(f"Error activating light: {e}")
    
    def deactivate_light(self):
        """Deactivate grow light"""
        try:
            self.actuator_timers['grow_light'] = {
                'start_time': None,
                'duration': 0
            }
            logger.info("Grow light deactivated")
            # In real implementation, set GPIO 19 LOW
        except Exception as e:
            logger.error(f"Error deactivating light: {e}")
    
    def deactivate_all(self):
        """Emergency stop - deactivate all actuators"""
        try:
            self.deactivate_pump()
            self.deactivate_fan()
            self.deactivate_light()
            logger.warning("All actuators deactivated (emergency stop)")
        except Exception as e:
            logger.error(f"Error during emergency stop: {e}")
    
    def check_duration_expired(self):
        """Check if any actuator duration has expired"""
        try:
            current_time = time.time()
            
            for actuator, timer in self.actuator_timers.items():
                if timer['start_time'] and timer['duration'] > 0:
                    elapsed = current_time - timer['start_time']
                    if elapsed > timer['duration']:
                        logger.info(f"{actuator} duration expired, deactivating")
                        if actuator == 'pump':
                            self.deactivate_pump()
                        elif actuator == 'fan':
                            self.deactivate_fan()
                        elif actuator == 'grow_light':
                            self.deactivate_light()
        except Exception as e:
            logger.error(f"Error checking duration expiry: {e}")
    
    def get_status(self, actuator):
        """Get current status of actuator"""
        try:
            timer = self.actuator_timers.get(actuator)
            if timer and timer['start_time']:
                elapsed = time.time() - timer['start_time']
                return {
                    'status': 'ON',
                    'elapsed': elapsed,
                    'remaining': timer['duration'] - elapsed if timer['duration'] > 0 else -1
                }
            else:
                return {'status': 'OFF'}
        except Exception as e:
            logger.error(f"Error getting status for {actuator}: {e}")
            return {'status': 'UNKNOWN'}
