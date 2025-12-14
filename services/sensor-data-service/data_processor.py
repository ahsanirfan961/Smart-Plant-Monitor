"""
Data Processor - Validates and processes sensor data
"""

import logging
import statistics
from collections import deque

logger = logging.getLogger(__name__)


class DataProcessor:
    """Process and validate sensor data"""
    
    # Sensor valid ranges
    RANGES = {
        'temperature': (-50, 80),  # Extended range for sensor variations
        'humidity': (0, 100),
        'soil_moisture': (0, 100),
        'light_intensity': (0, 100)
    }
    
    # Acceptable deviation from expected values (for anomaly detection)
    ANOMALY_THRESHOLDS = {
        'temperature': 15,      # Increased from 5 to 15 - only alert on significant changes
        'humidity': 25,        # Increased from 15 to 25
        'soil_moisture': 30,   # Increased from 20 to 30
        'light_intensity': 40  # Increased from 30 to 40
    }
    
    def __init__(self, window_size=20):  # Increased from 5 to 20 for more stable expected values
        """Initialize processor with rolling window"""
        self.window_size = window_size
        self.data_history = deque(maxlen=window_size)
        self.expected_values = {
            'temperature': 25.0,
            'humidity': 60.0,
            'soil_moisture': 50.0,
            'light_intensity': 50.0
        }
    
    def validate_data(self, data):
        """Validate sensor data is within acceptable ranges"""
        try:
            for key, (min_val, max_val) in self.RANGES.items():
                if key in data and data[key] is not None:
                    value = data[key]
                    if not (min_val <= value <= max_val):
                        logger.warning(f"{key} out of range: {value} "
                                     f"(expected {min_val}-{max_val})")
                        return False
            return True
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False
    
    def detect_anomalies(self, data):
        """Detect anomalies in sensor readings"""
        anomalies = []
        
        try:
            for key, threshold in self.ANOMALY_THRESHOLDS.items():
                if key in data and data[key] is not None:
                    value = data[key]
                    expected = self.expected_values[key]
                    deviation = abs(value - expected)
                    
                    if deviation > threshold:
                        anomalies.append({
                            'sensor': key,
                            'value': value,
                            'expected': expected,
                            'deviation': deviation
                        })
                        logger.warning(f"Anomaly in {key}: {value} "
                                     f"(deviation: {deviation:.1f})")
            
            # Update expected values based on recent data
            self.data_history.append(data)
            if len(self.data_history) == self.window_size:
                self._update_expected_values()
                
        except Exception as e:
            logger.error(f"Anomaly detection error: {e}")
        
        return anomalies
    
    def _update_expected_values(self):
        """Update expected values using rolling average"""
        try:
            for key in self.RANGES.keys():
                values = [d.get(key) for d in self.data_history if d.get(key) is not None]
                if values:
                    self.expected_values[key] = statistics.mean(values)
        except Exception as e:
            logger.error(f"Error updating expected values: {e}")
    
    def assess_quality(self, data):
        """Assess overall data quality"""
        quality_score = 100
        
        try:
            # Deduct points for out-of-range values
            for key, (min_val, max_val) in self.RANGES.items():
                if key in data and data[key] is not None:
                    value = data[key]
                    if not (min_val <= value <= max_val):
                        quality_score -= 10
            
            # Deduct points for anomalies
            if quality_score < 90:
                quality_score = max(0, quality_score - 5)
            
            # Determine quality level
            if quality_score >= 90:
                return "excellent"
            elif quality_score >= 75:
                return "good"
            elif quality_score >= 50:
                return "fair"
            else:
                return "poor"
                
        except Exception as e:
            logger.error(f"Error assessing quality: {e}")
            return "unknown"
    
    def calculate_statistics(self, metric):
        """Calculate statistics for a metric"""
        values = [d.get(metric) for d in self.data_history 
                 if d.get(metric) is not None]
        
        if not values:
            return None
        
        return {
            'min': min(values),
            'max': max(values),
            'avg': statistics.mean(values),
            'stdev': statistics.stdev(values) if len(values) > 1 else 0,
            'count': len(values)
        }
