"""
Trend Predictor - Predictive analytics for environmental trends
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import PolynomialFeatures
from typing import Dict, List, Tuple, Optional
import joblib
import logging
import os
from datetime import datetime, timedelta
from config import (
    TREND_MODEL_PATH,
    MAX_FORECAST_HOURS,
    FORECAST_INTERVAL_MINUTES
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TrendPredictor:
    """Predict future environmental trends using time-series analysis"""
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize trend predictor
        
        Args:
            model_path: Path to saved model file (optional)
        """
        self.model_path = model_path or TREND_MODEL_PATH
        self.models: Dict[str, LinearRegression] = {}
        self.poly_features: Optional[PolynomialFeatures] = None
        self.is_trained = False
        
        # Historical data buffers (for online learning)
        self.history_buffers: Dict[str, List[Tuple[float, float]]] = {
            'temperature': [],
            'humidity': [],
            'soil_moisture': [],
            'light_intensity': []
        }
        
        # Maximum buffer size (24 hours of data at 1-minute intervals)
        self.max_buffer_size = 1440
        
        # Try to load existing models
        if os.path.exists(self.model_path):
            self.load_models()
    
    def train(self, historical_data: pd.DataFrame) -> Dict[str, float]:
        """
        Train trend prediction models on historical data
        
        Args:
            historical_data: DataFrame with columns ['timestamp', 'temperature', 'humidity', 'soil_moisture', 'light_intensity']
        
        Returns:
            Dictionary with R² scores for each metric
        """
        logger.info("Training trend prediction models...")
        
        # Ensure timestamp is numeric (minutes since start)
        if 'timestamp' not in historical_data.columns:
            historical_data['timestamp'] = range(len(historical_data))
        
        # Use polynomial features for better trend capture
        self.poly_features = PolynomialFeatures(degree=2, include_bias=False)
        
        metrics = ['temperature', 'humidity', 'soil_moisture', 'light_intensity']
        scores = {}
        
        for metric in metrics:
            if metric not in historical_data.columns:
                logger.warning(f"Metric {metric} not found in data, skipping...")
                continue
            
            logger.info(f"Training model for {metric}...")
            
            # Prepare features and target
            X = historical_data[['timestamp']].values
            y = historical_data[metric].values
            
            # Transform features
            X_poly = self.poly_features.fit_transform(X)
            
            # Create and train model (Ridge for regularization)
            model = Ridge(alpha=1.0)
            model.fit(X_poly, y)
            
            # Calculate R² score
            score = model.score(X_poly, y)
            scores[metric] = score
            
            logger.info(f"{metric} model R² score: {score:.4f}")
            
            # Store model
            self.models[metric] = model
        
        self.is_trained = True
        
        return scores
    
    def predict_future(
        self, 
        current_data: Dict[str, float], 
        hours_ahead: int = 6
    ) -> Dict[str, List[Dict]]:
        """
        Predict future environmental values
        
        Args:
            current_data: Current sensor readings
            hours_ahead: Number of hours to forecast
        
        Returns:
            Dictionary with predictions for each metric
            Example: {
                'temperature': [
                    {'time': '14:30', 'value': 28.5, 'confidence': 0.85},
                    {'time': '15:00', 'value': 29.2, 'confidence': 0.82},
                    ...
                ]
            }
        """
        if not self.is_trained:
            # Use simple linear trends if not trained
            return self._predict_simple_trends(current_data, hours_ahead)
        
        predictions = {}
        
        # Generate future timestamps
        num_predictions = (hours_ahead * 60) // FORECAST_INTERVAL_MINUTES
        future_timestamps = np.arange(1, num_predictions + 1) * FORECAST_INTERVAL_MINUTES
        
        for metric, value in current_data.items():
            if metric not in self.models:
                continue
            
            model = self.models[metric]
            
            # Prepare future timestamps
            X_future = future_timestamps.reshape(-1, 1)
            X_future_poly = self.poly_features.transform(X_future)
            
            # Make predictions
            y_pred = model.predict(X_future_poly)
            
            # Calculate confidence (decreases with time)
            confidences = np.exp(-future_timestamps / (hours_ahead * 60))
            
            # Format predictions
            predictions[metric] = []
            for i, (timestamp, pred_value, confidence) in enumerate(
                zip(future_timestamps, y_pred, confidences)
            ):
                # Calculate actual time
                minutes_ahead = int(timestamp)
                future_time = datetime.now() + timedelta(minutes=minutes_ahead)
                
                predictions[metric].append({
                    'time': future_time.strftime('%H:%M'),
                    'minutes_ahead': minutes_ahead,
                    'value': float(pred_value),
                    'confidence': float(confidence)
                })
        
        return predictions
    
    def _predict_simple_trends(
        self, 
        current_data: Dict[str, float], 
        hours_ahead: int
    ) -> Dict[str, List[Dict]]:
        """
        Predict using simple linear trends (fallback when not trained)
        
        Args:
            current_data: Current sensor readings
            hours_ahead: Number of hours to forecast
        
        Returns:
            Dictionary with simple trend predictions
        """
        predictions = {}
        
        # Simple trend assumptions (hardcoded for demonstration)
        trends = {
            'temperature': 0.5,      # Increases 0.5°C per hour
            'humidity': -1.0,        # Decreases 1% per hour
            'soil_moisture': -2.0,   # Decreases 2% per hour (evaporation)
            'light_intensity': 0.0   # Stays relatively constant
        }
        
        num_predictions = (hours_ahead * 60) // FORECAST_INTERVAL_MINUTES
        
        for metric, current_value in current_data.items():
            if metric not in trends:
                continue
            
            predictions[metric] = []
            
            for i in range(1, num_predictions + 1):
                minutes_ahead = i * FORECAST_INTERVAL_MINUTES
                hours_fraction = minutes_ahead / 60
                
                # Apply trend
                predicted_value = current_value + (trends[metric] * hours_fraction)
                
                # Add some uncertainty
                noise = np.random.normal(0, 0.5 * hours_fraction)
                predicted_value += noise
                
                # Clamp to realistic ranges
                if metric == 'temperature':
                    predicted_value = np.clip(predicted_value, 10, 40)
                elif metric in ['humidity', 'soil_moisture', 'light_intensity']:
                    predicted_value = np.clip(predicted_value, 0, 100)
                
                # Calculate confidence
                confidence = max(0.3, 1.0 - (hours_fraction / hours_ahead))
                
                future_time = datetime.now() + timedelta(minutes=minutes_ahead)
                
                predictions[metric].append({
                    'time': future_time.strftime('%H:%M'),
                    'minutes_ahead': minutes_ahead,
                    'value': float(predicted_value),
                    'confidence': float(confidence)
                })
        
        return predictions
    
    def detect_anomalies(
        self, 
        current_data: Dict[str, float], 
        predictions: Dict[str, List[Dict]]
    ) -> List[Dict[str, any]]:
        """
        Detect anomalies by comparing current data with predictions
        
        Args:
            current_data: Current sensor readings
            predictions: Predicted values
        
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        for metric, value in current_data.items():
            if metric not in predictions or len(predictions[metric]) == 0:
                continue
            
            # Get first prediction (closest to current time)
            first_pred = predictions[metric][0]
            predicted_value = first_pred['value']
            
            # Calculate deviation
            deviation = abs(value - predicted_value)
            
            # Adaptive threshold based on metric type and realistic ranges
            # Use percentage or absolute value whichever is larger for sensitivity
            if metric == 'temperature':
                # ±8°C threshold (realistic daily variation)
                threshold = max(8.0, abs(value) * 0.15)
            elif metric == 'light_intensity':
                # ±35% threshold (light can vary significantly)
                threshold = max(35.0, abs(value) * 0.40)
            else:  # humidity, soil_moisture
                # ±30% threshold (allows for natural variation)
                threshold = max(30.0, abs(value) * 0.40)
            
            # Only flag as anomaly if deviation significantly exceeds threshold
            if deviation > threshold:
                anomalies.append({
                    'metric': metric,
                    'current_value': value,
                    'predicted_value': predicted_value,
                    'deviation': deviation,
                    'severity': 'high' if deviation > threshold * 2 else 'medium'
                })
        
        return anomalies
    
    def update_history(self, timestamp: float, data: Dict[str, float]) -> None:
        """
        Update historical data buffers for online learning
        
        Args:
            timestamp: Unix timestamp or minutes since start
            data: Sensor readings
        """
        for metric, value in data.items():
            if metric in self.history_buffers:
                self.history_buffers[metric].append((timestamp, value))
                
                # Maintain buffer size
                if len(self.history_buffers[metric]) > self.max_buffer_size:
                    self.history_buffers[metric].pop(0)
    
    def retrain_online(self) -> None:
        """
        Retrain models using accumulated historical data
        """
        if not any(len(buf) > 10 for buf in self.history_buffers.values()):
            logger.warning("Not enough data for retraining")
            return
        
        logger.info("Retraining models with online data...")
        
        # Convert buffers to DataFrame
        data_dict = {'timestamp': []}
        
        for metric, buffer in self.history_buffers.items():
            if len(buffer) > 0:
                timestamps, values = zip(*buffer)
                if len(data_dict['timestamp']) == 0:
                    data_dict['timestamp'] = timestamps
                data_dict[metric] = values
        
        historical_data = pd.DataFrame(data_dict)
        
        # Retrain
        scores = self.train(historical_data)
        
        logger.info("Online retraining complete")
        for metric, score in scores.items():
            logger.info(f"{metric}: R² = {score:.4f}")
    
    def save_models(self, path: Optional[str] = None) -> None:
        """
        Save trained models to disk
        
        Args:
            path: Path to save models (optional)
        """
        save_path = path or self.model_path
        
        # Create directory if needed
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Save models and polynomial features
        model_data = {
            'models': self.models,
            'poly_features': self.poly_features,
            'history_buffers': self.history_buffers
        }
        
        joblib.dump(model_data, save_path)
        logger.info(f"Models saved to {save_path}")
    
    def load_models(self, path: Optional[str] = None) -> None:
        """
        Load trained models from disk
        
        Args:
            path: Path to load models from (optional)
        """
        load_path = path or self.model_path
        
        if not os.path.exists(load_path):
            logger.warning(f"Model file not found: {load_path}")
            return
        
        model_data = joblib.load(load_path)
        self.models = model_data['models']
        self.poly_features = model_data['poly_features']
        self.history_buffers = model_data.get('history_buffers', self.history_buffers)
        self.is_trained = True
        
        logger.info(f"Models loaded from {load_path}")


def generate_synthetic_history(hours: int = 24) -> pd.DataFrame:
    """
    Generate synthetic historical data for training
    
    Args:
        hours: Number of hours of history to generate
    
    Returns:
        DataFrame with historical sensor readings
    """
    minutes = hours * 60
    timestamps = np.arange(0, minutes, 1)
    
    # Simulate daily cycles
    hour_of_day = (timestamps / 60) % 24
    
    # Temperature: sinusoidal daily cycle
    temperature = 24 + 6 * np.sin(2 * np.pi * (hour_of_day - 6) / 24) + np.random.normal(0, 1, len(timestamps))
    temperature = np.clip(temperature, 15, 35)
    
    # Humidity: inverse correlation with temperature
    humidity = 70 - 15 * np.sin(2 * np.pi * (hour_of_day - 6) / 24) + np.random.normal(0, 3, len(timestamps))
    humidity = np.clip(humidity, 30, 90)
    
    # Soil moisture: gradual decay with periodic watering
    soil_moisture = 80 - (timestamps / minutes) * 40  # Gradual decay
    # Add watering events
    watering_times = np.random.choice(len(timestamps), size=hours // 6, replace=False)
    for t in watering_times:
        soil_moisture[t:] += 20
        soil_moisture = np.clip(soil_moisture, 20, 90)
    soil_moisture += np.random.normal(0, 2, len(timestamps))
    
    # Light intensity: day/night cycle
    light_intensity = np.where(
        (hour_of_day >= 6) & (hour_of_day <= 18),
        70 + 20 * np.sin(np.pi * (hour_of_day - 6) / 12),
        10
    ) + np.random.normal(0, 5, len(timestamps))
    light_intensity = np.clip(light_intensity, 0, 100)
    
    return pd.DataFrame({
        'timestamp': timestamps,
        'temperature': temperature,
        'humidity': humidity,
        'soil_moisture': soil_moisture,
        'light_intensity': light_intensity
    })


def train_and_save_trend_model() -> TrendPredictor:
    """
    Train trend prediction model and save to disk
    
    Returns:
        Trained TrendPredictor instance
    """
    logger.info("=== Training Trend Prediction Model ===")
    
    # Generate synthetic historical data
    historical_data = generate_synthetic_history(hours=24)
    
    # Train model
    predictor = TrendPredictor()
    scores = predictor.train(historical_data)
    
    logger.info("\n=== Training Results ===")
    for metric, score in scores.items():
        logger.info(f"{metric}: R² = {score:.4f}")
    
    # Save model
    predictor.save_models()
    
    return predictor


if __name__ == "__main__":
    # Train and save model
    predictor = train_and_save_trend_model()
    
    # Test prediction
    current_data = {
        'temperature': 26.5,
        'humidity': 62.0,
        'soil_moisture': 55.0,
        'light_intensity': 75.0
    }
    
    predictions = predictor.predict_future(current_data, hours_ahead=6)
    
    logger.info("\n=== Sample Predictions ===")
    logger.info(f"Current data: {current_data}")
    
    for metric, pred_list in predictions.items():
        logger.info(f"\n{metric.upper()} forecast:")
        for i, pred in enumerate(pred_list[:4]):  # Show first 4 predictions
            logger.info(f"  {pred['time']}: {pred['value']:.2f} (confidence: {pred['confidence']:.2f})")
    
    # Test anomaly detection
    anomalies = predictor.detect_anomalies(current_data, predictions)
    if anomalies:
        logger.info("\n=== Detected Anomalies ===")
        for anomaly in anomalies:
            logger.info(f"  {anomaly['metric']}: deviation = {anomaly['deviation']:.2f}")
    else:
        logger.info("\nNo anomalies detected")
