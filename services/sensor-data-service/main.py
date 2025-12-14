"""
Sensor Data Service - Main Entry Point
Subscribes to sensor data and publishes to aggregated topics
"""

import json
import logging
import os
import time
from datetime import datetime
import paho.mqtt.client as mqtt
from data_processor import DataProcessor
from publisher import DataPublisher

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
MQTT_BROKER = os.getenv('MQTT_BROKER', 'localhost')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
MQTT_USERNAME = os.getenv('MQTT_USERNAME', '')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD', '')

# Global state
sensor_data = {
    'temperature': None,
    'humidity': None,
    'soil_moisture': None,
    'light_intensity': None,
    'timestamp': None
}

client = mqtt.Client()
processor = DataProcessor()
publisher = DataPublisher()


def on_connect(client, userdata, flags, rc):
    """MQTT connection callback"""
    if rc == 0:
        logger.info(f"Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
        # Subscribe to sensor topics (both individual and aggregated)
        client.subscribe("plant-iot/sensors/temperature")
        client.subscribe("plant-iot/sensors/humidity")
        client.subscribe("plant-iot/sensors/soil-moisture")
        client.subscribe("plant-iot/sensors/light")
        client.subscribe("plant-iot/sensors/aggregated")  # Subscribe to aggregated data from simulator
        client.subscribe("plant-iot/status/actuators")
    else:
        logger.error(f"Failed to connect, return code {rc}")


def on_message(client, userdata, msg):
    """MQTT message callback"""
    try:
        topic = msg.topic
        payload = json.loads(msg.payload.decode('utf-8'))
        
        logger.info(f"MESSAGE RECEIVED on {topic}: {payload}")  # Always log incoming messages
        logger.debug(f"Received on {topic}: {payload}")
        
        # Handle aggregated data from simulator
        if topic == "plant-iot/sensors/aggregated":
            logger.info(f"Processing aggregated sensor data: {payload}")
            # Process the aggregated data directly
            aggregated_data = {
                'temperature': payload.get('temperature'),
                'humidity': payload.get('humidity'),
                'soil_moisture': payload.get('soil_moisture_percent', payload.get('soil_moisture')),
                'light_intensity': payload.get('light_percent', payload.get('light_intensity', 0)),
                'timestamp': payload.get('timestamp', int(time.time() * 1000))
            }
            
            logger.info(f"Processing aggregated data: {aggregated_data}")
            
            # Validate and process the aggregated data (temperature, humidity, soil_moisture are required)
            if aggregated_data['temperature'] is not None and aggregated_data['humidity'] is not None and aggregated_data['soil_moisture'] is not None:
                global sensor_data
                sensor_data = aggregated_data
                process_aggregated_data()
        
        # Handle individual sensor topics (backward compatibility)
        elif topic == "plant-iot/sensors/temperature":
            sensor_data['temperature'] = payload.get('temperature')
            sensor_data['timestamp'] = payload.get('timestamp', int(time.time() * 1000))
            
        elif topic == "plant-iot/sensors/humidity":
            sensor_data['humidity'] = payload.get('humidity')
            sensor_data['timestamp'] = payload.get('timestamp', int(time.time() * 1000))
            
        elif topic == "plant-iot/sensors/soil-moisture":
            sensor_data['soil_moisture'] = payload.get('moisture_percent', payload.get('moisture'))
            sensor_data['timestamp'] = payload.get('timestamp', int(time.time() * 1000))
            
        elif topic == "plant-iot/sensors/light":
            sensor_data['light_intensity'] = payload.get('light_percent', payload.get('light'))
            sensor_data['timestamp'] = payload.get('timestamp', int(time.time() * 1000))
        
        # Check if all sensors have data (for individual sensor topics)
        if topic.startswith("plant-iot/sensors/") and topic != "plant-iot/sensors/aggregated":
            if all(v is not None for v in sensor_data.values()):
                process_aggregated_data()
            
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from {msg.topic}: {e}")
    except Exception as e:
        logger.error(f"Error processing message: {e}")


def process_aggregated_data():
    """Process and publish aggregated sensor data"""
    try:
        # Validate data
        is_valid = processor.validate_data(sensor_data)
        
        if is_valid:
            # Add quality assessment
            sensor_data['quality'] = processor.assess_quality(sensor_data)
            
            # Detect anomalies
            anomalies = processor.detect_anomalies(sensor_data)
            
            # Publish aggregated data
            publisher.publish_aggregated(sensor_data)
            
            # Publish anomalies if detected
            if anomalies:
                logger.warning(f"Anomalies detected: {anomalies}")
                publisher.publish_anomalies(anomalies)
            
            logger.info(f"Aggregated: Temp={sensor_data['temperature']:.1f}°C, "
                       f"Humidity={sensor_data['humidity']:.1f}%, "
                       f"Moisture={sensor_data['soil_moisture']:.1f}%, "
                       f"Light={sensor_data['light_intensity']:.1f}%")
        else:
            logger.warning(f"Data validation failed: {sensor_data}")
            
    except Exception as e:
        logger.error(f"Error processing aggregated data: {e}")


def on_disconnect(client, userdata, rc):
    """MQTT disconnection callback"""
    if rc != 0:
        logger.warning(f"Unexpected disconnection (code {rc}), attempting to reconnect...")
    else:
        logger.info("Cleanly disconnected from MQTT broker")


def main():
    """Main entry point"""
    logger.info("Starting Sensor Data Service...")
    
    # Set up MQTT client
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    
    # Connect to MQTT broker
    try:
        if MQTT_USERNAME and MQTT_PASSWORD:
            client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        client.loop_start()
        
        logger.info("MQTT client started, waiting for messages...")
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except ConnectionRefusedError:
        logger.error(f"Failed to connect to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
        logger.info("Make sure MQTT broker is running: docker-compose up -d mosquitto")
        raise
    except KeyboardInterrupt:
        logger.info("Shutting down Sensor Data Service...")
        client.loop_stop()
        client.disconnect()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise


if __name__ == "__main__":
    main()
