"""
Data Analytics Service - ML predictions and analytics
"""

import json
import logging
import os
import time
from datetime import datetime
import paho.mqtt.client as mqtt
import numpy as np
from predictor import SoilDrynessPredictor, HealthScorePredictor

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
MQTT_BROKER = os.getenv('MQTT_BROKER', 'localhost')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))

# Global state
sensor_data = {}
last_prediction = {}

client = mqtt.Client()
dryness_predictor = SoilDrynessPredictor()
health_predictor = HealthScorePredictor()

# Prediction intervals
DRYNESS_PREDICTION_INTERVAL = 3600  # 1 hour
HEALTH_PREDICTION_INTERVAL = 1800   # 30 minutes
last_dryness_prediction = 0
last_health_prediction = 0


def on_connect(client, userdata, flags, rc):
    """MQTT connection callback"""
    if rc == 0:
        logger.info(f"Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
        client.subscribe("plant-iot/sensors/aggregated")
    else:
        logger.error(f"Failed to connect, return code {rc}")


def on_message(client, userdata, msg):
    """MQTT message callback"""
    try:
        global sensor_data, last_dryness_prediction, last_health_prediction
        
        topic = msg.topic
        payload = json.loads(msg.payload.decode('utf-8'))
        
        if topic == "plant-iot/sensors/aggregated":
            sensor_data = payload
            
            current_time = time.time()
            
            # Perform predictions at intervals
            if current_time - last_dryness_prediction >= DRYNESS_PREDICTION_INTERVAL:
                predict_soil_dryness(sensor_data)
                last_dryness_prediction = current_time
            
            if current_time - last_health_prediction >= HEALTH_PREDICTION_INTERVAL:
                predict_health_score(sensor_data)
                last_health_prediction = current_time
            
    except Exception as e:
        logger.error(f"Error processing message: {e}")


def predict_soil_dryness(data):
    """Predict soil dryness ETA"""
    try:
        moisture = data.get('soil_moisture')
        temperature = data.get('temperature')
        humidity = data.get('humidity')
        
        if moisture is None:
            return
        
        # Get prediction
        eta_hours, confidence = dryness_predictor.predict(
            moisture, temperature, humidity
        )
        
        # Determine recommendation
        if eta_hours < 3:
            recommendation = "Water immediately!"
        elif eta_hours < 12:
            recommendation = f"Water in {int(eta_hours)} hours"
        else:
            recommendation = "Soil moisture is good"
        
        prediction = {
            'timestamp': int(time.time() * 1000),
            'current_moisture': moisture,
            'critical_moisture': 30,
            'eta_hours': eta_hours,
            'confidence': confidence,
            'recommendation': recommendation
        }
        
        last_prediction['dryness'] = prediction
        
        # Publish prediction
        client.publish(
            "plant-iot/predictions/soil-dryness",
            json.dumps(prediction),
            qos=1
        )
        
        logger.info(f"Soil dryness prediction: {eta_hours:.1f} hours "
                   f"(confidence: {confidence:.2f})")
        
    except Exception as e:
        logger.error(f"Error predicting soil dryness: {e}")


def predict_health_score(data):
    """Predict plant health score"""
    try:
        # Get health score
        score, classification = health_predictor.predict(data)
        
        # Determine recommendations
        recommendations = []
        if data.get('temperature', 0) > 35:
            recommendations.append("Temperature is high, increase ventilation")
        if data.get('soil_moisture', 50) < 30:
            recommendations.append("Soil is dry, water the plant")
        if data.get('light_intensity', 50) < 20:
            recommendations.append("Light is low, activate grow light")
        if data.get('humidity', 60) > 85:
            recommendations.append("Humidity is high, improve air circulation")
        
        health = {
            'timestamp': int(time.time() * 1000),
            'score': score,
            'classification': classification,
            'recommendations': recommendations
        }
        
        last_prediction['health'] = health
        
        # Publish prediction
        client.publish(
            "plant-iot/predictions/health-score",
            json.dumps(health),
            qos=1
        )
        
        logger.info(f"Plant health score: {score:.1f}/100 ({classification})")
        
    except Exception as e:
        logger.error(f"Error predicting health score: {e}")


def on_disconnect(client, userdata, rc):
    """MQTT disconnection callback"""
    if rc != 0:
        logger.warning(f"Unexpected disconnection (code {rc})")
    else:
        logger.info("Cleanly disconnected from MQTT broker")


def main():
    """Main entry point"""
    logger.info("Starting Data Analytics Service...")
    
    # Set up MQTT client
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        client.loop_start()
        
        logger.info("Analytics service started, waiting for sensor data...")
        
        while True:
            time.sleep(1)
            
    except ConnectionRefusedError:
        logger.error(f"Failed to connect to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
        raise
    except KeyboardInterrupt:
        logger.info("Shutting down Data Analytics Service...")
        client.loop_stop()
        client.disconnect()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise


if __name__ == "__main__":
    main()
