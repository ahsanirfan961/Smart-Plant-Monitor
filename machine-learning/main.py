"""
Main entry point for ML module
Demonstrates usage of actuator control and trend prediction
"""

import logging
from actuator_model import ActuatorController, train_and_save_model as train_actuator
from trend_predictor import TrendPredictor, train_and_save_trend_model as train_trend
from data_handler import SyntheticDataGenerator
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demo_actuator_control():
    """Demonstrate actuator control inference"""
    logger.info("\n" + "="*60)
    logger.info("ACTUATOR CONTROL DEMONSTRATION")
    logger.info("="*60)
    
    # Train or load model
    controller = train_actuator()
    
    # Test scenarios
    logger.info("\n--- Testing Various Scenarios ---\n")
    
    scenarios = [
        {
            'name': 'Normal Conditions',
            'data': {
                'temperature': 24.0,
                'humidity': 60.0,
                'soil_moisture': 55.0,
                'light_intensity': 70.0
            }
        },
        {
            'name': 'Heat Stress',
            'data': {
                'temperature': 36.0,
                'humidity': 40.0,
                'soil_moisture': 45.0,
                'light_intensity': 85.0
            }
        },
        {
            'name': 'Drought Alert',
            'data': {
                'temperature': 28.0,
                'humidity': 35.0,
                'soil_moisture': 22.0,
                'light_intensity': 75.0
            }
        },
        {
            'name': 'Night Time Low Light',
            'data': {
                'temperature': 22.0,
                'humidity': 65.0,
                'soil_moisture': 50.0,
                'light_intensity': 12.0
            }
        }
    ]
    
    # Collect all predictions for tuple output
    all_predictions = []
    
    for scenario in scenarios:
        logger.info(f"\nScenario: {scenario['name']}")
        logger.info(f"Inputs: {scenario['data']}")
        
        decisions = controller.predict(scenario['data'])
        decisions_conf = controller.predict_with_confidence(scenario['data'])
        
        logger.info("Decisions:")
        for actuator, state in decisions.items():
            conf = decisions_conf[actuator][1]
            status = "ON" if state else "OFF"
            logger.info(f"  {actuator.upper()}: {status} (confidence: {conf:.2%})")
        
        # Format as tuple for integration: (scenario_name, inputs, decisions, confidences)
        tuple_output = (
            scenario['name'],
            tuple(scenario['data'].items()),
            tuple((act, bool(state)) for act, state in decisions.items()),
            tuple((act, decisions_conf[act][1]) for act in decisions.keys())
        )
        all_predictions.append(tuple_output)
    
    # Print integration-friendly tuple output
    logger.info("\n" + "="*60)
    logger.info("INTEGRATION OUTPUT (TUPLE FORMAT)")
    logger.info("="*60)
    for scenario_name, inputs, decisions, confidences in all_predictions:
        logger.info(f"\n({repr(scenario_name)}, {inputs}, {decisions}, {confidences})")


def demo_trend_prediction():
    """Demonstrate predictive analytics"""
    logger.info("\n" + "="*60)
    logger.info("TREND PREDICTION DEMONSTRATION")
    logger.info("="*60)
    
    # Train or load model
    predictor = train_trend()
    
    # Current state
    current_data = {
        'temperature': 26.5,
        'humidity': 62.0,
        'soil_moisture': 55.0,
        'light_intensity': 75.0
    }
    
    logger.info(f"\nCurrent State: {current_data}")
    
    # Predict future (6 hours ahead)
    logger.info("\n--- 6-Hour Forecast ---\n")
    predictions = predictor.predict_future(current_data, hours_ahead=6)
    
    # Collect predictions in tuple format
    predictions_tuples = {}
    
    for metric, pred_list in predictions.items():
        logger.info(f"\n{metric.upper()} forecast:")
        metric_predictions = []
        
        for i in range(min(4, len(pred_list))):  # Show first 4 predictions
            pred = pred_list[i]
            logger.info(
                f"  {pred['time']}: {pred['value']:.2f} "
                f"(confidence: {pred['confidence']:.2%})"
            )
            # Format as tuple: (time, value, confidence)
            metric_predictions.append((pred['time'], round(pred['value'], 2), round(pred['confidence'], 4)))
        
        predictions_tuples[metric] = tuple(metric_predictions)
    
    # Anomaly detection
    logger.info("\n--- Anomaly Detection ---\n")
    
    # Create anomalous data
    anomalous_data = {
        'temperature': 38.0,  # Very high
        'humidity': 25.0,     # Very low
        'soil_moisture': 18.0,  # Critical
        'light_intensity': 75.0
    }
    
    logger.info(f"Testing anomalous data: {anomalous_data}")
    anomalies = predictor.detect_anomalies(anomalous_data, predictions)
    
    # Collect anomalies in tuple format
    anomalies_tuples = []
    
    if anomalies:
        logger.info("Anomalies detected:")
        for anomaly in anomalies:
            logger.info(
                f"  {anomaly['metric']}: "
                f"Current={anomaly['current_value']:.2f}, "
                f"Expected={anomaly['predicted_value']:.2f}, "
                f"Deviation={anomaly['deviation']:.2f} "
                f"[{anomaly['severity']}]"
            )
            # Format as tuple: (metric, current_value, predicted_value, deviation, severity)
            anomalies_tuples.append((
                anomaly['metric'],
                round(anomaly['current_value'], 2),
                round(anomaly['predicted_value'], 2),
                round(anomaly['deviation'], 2),
                anomaly['severity']
            ))
    else:
        logger.info("No anomalies detected")
    
    # Print integration-friendly tuple output
    logger.info("\n" + "="*60)
    logger.info("INTEGRATION OUTPUT (TUPLE FORMAT)")
    logger.info("="*60)
    logger.info(f"\nCurrent State: {tuple(current_data.items())}")
    logger.info("\nPredictions:")
    for metric, pred_tuples in predictions_tuples.items():
        logger.info(f"  {metric}: {pred_tuples}")
    logger.info(f"\nAnomalies: {tuple(anomalies_tuples)}")


def demo_integrated_system():
    """Demonstrate integrated decision making"""
    logger.info("\n" + "="*60)
    logger.info("INTEGRATED SYSTEM DEMONSTRATION")
    logger.info("="*60)
    
    # Load models
    actuator_controller = ActuatorController()
    if not actuator_controller.is_trained:
        logger.info("Training actuator model...")
        actuator_controller = train_actuator()
    else:
        logger.info("Loaded existing actuator model")
    
    trend_predictor = TrendPredictor()
    if not trend_predictor.is_trained:
        logger.info("Training trend model...")
        trend_predictor = train_trend()
    else:
        logger.info("Loaded existing trend model")
    
    # Scenario: Marginal soil moisture, predict if watering needed
    logger.info("\n--- Smart Watering Decision ---\n")
    
    current_state = {
        'temperature': 28.0,
        'humidity': 50.0,
        'soil_moisture': 38.0,  # Just above threshold
        'light_intensity': 70.0
    }
    
    logger.info(f"Current State: {current_state}")
    
    # Current decision
    current_decisions = actuator_controller.predict(current_state)
    logger.info(f"\nImmediate Decisions: {current_decisions}")
    
    # Future prediction
    future_trends = trend_predictor.predict_future(current_state, hours_ahead=6)
    
    # Check if moisture will drop critically
    future_moisture = [p['value'] for p in future_trends['soil_moisture']]
    min_future_moisture = min(future_moisture)
    
    logger.info(f"\nPredicted minimum moisture (6h): {min_future_moisture:.1f}%")
    
    recommendation = None
    if min_future_moisture < 30.0:
        logger.info("⚠️  Recommendation: Activate pump NOW (preventive action)")
        logger.info(f"   Moisture predicted to drop below 30% threshold")
        recommendation = "ACTIVATE_PUMP_PREVENTIVE"
    elif current_decisions['pump']:
        logger.info("✓  Pump activated based on current readings")
        recommendation = "PUMP_ACTIVE_CURRENT"
    else:
        logger.info("✓  No watering needed - moisture stable")
        recommendation = "STABLE_NO_ACTION"
    
    # Print integration-friendly tuple output
    logger.info("\n" + "="*60)
    logger.info("INTEGRATION OUTPUT (TUPLE FORMAT)")
    logger.info("="*60)
    
    integrated_decision = (
        tuple(current_state.items()),
        tuple((act, bool(state)) for act, state in current_decisions.items()),
        round(min_future_moisture, 2),
        recommendation
    )
    
    logger.info(f"\n{integrated_decision}")


def main():
    """Main entry point"""
    logger.info("="*60)
    logger.info("SMART PLANT ML MODULE - DEMONSTRATION")
    logger.info("="*60)
    
    try:
        # Run demonstrations
        demo_actuator_control()
        demo_trend_prediction()
        demo_integrated_system()
        
        logger.info("\n" + "="*60)
        logger.info("ALL DEMONSTRATIONS COMPLETED SUCCESSFULLY")
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"Error during demonstration: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
