"""
Actuator Model - ML-based actuator control inference
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from typing import Dict, Tuple, Optional
import joblib
import logging
import os
from config import (
    ACTUATOR_MODEL_PATH,
    FEATURE_NAMES,
    TARGET_ACTUATORS,
    PREDICTION_CONFIDENCE_THRESHOLD,
    TEST_SPLIT_RATIO
)
from data_handler import SyntheticDataGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ActuatorController:
    """ML-based actuator control decision system"""
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize actuator controller
        
        Args:
            model_path: Path to saved model file (optional)
        """
        self.model_path = model_path or ACTUATOR_MODEL_PATH
        self.models: Dict[str, RandomForestClassifier] = {}
        self.feature_names = FEATURE_NAMES
        self.target_names = TARGET_ACTUATORS
        self.is_trained = False
        
        # Try to load existing models
        if os.path.exists(self.model_path):
            self.load_models()
    
    def train(self, features_df: pd.DataFrame, targets_df: pd.DataFrame) -> Dict[str, float]:
        """
        Train actuator control models
        
        Args:
            features_df: DataFrame with sensor readings
            targets_df: DataFrame with actuator states
        
        Returns:
            Dictionary with accuracy metrics for each actuator
        """
        logger.info("Training actuator control models...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            features_df, targets_df, test_size=TEST_SPLIT_RATIO, random_state=42
        )
        
        accuracies = {}
        
        # Train separate model for each actuator
        for actuator in self.target_names:
            logger.info(f"Training model for {actuator}...")
            
            # Create and train Random Forest classifier
            model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
            
            model.fit(X_train, y_train[actuator])
            
            # Evaluate
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test[actuator], y_pred)
            accuracies[actuator] = accuracy
            
            logger.info(f"{actuator} model accuracy: {accuracy:.4f}")
            logger.info(f"Classification report:\n{classification_report(y_test[actuator], y_pred)}")
            
            # Store model
            self.models[actuator] = model
        
        self.is_trained = True
        
        # Calculate feature importance
        self._log_feature_importance()
        
        return accuracies
    
    def predict(self, sensor_data: Dict[str, float]) -> Dict[str, bool]:
        """
        Predict actuator states based on sensor readings
        
        Args:
            sensor_data: Dictionary with sensor readings
                Example: {'temperature': 32, 'humidity': 45, 'soil_moisture': 28, 'light_intensity': 80}
        
        Returns:
            Dictionary with actuator states
                Example: {'fan': True, 'pump': True, 'light': False}
        
        Raises:
            ValueError: If models are not trained
        """
        if not self.is_trained:
            raise ValueError("Models must be trained before prediction")
        
        # Validate input
        for feature in self.feature_names:
            if feature not in sensor_data:
                raise ValueError(f"Missing feature: {feature}")
        
        # Prepare input
        X = pd.DataFrame([sensor_data])[self.feature_names]
        
        # Make predictions
        predictions = {}
        for actuator, model in self.models.items():
            pred = model.predict(X)[0]
            predictions[actuator] = bool(pred)
        
        return predictions
    
    def predict_with_confidence(self, sensor_data: Dict[str, float]) -> Dict[str, Tuple[bool, float]]:
        """
        Predict actuator states with confidence scores
        
        Args:
            sensor_data: Dictionary with sensor readings
        
        Returns:
            Dictionary with (state, confidence) tuples for each actuator
        """
        if not self.is_trained:
            raise ValueError("Models must be trained before prediction")
        
        # Validate input
        for feature in self.feature_names:
            if feature not in sensor_data:
                raise ValueError(f"Missing feature: {feature}")
        
        # Prepare input
        X = pd.DataFrame([sensor_data])[self.feature_names]
        
        # Make predictions with probabilities
        predictions = {}
        for actuator, model in self.models.items():
            pred_proba = model.predict_proba(X)[0]
            pred_class = int(np.argmax(pred_proba))
            confidence = pred_proba[pred_class]
            
            predictions[actuator] = (bool(pred_class), float(confidence))
        
        return predictions
    
    def batch_predict(self, sensor_data_list: pd.DataFrame) -> pd.DataFrame:
        """
        Predict actuator states for multiple sensor readings
        
        Args:
            sensor_data_list: DataFrame with multiple sensor readings
        
        Returns:
            DataFrame with actuator predictions
        """
        if not self.is_trained:
            raise ValueError("Models must be trained before prediction")
        
        predictions_dict = {}
        
        for actuator, model in self.models.items():
            predictions_dict[actuator] = model.predict(sensor_data_list[self.feature_names])
        
        return pd.DataFrame(predictions_dict)
    
    def save_models(self, path: Optional[str] = None) -> None:
        """
        Save trained models to disk
        
        Args:
            path: Path to save models (optional)
        """
        save_path = path or self.model_path
        
        # Create directory if needed
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Save all models
        model_data = {
            'models': self.models,
            'feature_names': self.feature_names,
            'target_names': self.target_names
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
        self.feature_names = model_data['feature_names']
        self.target_names = model_data['target_names']
        self.is_trained = True
        
        logger.info(f"Models loaded from {load_path}")
    
    def _log_feature_importance(self) -> None:
        """Log feature importance for each model"""
        logger.info("\n=== Feature Importance ===")
        
        for actuator, model in self.models.items():
            importances = model.feature_importances_
            feature_importance = sorted(
                zip(self.feature_names, importances),
                key=lambda x: x[1],
                reverse=True
            )
            
            logger.info(f"\n{actuator.upper()} Model:")
            for feature, importance in feature_importance:
                logger.info(f"  {feature}: {importance:.4f}")
    
    def evaluate_scenarios(self, scenarios: list) -> Dict[str, any]:
        """
        Evaluate model performance on specific test scenarios
        
        Args:
            scenarios: List of test scenarios from data_handler
        
        Returns:
            Dictionary with evaluation results
        """
        if not self.is_trained:
            raise ValueError("Models must be trained before evaluation")
        
        results = {
            'total': len(scenarios),
            'correct': 0,
            'scenarios': []
        }
        
        for scenario in scenarios:
            predictions = self.predict(scenario['input'])
            expected = scenario['expected']
            
            # Check if all predictions match
            all_correct = all(
                predictions[act] == expected[act] 
                for act in self.target_names
            )
            
            if all_correct:
                results['correct'] += 1
            
            results['scenarios'].append({
                'name': scenario['name'],
                'input': scenario['input'],
                'predicted': predictions,
                'expected': expected,
                'correct': all_correct
            })
        
        results['accuracy'] = results['correct'] / results['total']
        
        return results


def train_and_save_model() -> ActuatorController:
    """
    Train actuator control model and save to disk
    
    Returns:
        Trained ActuatorController instance
    """
    logger.info("=== Training Actuator Control Model ===")
    
    # Generate training data
    data_gen = SyntheticDataGenerator()
    features_df, targets_df = data_gen.generate_training_data()
    
    # Train model
    controller = ActuatorController()
    accuracies = controller.train(features_df, targets_df)
    
    logger.info("\n=== Training Results ===")
    for actuator, acc in accuracies.items():
        logger.info(f"{actuator}: {acc:.4f}")
    
    # Save model
    controller.save_models()
    
    # Evaluate on test scenarios
    scenarios = data_gen.generate_test_scenarios()
    eval_results = controller.evaluate_scenarios(scenarios)
    
    logger.info(f"\n=== Scenario Evaluation ===")
    logger.info(f"Scenario Accuracy: {eval_results['accuracy']:.2%}")
    
    for scenario in eval_results['scenarios']:
        status = "✓" if scenario['correct'] else "✗"
        logger.info(f"{status} {scenario['name']}")
    
    return controller


if __name__ == "__main__":
    # Train and save model
    controller = train_and_save_model()
    
    # Test prediction
    test_data = {
        'temperature': 32.0,
        'humidity': 45.0,
        'soil_moisture': 28.0,
        'light_intensity': 80.0
    }
    
    predictions = controller.predict(test_data)
    predictions_conf = controller.predict_with_confidence(test_data)
    
    logger.info("\n=== Sample Prediction ===")
    logger.info(f"Input: {test_data}")
    logger.info(f"Predictions: {predictions}")
    logger.info(f"With confidence: {predictions_conf}")
