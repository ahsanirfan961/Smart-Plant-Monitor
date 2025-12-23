"""
Test cases for Actuator Control Model
"""

import pytest
import numpy as np
import pandas as pd
from actuator_model import ActuatorController, train_and_save_model
from data_handler import SyntheticDataGenerator


class TestActuatorController:
    """Test suite for actuator control inference"""
    
    @pytest.fixture
    def trained_controller(self):
        """Fixture providing a trained controller"""
        data_gen = SyntheticDataGenerator(num_samples=500)
        features_df, targets_df = data_gen.generate_training_data()
        
        controller = ActuatorController()
        controller.train(features_df, targets_df)
        
        return controller
    
    def test_initialization(self):
        """Test controller initialization"""
        controller = ActuatorController()
        
        assert controller is not None
        assert controller.feature_names == ['temperature', 'humidity', 'soil_moisture', 'light_intensity']
        assert controller.target_names == ['fan', 'pump', 'light']
        assert not controller.is_trained
    
    def test_training(self):
        """Test model training"""
        data_gen = SyntheticDataGenerator(num_samples=200)
        features_df, targets_df = data_gen.generate_training_data()
        
        controller = ActuatorController()
        accuracies = controller.train(features_df, targets_df)
        
        assert controller.is_trained
        assert len(accuracies) == 3
        
        # Check that all models have reasonable accuracy
        for actuator, acc in accuracies.items():
            assert acc > 0.7, f"{actuator} accuracy too low: {acc}"
    
    def test_prediction_heat_stress(self, trained_controller):
        """Test prediction for heat stress scenario"""
        sensor_data = {
            'temperature': 36.0,
            'humidity': 40.0,
            'soil_moisture': 45.0,
            'light_intensity': 85.0
        }
        
        predictions = trained_controller.predict(sensor_data)
        
        assert predictions['fan'] is True, "Fan should be ON during heat stress"
        assert predictions['pump'] is False
        assert predictions['light'] is False
    
    def test_prediction_drought(self, trained_controller):
        """Test prediction for drought scenario"""
        sensor_data = {
            'temperature': 28.0,
            'humidity': 35.0,
            'soil_moisture': 20.0,
            'light_intensity': 75.0
        }
        
        predictions = trained_controller.predict(sensor_data)
        
        assert predictions['pump'] is True, "Pump should be ON during drought"
    
    def test_prediction_low_light(self, trained_controller):
        """Test prediction for low light scenario"""
        sensor_data = {
            'temperature': 22.0,
            'humidity': 65.0,
            'soil_moisture': 50.0,
            'light_intensity': 15.0
        }
        
        predictions = trained_controller.predict(sensor_data)
        
        assert predictions['light'] is True, "Light should be ON when intensity is low"
        assert predictions['fan'] is False
        assert predictions['pump'] is False
    
    def test_prediction_normal_conditions(self, trained_controller):
        """Test prediction for normal conditions"""
        sensor_data = {
            'temperature': 24.0,
            'humidity': 60.0,
            'soil_moisture': 55.0,
            'light_intensity': 70.0
        }
        
        predictions = trained_controller.predict(sensor_data)
        
        # All actuators should be OFF under normal conditions
        assert predictions['fan'] is False
        assert predictions['pump'] is False
        assert predictions['light'] is False
    
    def test_prediction_with_confidence(self, trained_controller):
        """Test prediction with confidence scores"""
        sensor_data = {
            'temperature': 32.0,
            'humidity': 45.0,
            'soil_moisture': 28.0,
            'light_intensity': 80.0
        }
        
        predictions = trained_controller.predict_with_confidence(sensor_data)
        
        assert len(predictions) == 3
        
        for actuator, (state, confidence) in predictions.items():
            assert isinstance(state, bool)
            assert 0.0 <= confidence <= 1.0
    
    def test_batch_prediction(self, trained_controller):
        """Test batch prediction on multiple samples"""
        data_gen = SyntheticDataGenerator(num_samples=50)
        features_df, _ = data_gen.generate_training_data()
        
        predictions_df = trained_controller.batch_predict(features_df)
        
        assert len(predictions_df) == 50
        assert list(predictions_df.columns) == ['fan', 'pump', 'light']
        assert predictions_df.dtypes['fan'] == np.int64
    
    def test_missing_features_raises_error(self, trained_controller):
        """Test that missing features raise ValueError"""
        incomplete_data = {
            'temperature': 25.0,
            'humidity': 60.0
            # Missing soil_moisture and light_intensity
        }
        
        with pytest.raises(ValueError, match="Missing feature"):
            trained_controller.predict(incomplete_data)
    
    def test_untrained_model_raises_error(self):
        """Test that prediction on untrained model raises error"""
        controller = ActuatorController()
        
        sensor_data = {
            'temperature': 25.0,
            'humidity': 60.0,
            'soil_moisture': 55.0,
            'light_intensity': 70.0
        }
        
        with pytest.raises(ValueError, match="Models must be trained"):
            controller.predict(sensor_data)
    
    def test_save_and_load_model(self, tmp_path, trained_controller):
        """Test model saving and loading"""
        model_path = tmp_path / "test_model.pkl"
        
        # Save model
        trained_controller.save_models(str(model_path))
        assert model_path.exists()
        
        # Load model
        new_controller = ActuatorController()
        new_controller.load_models(str(model_path))
        
        assert new_controller.is_trained
        
        # Test that loaded model makes same predictions
        sensor_data = {
            'temperature': 32.0,
            'humidity': 45.0,
            'soil_moisture': 28.0,
            'light_intensity': 80.0
        }
        
        pred1 = trained_controller.predict(sensor_data)
        pred2 = new_controller.predict(sensor_data)
        
        assert pred1 == pred2
    
    def test_scenario_evaluation(self, trained_controller):
        """Test evaluation on specific scenarios"""
        data_gen = SyntheticDataGenerator()
        scenarios = data_gen.generate_test_scenarios()
        
        results = trained_controller.evaluate_scenarios(scenarios)
        
        assert 'total' in results
        assert 'correct' in results
        assert 'accuracy' in results
        assert results['total'] == len(scenarios)
        assert 0.0 <= results['accuracy'] <= 1.0
    
    def test_high_humidity_fan_activation(self, trained_controller):
        """Test fan activation for high humidity"""
        sensor_data = {
            'temperature': 26.0,
            'humidity': 85.0,
            'soil_moisture': 60.0,
            'light_intensity': 50.0
        }
        
        predictions = trained_controller.predict(sensor_data)
        
        assert predictions['fan'] is True, "Fan should activate for high humidity"
    
    def test_multiple_stress_factors(self, trained_controller):
        """Test prediction with multiple stress factors"""
        sensor_data = {
            'temperature': 34.0,
            'humidity': 30.0,
            'soil_moisture': 18.0,
            'light_intensity': 10.0
        }
        
        predictions = trained_controller.predict(sensor_data)
        
        # Multiple actuators should be ON
        assert predictions['fan'] is True
        assert predictions['pump'] is True
        assert predictions['light'] is True


class TestDataGenerator:
    """Test suite for synthetic data generation"""
    
    def test_generate_training_data(self):
        """Test training data generation"""
        data_gen = SyntheticDataGenerator(num_samples=100)
        features_df, targets_df = data_gen.generate_training_data()
        
        assert len(features_df) == 100
        assert len(targets_df) == 100
        assert list(features_df.columns) == ['temperature', 'humidity', 'soil_moisture', 'light_intensity']
        assert list(targets_df.columns) == ['fan', 'pump', 'light']
    
    def test_data_ranges(self):
        """Test that generated data is within valid ranges"""
        data_gen = SyntheticDataGenerator(num_samples=200)
        features_df, _ = data_gen.generate_training_data()
        
        # Check temperature range
        assert features_df['temperature'].min() >= 10
        assert features_df['temperature'].max() <= 40
        
        # Check percentage ranges
        for col in ['humidity', 'soil_moisture', 'light_intensity']:
            assert features_df[col].min() >= 0
            assert features_df[col].max() <= 100
    
    def test_generate_test_scenarios(self):
        """Test test scenario generation"""
        data_gen = SyntheticDataGenerator()
        scenarios = data_gen.generate_test_scenarios()
        
        assert len(scenarios) > 0
        
        for scenario in scenarios:
            assert 'name' in scenario
            assert 'input' in scenario
            assert 'expected' in scenario
            assert all(k in scenario['input'] for k in ['temperature', 'humidity', 'soil_moisture', 'light_intensity'])
            assert all(k in scenario['expected'] for k in ['fan', 'pump', 'light'])


def test_full_pipeline():
    """Integration test for full training and prediction pipeline"""
    # Generate data
    data_gen = SyntheticDataGenerator(num_samples=300)
    features_df, targets_df = data_gen.generate_training_data()
    
    # Train model
    controller = ActuatorController()
    accuracies = controller.train(features_df, targets_df)
    
    # Check accuracies
    assert all(acc > 0.7 for acc in accuracies.values())
    
    # Make prediction
    test_data = {
        'temperature': 32.0,
        'humidity': 45.0,
        'soil_moisture': 28.0,
        'light_intensity': 80.0
    }
    
    predictions = controller.predict(test_data)
    
    # Verify output format
    assert isinstance(predictions, dict)
    assert len(predictions) == 3
    assert all(isinstance(v, bool) for v in predictions.values())


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
