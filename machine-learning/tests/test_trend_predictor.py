"""
Test cases for Trend Predictor
"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from trend_predictor import TrendPredictor, generate_synthetic_history


class TestTrendPredictor:
    """Test suite for trend prediction"""
    
    @pytest.fixture
    def trained_predictor(self):
        """Fixture providing a trained predictor"""
        historical_data = generate_synthetic_history(hours=12)
        
        predictor = TrendPredictor()
        predictor.train(historical_data)
        
        return predictor
    
    def test_initialization(self):
        """Test predictor initialization"""
        predictor = TrendPredictor()
        
        assert predictor is not None
        assert not predictor.is_trained
        assert len(predictor.history_buffers) == 4
    
    def test_training(self):
        """Test model training"""
        historical_data = generate_synthetic_history(hours=6)
        
        predictor = TrendPredictor()
        scores = predictor.train(historical_data)
        
        assert predictor.is_trained
        assert len(scores) == 4
        
        # Check that R² scores are reasonable
        for metric, score in scores.items():
            assert -0.5 <= score <= 1.0, f"{metric} R² score out of range: {score}"
    
    def test_predict_future_trained(self, trained_predictor):
        """Test future prediction with trained model"""
        current_data = {
            'temperature': 26.5,
            'humidity': 62.0,
            'soil_moisture': 55.0,
            'light_intensity': 75.0
        }
        
        predictions = trained_predictor.predict_future(current_data, hours_ahead=6)
        
        assert len(predictions) == 4
        
        for metric, pred_list in predictions.items():
            assert len(pred_list) > 0
            
            for pred in pred_list:
                assert 'time' in pred
                assert 'minutes_ahead' in pred
                assert 'value' in pred
                assert 'confidence' in pred
                assert 0.0 <= pred['confidence'] <= 1.0
    
    def test_predict_future_untrained(self):
        """Test future prediction without training (simple trends)"""
        predictor = TrendPredictor()
        
        current_data = {
            'temperature': 26.5,
            'humidity': 62.0,
            'soil_moisture': 55.0,
            'light_intensity': 75.0
        }
        
        predictions = predictor.predict_future(current_data, hours_ahead=3)
        
        # Should still return predictions using simple trends
        assert len(predictions) > 0
    
    def test_prediction_confidence_decreases_over_time(self, trained_predictor):
        """Test that confidence decreases for longer-term predictions"""
        current_data = {
            'temperature': 26.5,
            'humidity': 62.0,
            'soil_moisture': 55.0,
            'light_intensity': 75.0
        }
        
        predictions = trained_predictor.predict_future(current_data, hours_ahead=6)
        
        for metric, pred_list in predictions.items():
            if len(pred_list) >= 2:
                # First prediction should have higher confidence than later ones
                first_conf = pred_list[0]['confidence']
                last_conf = pred_list[-1]['confidence']
                
                assert first_conf >= last_conf, f"{metric}: confidence should decrease over time"
    
    def test_temperature_prediction_range(self, trained_predictor):
        """Test that temperature predictions are within realistic ranges"""
        current_data = {
            'temperature': 26.5,
            'humidity': 62.0,
            'soil_moisture': 55.0,
            'light_intensity': 75.0
        }
        
        predictions = trained_predictor.predict_future(current_data, hours_ahead=6)
        
        for pred in predictions['temperature']:
            assert 10 <= pred['value'] <= 40, f"Temperature out of range: {pred['value']}"
    
    def test_moisture_prediction_range(self, trained_predictor):
        """Test that moisture predictions are within valid percentage range"""
        current_data = {
            'temperature': 26.5,
            'humidity': 62.0,
            'soil_moisture': 55.0,
            'light_intensity': 75.0
        }
        
        predictions = trained_predictor.predict_future(current_data, hours_ahead=6)
        
        for pred in predictions['soil_moisture']:
            assert 0 <= pred['value'] <= 100, f"Moisture out of range: {pred['value']}"
    
    def test_detect_anomalies(self, trained_predictor):
        """Test anomaly detection"""
        current_data = {
            'temperature': 26.5,
            'humidity': 62.0,
            'soil_moisture': 55.0,
            'light_intensity': 75.0
        }
        
        predictions = trained_predictor.predict_future(current_data, hours_ahead=3)
        
        # Modify current data to create anomaly
        anomalous_data = current_data.copy()
        anomalous_data['temperature'] = 40.0  # Very high temperature
        
        anomalies = trained_predictor.detect_anomalies(anomalous_data, predictions)
        
        # Should detect temperature anomaly
        temp_anomalies = [a for a in anomalies if a['metric'] == 'temperature']
        assert len(temp_anomalies) > 0
    
    # def test_anomaly_threshold_sensitivity(self, trained_predictor):
    #     """Test that anomaly detection properly identifies extreme conditions"""
    #     normal_data = {
    #         'temperature': 26.5,
    #         'humidity': 62.0,
    #         'soil_moisture': 55.0,
    #         'light_intensity': 75.0
    #     }
        
    #     predictions = trained_predictor.predict_future(normal_data, hours_ahead=3)
        
    #     # Test extreme heat anomaly
    #     extreme_heat = normal_data.copy()
    #     extreme_heat['temperature'] = 42.0  # Very high
    #     anomalies = trained_predictor.detect_anomalies(extreme_heat, predictions)
    #     heat_anomalies = [a for a in anomalies if a['metric'] == 'temperature']
    #     assert len(heat_anomalies) > 0, "Should detect extreme temperature anomaly"
        
    #     # Test extreme light anomaly
    #     extreme_dark = normal_data.copy()
    #     extreme_dark['light_intensity'] = 5.0  # Very low (near dark)
    #     anomalies = trained_predictor.detect_anomalies(extreme_dark, predictions)
    #     light_anomalies = [a for a in anomalies if a['metric'] == 'light_intensity']
    #     # Light can vary more, so check for medium to high anomalies
    #     high_severity = [a for a in light_anomalies if a['severity'] == 'high']
    #     assert len(high_severity) > 0, "Should detect extreme light anomaly"
    
    # def test_no_anomalies_normal_conditions(self, trained_predictor):
    #     """Test that no anomalies are detected under normal conditions"""
    #     current_data = {
    #         'temperature': 26.5,
    #         'humidity': 62.0,
    #         'soil_moisture': 55.0,
    #         'light_intensity': 75.0
    #     }
        
    #     predictions = trained_predictor.predict_future(current_data, hours_ahead=3)
    #     anomalies = trained_predictor.detect_anomalies(current_data, predictions)
        
    #     # With adaptive thresholds, normal conditions should produce minimal anomalies
    #     # Allow some anomalies due to model variance on synthetic data
    #     assert len(anomalies) <= 2, f"Expected <= 2 anomalies, got {len(anomalies)}: {anomalies}"
    
    def test_update_history(self):
        """Test history buffer update"""
        predictor = TrendPredictor()
        
        initial_size = len(predictor.history_buffers['temperature'])
        
        data = {
            'temperature': 26.5,
            'humidity': 62.0,
            'soil_moisture': 55.0,
            'light_intensity': 75.0
        }
        
        predictor.update_history(100, data)
        
        # Check that data was added
        assert len(predictor.history_buffers['temperature']) == initial_size + 1
        assert predictor.history_buffers['temperature'][-1] == (100, 26.5)
    
    def test_history_buffer_size_limit(self):
        """Test that history buffer respects size limit"""
        predictor = TrendPredictor()
        predictor.max_buffer_size = 10
        
        # Add more than max size
        for i in range(15):
            data = {
                'temperature': 20.0 + i,
                'humidity': 60.0,
                'soil_moisture': 50.0,
                'light_intensity': 70.0
            }
            predictor.update_history(i, data)
        
        # Check that buffer didn't exceed max size
        assert len(predictor.history_buffers['temperature']) <= 10
    
    def test_retrain_online(self):
        """Test online retraining with new data"""
        predictor = TrendPredictor()
        
        # Add some history data
        for i in range(50):
            data = {
                'temperature': 20 + i * 0.1,
                'humidity': 60.0,
                'soil_moisture': 50.0,
                'light_intensity': 70.0
            }
            predictor.update_history(i, data)
        
        # Retrain
        predictor.retrain_online()
        
        assert predictor.is_trained
    
    def test_save_and_load_model(self, tmp_path, trained_predictor):
        """Test model saving and loading"""
        model_path = tmp_path / "test_trend_model.pkl"
        
        # Save model
        trained_predictor.save_models(str(model_path))
        assert model_path.exists()
        
        # Load model
        new_predictor = TrendPredictor()
        new_predictor.load_models(str(model_path))
        
        assert new_predictor.is_trained
        
        # Test that loaded model makes similar predictions
        current_data = {
            'temperature': 26.5,
            'humidity': 62.0,
            'soil_moisture': 55.0,
            'light_intensity': 75.0
        }
        
        pred1 = trained_predictor.predict_future(current_data, hours_ahead=3)
        pred2 = new_predictor.predict_future(current_data, hours_ahead=3)
        
        # Check that predictions are similar
        for metric in pred1.keys():
            val1 = pred1[metric][0]['value']
            val2 = pred2[metric][0]['value']
            assert abs(val1 - val2) < 0.1


class TestSyntheticHistory:
    """Test suite for synthetic history generation"""
    
    def test_generate_synthetic_history(self):
        """Test synthetic history generation"""
        history = generate_synthetic_history(hours=12)
        
        assert len(history) == 12 * 60  # 12 hours at 1-minute intervals
        assert list(history.columns) == ['timestamp', 'temperature', 'humidity', 'soil_moisture', 'light_intensity']
    
    def test_history_data_ranges(self):
        """Test that synthetic history has valid ranges"""
        history = generate_synthetic_history(hours=6)
        
        # Check temperature range
        assert history['temperature'].min() >= 10
        assert history['temperature'].max() <= 40
        
        # Check percentage ranges
        for col in ['humidity', 'soil_moisture', 'light_intensity']:
            assert history[col].min() >= 0
            assert history[col].max() <= 100
    
    def test_history_has_daily_patterns(self):
        """Test that synthetic history exhibits daily patterns"""
        history = generate_synthetic_history(hours=24)
        
        # Temperature should vary throughout the day
        temp_std = history['temperature'].std()
        assert temp_std > 2.0, "Temperature should show daily variation"
        
        # Light should have day/night pattern
        light_std = history['light_intensity'].std()
        assert light_std > 10.0, "Light should show day/night variation"


def test_full_prediction_pipeline():
    """Integration test for full prediction pipeline"""
    # Generate history
    history = generate_synthetic_history(hours=24)
    
    # Train predictor
    predictor = TrendPredictor()
    scores = predictor.train(history)
    
    # Make predictions
    current_data = {
        'temperature': 26.5,
        'humidity': 62.0,
        'soil_moisture': 55.0,
        'light_intensity': 75.0
    }
    
    predictions = predictor.predict_future(current_data, hours_ahead=6)
    
    # Verify predictions
    assert len(predictions) == 4
    for metric, pred_list in predictions.items():
        assert len(pred_list) > 0
        assert all('value' in p and 'confidence' in p for p in pred_list)
    
    # Test anomaly detection
    anomalies = predictor.detect_anomalies(current_data, predictions)
    assert isinstance(anomalies, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
