"""
Data Handler - Generates synthetic training data for ML models
"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict, List
import logging
from config import (
    TEMPERATURE_HIGH_THRESHOLD,
    MOISTURE_LOW_THRESHOLD,
    LIGHT_LOW_THRESHOLD,
    TRAINING_SAMPLES
)

logger = logging.getLogger(__name__)


class SyntheticDataGenerator:
    """Generate synthetic sensor data and actuator states for training"""
    
    def __init__(self, num_samples: int = TRAINING_SAMPLES):
        """
        Initialize data generator
        
        Args:
            num_samples: Number of training samples to generate
        """
        self.num_samples = num_samples
        np.random.seed(42)  # For reproducibility
    
    def generate_training_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Generate synthetic training data
        
        Returns:
            (features_df, targets_df): DataFrames with features and target actuator states
        """
        logger.info(f"Generating {self.num_samples} training samples...")
        
        # Generate sensor readings
        data = {
            'temperature': self._generate_temperature(),
            'humidity': self._generate_humidity(),
            'soil_moisture': self._generate_moisture(),
            'light_intensity': self._generate_light()
        }
        
        features_df = pd.DataFrame(data)
        
        # Generate corresponding actuator states based on rules + noise
        targets_df = self._generate_actuator_states(features_df)
        
        logger.info("Training data generation complete")
        return features_df, targets_df
    
    def _generate_temperature(self) -> np.ndarray:
        """Generate temperature readings (10-40°C)"""
        # Base distribution around 24°C with realistic variations
        base = np.random.normal(24, 6, self.num_samples)
        # Add some extreme conditions
        extreme_indices = np.random.choice(self.num_samples, size=int(self.num_samples * 0.1), replace=False)
        base[extreme_indices] = np.random.uniform(35, 40, len(extreme_indices))
        return np.clip(base, 10, 40)
    
    def _generate_humidity(self) -> np.ndarray:
        """Generate humidity readings (20-90%)"""
        # Bimodal: dry and humid conditions
        mode1 = np.random.normal(45, 10, self.num_samples // 2)
        mode2 = np.random.normal(70, 10, self.num_samples - self.num_samples // 2)
        combined = np.concatenate([mode1, mode2])
        np.random.shuffle(combined)
        return np.clip(combined, 20, 90)
    
    def _generate_moisture(self) -> np.ndarray:
        """Generate soil moisture readings (0-100%)"""
        # Exponential decay pattern (realistic soil drying)
        base = np.random.uniform(20, 90, self.num_samples)
        # Add dry condition samples
        dry_indices = np.random.choice(self.num_samples, size=int(self.num_samples * 0.15), replace=False)
        base[dry_indices] = np.random.uniform(0, 30, len(dry_indices))
        return np.clip(base, 0, 100)
    
    def _generate_light(self) -> np.ndarray:
        """Generate light intensity readings (0-100%)"""
        # Day/night cycle simulation
        day_light = np.random.uniform(40, 100, self.num_samples // 2)
        night_light = np.random.uniform(0, 30, self.num_samples - self.num_samples // 2)
        combined = np.concatenate([day_light, night_light])
        np.random.shuffle(combined)
        return np.clip(combined, 0, 100)
    
    def _generate_actuator_states(self, features_df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate actuator states based on sensor readings
        
        Args:
            features_df: DataFrame with sensor readings
        
        Returns:
            DataFrame with actuator states (fan, pump, light)
        """
        n = len(features_df)
        
        # Fan control: ON if temperature is high OR humidity is very high
        fan_on = (
            (features_df['temperature'] > TEMPERATURE_HIGH_THRESHOLD) | 
            (features_df['humidity'] > 80)
        ).astype(int)
        
        # Add some noise (imperfect control)
        noise_indices = np.random.choice(n, size=int(n * 0.05), replace=False)
        fan_on.iloc[noise_indices] = 1 - fan_on.iloc[noise_indices]
        
        # Pump control: ON if soil moisture is low
        pump_on = (
            features_df['soil_moisture'] < MOISTURE_LOW_THRESHOLD
        ).astype(int)
        
        # Add some noise
        noise_indices = np.random.choice(n, size=int(n * 0.05), replace=False)
        pump_on.iloc[noise_indices] = 1 - pump_on.iloc[noise_indices]
        
        # Light control: ON if light intensity is low (nighttime or cloudy)
        light_on = (
            features_df['light_intensity'] < LIGHT_LOW_THRESHOLD
        ).astype(int)
        
        # Add some noise
        noise_indices = np.random.choice(n, size=int(n * 0.05), replace=False)
        light_on.iloc[noise_indices] = 1 - light_on.iloc[noise_indices]
        
        targets_df = pd.DataFrame({
            'fan': fan_on,
            'pump': pump_on,
            'light': light_on
        })
        
        return targets_df
    
    def generate_test_scenarios(self) -> List[Dict]:
        """
        Generate specific test scenarios for validation
        
        Returns:
            List of test scenarios with expected outcomes
        """
        scenarios = [
            {
                'name': 'Normal Conditions',
                'input': {
                    'temperature': 24.0,
                    'humidity': 60.0,
                    'soil_moisture': 55.0,
                    'light_intensity': 70.0
                },
                'expected': {
                    'fan': False,
                    'pump': False,
                    'light': False
                }
            },
            {
                'name': 'Heat Stress',
                'input': {
                    'temperature': 36.0,
                    'humidity': 40.0,
                    'soil_moisture': 45.0,
                    'light_intensity': 85.0
                },
                'expected': {
                    'fan': True,
                    'pump': False,
                    'light': False
                }
            },
            {
                'name': 'Drought Condition',
                'input': {
                    'temperature': 28.0,
                    'humidity': 35.0,
                    'soil_moisture': 20.0,
                    'light_intensity': 75.0
                },
                'expected': {
                    'fan': False,
                    'pump': True,
                    'light': False
                }
            },
            {
                'name': 'Low Light Nighttime',
                'input': {
                    'temperature': 22.0,
                    'humidity': 65.0,
                    'soil_moisture': 50.0,
                    'light_intensity': 15.0
                },
                'expected': {
                    'fan': False,
                    'pump': False,
                    'light': True
                }
            },
            {
                'name': 'Multiple Stress Factors',
                'input': {
                    'temperature': 34.0,
                    'humidity': 30.0,
                    'soil_moisture': 18.0,
                    'light_intensity': 90.0
                },
                'expected': {
                    'fan': True,
                    'pump': True,
                    'light': False
                }
            },
            {
                'name': 'High Humidity',
                'input': {
                    'temperature': 26.0,
                    'humidity': 85.0,
                    'soil_moisture': 60.0,
                    'light_intensity': 50.0
                },
                'expected': {
                    'fan': True,
                    'pump': False,
                    'light': False
                }
            }
        ]
        
        return scenarios


def create_sample_data_dict() -> Dict:
    """
    Create a sample data dictionary for quick testing
    
    Returns:
        Dictionary with sample sensor readings
    """
    return {
        'temperature': 32.0,
        'humidity': 45.0,
        'soil_moisture': 28.0,
        'light_intensity': 80.0
    }
