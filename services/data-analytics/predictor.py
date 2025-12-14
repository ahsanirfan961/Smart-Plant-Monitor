"""
Predictor - ML models for predictions
"""

import logging
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)


class SoilDrynessPredictor:
    """Predict soil dryness using Linear Regression"""
    
    def __init__(self):
        """Initialize predictor"""
        # Coefficients learned from training data
        self.coefficients = {
            'moisture': -0.05,      # Dryness increases as moisture decreases
            'temperature': 0.02,    # Higher temp causes faster drying
            'humidity': -0.01,      # Higher humidity slows drying
            'intercept': 8.0        # Base drying rate
        }
    
    def predict(self, moisture, temperature, humidity, critical_moisture=30):
        """
        Predict hours until soil reaches critical moisture level
        
        Args:
            moisture: Current soil moisture (0-100%)
            temperature: Current temperature (°C)
            humidity: Current humidity (%)
            critical_moisture: Target moisture level (default 30%)
        
        Returns:
            (eta_hours, confidence): Tuple of predicted hours and confidence (0-1)
        """
        try:
            if moisture <= critical_moisture:
                return 0, 1.0
            
            # Simple linear model: drying_rate = coef_moisture * moisture + coef_temp * temp + ...
            drying_rate = (
                self.coefficients['intercept'] +
                self.coefficients['moisture'] * (100 - moisture) / 100 +
                self.coefficients['temperature'] * temperature / 50 +
                self.coefficients['humidity'] * (100 - humidity) / 100
            )
            
            # Calculate hours to critical moisture
            moisture_deficit = moisture - critical_moisture
            eta_hours = moisture_deficit / max(drying_rate, 0.1)  # Prevent division by zero
            
            # Confidence based on data variability
            confidence = min(0.95, 0.7 + (humidity / 100) * 0.2)  # Higher humidity = more predictable
            
            return max(0, eta_hours), confidence
            
        except Exception as e:
            logger.error(f"Error in soil dryness prediction: {e}")
            return 12.0, 0.5  # Default safe estimate


class HealthScorePredictor:
    """Predict plant health score using simple scoring system"""
    
    def __init__(self):
        """Initialize predictor"""
        # Ideal ranges for each metric
        self.ideal_ranges = {
            'temperature': (20, 28),    # °C
            'humidity': (50, 75),       # %
            'soil_moisture': (40, 70),  # %
            'light_intensity': (30, 80) # %
        }
        
        # Weights for each metric
        self.weights = {
            'temperature': 0.25,
            'humidity': 0.20,
            'soil_moisture': 0.35,
            'light_intensity': 0.20
        }
    
    def predict(self, data):
        """
        Predict plant health score
        
        Args:
            data: Dictionary with sensor readings
        
        Returns:
            (score, classification): Tuple of score (0-100) and classification string
        """
        try:
            score = 0
            
            # Temperature score
            temp = data.get('temperature', 24)
            temp_score = self._calculate_metric_score(
                temp, self.ideal_ranges['temperature']
            )
            score += temp_score * self.weights['temperature']
            
            # Humidity score
            humidity = data.get('humidity', 65)
            humidity_score = self._calculate_metric_score(
                humidity, self.ideal_ranges['humidity']
            )
            score += humidity_score * self.weights['humidity']
            
            # Soil moisture score
            moisture = data.get('soil_moisture', 55)
            moisture_score = self._calculate_metric_score(
                moisture, self.ideal_ranges['soil_moisture']
            )
            score += moisture_score * self.weights['soil_moisture']
            
            # Light intensity score
            light = data.get('light_intensity', 50)
            light_score = self._calculate_metric_score(
                light, self.ideal_ranges['light_intensity']
            )
            score += light_score * self.weights['light_intensity']
            
            # Classify health
            if score >= 80:
                classification = "Excellent"
            elif score >= 60:
                classification = "Good"
            elif score >= 40:
                classification = "Fair"
            else:
                classification = "Poor"
            
            return score, classification
            
        except Exception as e:
            logger.error(f"Error in health score prediction: {e}")
            return 50.0, "Unknown"
    
    def _calculate_metric_score(self, value, ideal_range):
        """Calculate score for a single metric (0-100)"""
        try:
            min_val, max_val = ideal_range
            mid_val = (min_val + max_val) / 2
            range_span = max_val - min_val
            
            # Perfect score if within ideal range
            if min_val <= value <= max_val:
                return 100.0
            
            # Calculate penalty for deviation
            if value < min_val:
                deviation = min_val - value
                penalty = min(1.0, deviation / range_span)
            else:
                deviation = value - max_val
                penalty = min(1.0, deviation / range_span)
            
            score = 100 * (1 - penalty)
            return max(0, score)
            
        except Exception as e:
            logger.error(f"Error calculating metric score: {e}")
            return 50.0
