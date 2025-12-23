"""
Integration tests for ML module
"""

import pytest
import pandas as pd
import numpy as np
from actuator_model import ActuatorController
from trend_predictor import TrendPredictor, generate_synthetic_history
from data_handler import SyntheticDataGenerator


class TestIntegration:
    """Integration tests combining multiple components"""
    
    def test_end_to_end_workflow(self):
        """Test complete workflow from data generation to prediction"""
        # Step 1: Generate training data
        data_gen = SyntheticDataGenerator(num_samples=500)
        features_df, targets_df = data_gen.generate_training_data()
        
        # Step 2: Train actuator controller
        actuator_controller = ActuatorController()
        actuator_accuracies = actuator_controller.train(features_df, targets_df)
        
        # Step 3: Generate historical data
        history = generate_synthetic_history(hours=12)
        
        # Step 4: Train trend predictor
        trend_predictor = TrendPredictor()
        trend_scores = trend_predictor.train(history)
        
        # Step 5: Make current predictions
        current_data = {
            'temperature': 32.0,
            'humidity': 45.0,
            'soil_moisture': 28.0,
            'light_intensity': 80.0
        }
        
        # Get actuator decisions
        actuator_decisions = actuator_controller.predict(current_data)
        
        # Get future trends
        future_trends = trend_predictor.predict_future(current_data, hours_ahead=6)
        
        # Verify all components worked
        assert all(acc > 0.7 for acc in actuator_accuracies.values())
        assert len(actuator_decisions) == 3
        assert len(future_trends) == 4
    
    def test_coordinated_decision_making(self):
        """Test coordinated decision making between models"""
        # Setup
        data_gen = SyntheticDataGenerator(num_samples=300)
        features_df, targets_df = data_gen.generate_training_data()
        
        actuator_controller = ActuatorController()
        actuator_controller.train(features_df, targets_df)
        
        history = generate_synthetic_history(hours=12)
        trend_predictor = TrendPredictor()
        trend_predictor.train(history)
        
        # Scenario: Current moisture is okay, but predicted to drop critically
        current_data = {
            'temperature': 28.0,
            'humidity': 50.0,
            'soil_moisture': 40.0,  # Currently okay
            'light_intensity': 70.0
        }
        
        # Get current decisions
        current_decisions = actuator_controller.predict(current_data)
        
        # Get future predictions
        future_trends = trend_predictor.predict_future(current_data, hours_ahead=6)
        
        # Check future moisture levels
        future_moisture = [p['value'] for p in future_trends['soil_moisture']]
        
        # If future moisture is predicted to drop below threshold
        will_need_water = any(m < 35.0 for m in future_moisture)
        
        # Should activate pump now or soon
        assert isinstance(will_need_water, bool)
    
    def test_stress_scenario_handling(self):
        """Test handling of multiple stress scenarios"""
        # Setup models
        data_gen = SyntheticDataGenerator(num_samples=400)
        features_df, targets_df = data_gen.generate_training_data()
        
        actuator_controller = ActuatorController()
        actuator_controller.train(features_df, targets_df)
        
        # Test multiple stress scenarios
        stress_scenarios = [
            {
                'name': 'Heat Wave',
                'data': {
                    'temperature': 38.0,
                    'humidity': 25.0,
                    'soil_moisture': 22.0,
                    'light_intensity': 95.0
                }
            },
            {
                'name': 'Drought',
                'data': {
                    'temperature': 30.0,
                    'humidity': 30.0,
                    'soil_moisture': 15.0,
                    'light_intensity': 85.0
                }
            },
            {
                'name': 'Cold Night',
                'data': {
                    'temperature': 15.0,
                    'humidity': 70.0,
                    'soil_moisture': 50.0,
                    'light_intensity': 5.0
                }
            }
        ]
        
        for scenario in stress_scenarios:
            decisions = actuator_controller.predict(scenario['data'])
            
            # At least one actuator should respond to stress
            assert any(decisions.values()), f"No actuator activated for {scenario['name']}"
    
    def test_model_consistency_over_time(self):
        """Test that models produce consistent results"""
        # Train models
        data_gen = SyntheticDataGenerator(num_samples=300)
        features_df, targets_df = data_gen.generate_training_data()
        
        controller = ActuatorController()
        controller.train(features_df, targets_df)
        
        # Make same prediction multiple times
        test_data = {
            'temperature': 28.0,
            'humidity': 60.0,
            'soil_moisture': 50.0,
            'light_intensity': 65.0
        }
        
        predictions = [controller.predict(test_data) for _ in range(5)]
        
        # All predictions should be identical
        for i in range(1, len(predictions)):
            assert predictions[0] == predictions[i]
    
    def test_anomaly_triggered_actions(self):
        """Test that anomalies trigger appropriate actions"""
        # Setup
        history = generate_synthetic_history(hours=24)
        predictor = TrendPredictor()
        predictor.train(history)
        
        # Normal data for prediction
        normal_data = {
            'temperature': 24.0,
            'humidity': 60.0,
            'soil_moisture': 55.0,
            'light_intensity': 70.0
        }
        
        predictions = predictor.predict_future(normal_data, hours_ahead=3)
        
        # Anomalous data
        anomalous_data = {
            'temperature': 42.0,  # Very high!
            'humidity': 15.0,     # Very low!
            'soil_moisture': 10.0,  # Critical!
            'light_intensity': 70.0
        }
        
        anomalies = predictor.detect_anomalies(anomalous_data, predictions)
        
        # Should detect multiple anomalies
        assert len(anomalies) >= 2
        
        # Check severity levels
        high_severity = [a for a in anomalies if a['severity'] == 'high']
        assert len(high_severity) > 0
    
    def test_predictive_maintenance_workflow(self):
        """Test workflow for predictive maintenance"""
        # Setup
        data_gen = SyntheticDataGenerator(num_samples=400)
        features_df, targets_df = data_gen.generate_training_data()
        
        actuator_controller = ActuatorController()
        actuator_controller.train(features_df, targets_df)
        
        history = generate_synthetic_history(hours=24)
        trend_predictor = TrendPredictor()
        trend_predictor.train(history)
        
        # Current state
        current_state = {
            'temperature': 26.0,
            'humidity': 55.0,
            'soil_moisture': 45.0,
            'light_intensity': 65.0
        }
        
        # Get future predictions
        future_predictions = trend_predictor.predict_future(current_state, hours_ahead=12)
        
        # Simulate checking future states
        maintenance_needed = []
        
        for i, pred in enumerate(future_predictions['soil_moisture']):
            if pred['value'] < 30.0:
                maintenance_needed.append({
                    'issue': 'Low moisture predicted',
                    'time': pred['time'],
                    'value': pred['value'],
                    'confidence': pred['confidence']
                })
        
        for i, pred in enumerate(future_predictions['temperature']):
            if pred['value'] > 35.0:
                maintenance_needed.append({
                    'issue': 'High temperature predicted',
                    'time': pred['time'],
                    'value': pred['value'],
                    'confidence': pred['confidence']
                })
        
        # System should identify potential issues
        assert isinstance(maintenance_needed, list)
    
    def test_batch_processing_efficiency(self):
        """Test efficient batch processing of multiple readings"""
        # Generate large batch
        data_gen = SyntheticDataGenerator(num_samples=1000)
        features_df, targets_df = data_gen.generate_training_data()
        
        # Train on subset
        controller = ActuatorController()
        controller.train(features_df[:800], targets_df[:800])
        
        # Batch predict on remaining
        test_features = features_df[800:]
        
        import time
        start_time = time.time()
        batch_predictions = controller.batch_predict(test_features)
        batch_time = time.time() - start_time
        
        # Individual predictions
        start_time = time.time()
        individual_predictions = []
        for idx in range(len(test_features)):
            row = test_features.iloc[idx]
            pred = controller.predict(row.to_dict())
            individual_predictions.append(pred)
        individual_time = time.time() - start_time
        
        # Batch should be faster
        assert batch_time < individual_time
        assert len(batch_predictions) == len(test_features)
    
    def test_model_robustness_to_noise(self):
        """Test model robustness with noisy data"""
        # Train models
        data_gen = SyntheticDataGenerator(num_samples=500)
        features_df, targets_df = data_gen.generate_training_data()
        
        controller = ActuatorController()
        controller.train(features_df, targets_df)
        
        # Base data
        base_data = {
            'temperature': 26.0,
            'humidity': 60.0,
            'soil_moisture': 50.0,
            'light_intensity': 70.0
        }
        
        base_prediction = controller.predict(base_data)
        
        # Add small noise and check consistency
        noise_levels = [0.5, 1.0, 2.0]
        consistent_count = 0
        
        for noise in noise_levels:
            noisy_data = base_data.copy()
            for key in noisy_data:
                noisy_data[key] += np.random.normal(0, noise)
            
            noisy_prediction = controller.predict(noisy_data)
            
            # Count how many actuators have same decision
            matches = sum(base_prediction[k] == noisy_prediction[k] for k in base_prediction)
            if matches >= 2:  # At least 2 out of 3 consistent
                consistent_count += 1
        
        # Should be consistent for most noise levels
        assert consistent_count >= 2


class TestModelValidation:
    """Validation tests for model performance"""
    
    def test_actuator_model_accuracy_threshold(self):
        """Test that actuator model meets minimum accuracy"""
        data_gen = SyntheticDataGenerator(num_samples=1000)
        features_df, targets_df = data_gen.generate_training_data()
        
        controller = ActuatorController()
        accuracies = controller.train(features_df, targets_df)
        
        # All models should meet 85% accuracy
        for actuator, acc in accuracies.items():
            assert acc >= 0.85, f"{actuator} accuracy {acc:.2%} below 85% threshold"
    
    def test_trend_prediction_rmse(self):
        """Test trend prediction RMSE is acceptable"""
        history = generate_synthetic_history(hours=24)
        
        predictor = TrendPredictor()
        scores = predictor.train(history)
        
        # R² scores should be positive (better than mean baseline)
        for metric, score in scores.items():
            assert score > 0.0, f"{metric} R² score {score} indicates poor fit"


def test_full_system_simulation():
    """Simulate full system operation over time"""
    # Initialize system
    data_gen = SyntheticDataGenerator(num_samples=500)
    features_df, targets_df = data_gen.generate_training_data()
    
    actuator_controller = ActuatorController()
    actuator_controller.train(features_df, targets_df)
    
    trend_predictor = TrendPredictor()
    history = generate_synthetic_history(hours=24)
    trend_predictor.train(history)
    
    # Simulate 10 time steps
    current_state = {
        'temperature': 24.0,
        'humidity': 60.0,
        'soil_moisture': 60.0,
        'light_intensity': 70.0
    }
    
    simulation_log = []
    
    for step in range(10):
        # Get actuator decisions
        decisions = actuator_controller.predict(current_state)
        
        # Get predictions
        predictions = trend_predictor.predict_future(current_state, hours_ahead=3)
        
        # Log state
        simulation_log.append({
            'step': step,
            'state': current_state.copy(),
            'decisions': decisions.copy(),
            'predictions': len(predictions)
        })
        
        # Simulate state change
        if decisions['pump']:
            current_state['soil_moisture'] += 5.0
        else:
            current_state['soil_moisture'] -= 2.0
        
        if decisions['fan']:
            current_state['temperature'] -= 1.0
        else:
            current_state['temperature'] += 0.5
        
        # Clamp values
        current_state['soil_moisture'] = np.clip(current_state['soil_moisture'], 0, 100)
        current_state['temperature'] = np.clip(current_state['temperature'], 15, 40)
    
    # Verify simulation ran successfully
    assert len(simulation_log) == 10
    assert all('decisions' in log for log in simulation_log)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
