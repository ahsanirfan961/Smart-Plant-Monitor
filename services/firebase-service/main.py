"""
Firebase Service - Manages cloud database operations
"""

import json
import logging
import os
import time
from datetime import datetime, timedelta
import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)


class FirebaseService:
    """Manage Firebase Realtime Database operations"""
    
    def __init__(self):
        """Initialize Firebase service"""
        self.mqtt_broker = os.getenv('MQTT_BROKER', 'localhost')
        self.mqtt_port = int(os.getenv('MQTT_PORT', 1883))
        self.client = mqtt.Client(client_id="firebase-service")
        self._connect_mqtt()
        
        # Simulated data store (replacing Firebase for demo)
        self.data_store = {
            'sensors': {'current': {}, 'history': []},
            'actuators': {},
            'events': []
        }
    
    def _connect_mqtt(self):
        """Connect to MQTT broker with retry logic"""
        max_retries = 5
        attempt = 0
        while attempt < max_retries:
            try:
                self.client.on_connect = self._on_connect
                self.client.on_message = self._on_message
                logger.info(f"Connecting to MQTT broker at {self.mqtt_broker}:{self.mqtt_port}...")
                self.client.connect(self.mqtt_broker, self.mqtt_port, keepalive=60)
                self.client.loop_start()
                logger.info("Firebase service connected to MQTT")
                time.sleep(1)  # Give connection time to establish
                return
            except Exception as e:
                attempt += 1
                logger.warning(f"MQTT connection attempt {attempt}/{max_retries} failed: {e}")
                if attempt < max_retries:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Failed to connect to MQTT after {max_retries} attempts")
                    # Continue anyway - will reconnect on retry
    
    def _on_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            logger.info("Firebase service subscribed to MQTT topics")
            client.subscribe("plant-iot/sensors/aggregated")
            client.subscribe("plant-iot/status/all")
            client.subscribe("plant-iot/analytics/#")
        else:
            logger.error(f"MQTT connection failed: {rc}")
    
    def _on_message(self, client, userdata, msg):
        """MQTT message callback"""
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode('utf-8'))
            
            if "sensors" in topic:
                self.store_sensor_data(payload)
            elif "status" in topic:
                self.store_actuator_status(payload)
            elif "analytics" in topic:
                self.store_analytics_data(topic, payload)
                
        except Exception as e:
            logger.error(f"Error processing Firebase message: {e}")
    
    def store_sensor_data(self, data):
        """Store sensor data to Firebase"""
        try:
            timestamp = data.get('timestamp', int(time.time() * 1000))
            
            # Store current reading
            self.data_store['sensors']['current'] = {
                'temperature': data.get('temperature'),
                'humidity': data.get('humidity'),
                'soil_moisture': data.get('soil_moisture'),
                'light_intensity': data.get('light_intensity'),
                'quality': data.get('quality'),
                'timestamp': timestamp
            }
            
            # Store in history
            self.data_store['sensors']['history'].append(self.data_store['sensors']['current'])
            
            # Keep only last 24 hours
            cutoff_time = int(time.time() * 1000) - (24 * 3600 * 1000)
            self.data_store['sensors']['history'] = [
                d for d in self.data_store['sensors']['history']
                if d['timestamp'] > cutoff_time
            ]
            
            logger.debug(f"Stored sensor data: {data}")
            
        except Exception as e:
            logger.error(f"Error storing sensor data: {e}")
    
    def store_actuator_status(self, data):
        """Store actuator status to Firebase"""
        try:
            timestamp = int(time.time() * 1000)
            self.data_store['actuators'] = {
                'pump': data.get('pump', {}),
                'fan': data.get('fan', {}),
                'grow_light': data.get('grow_light', {}),
                'timestamp': timestamp
            }
            
            logger.debug(f"Stored actuator status: {data}")
            
        except Exception as e:
            logger.error(f"Error storing actuator status: {e}")
    
    def store_analytics_data(self, topic, data):
        """Store analytics data (predictions, anomalies, etc.)"""
        try:
            timestamp = int(time.time() * 1000)
            
            event = {
                'type': topic.split('/')[-1],
                'data': data,
                'timestamp': timestamp
            }
            
            self.data_store['events'].append(event)
            
            # Keep only recent events
            cutoff_time = int(time.time() * 1000) - (7 * 24 * 3600 * 1000)
            self.data_store['events'] = [
                e for e in self.data_store['events']
                if e['timestamp'] > cutoff_time
            ]
            
            logger.debug(f"Stored analytics data: {event}")
            
        except Exception as e:
            logger.error(f"Error storing analytics data: {e}")
    
    def get_current_sensor_data(self):
        """Get current sensor readings"""
        return self.data_store['sensors']['current']
    
    def get_sensor_history(self, hours=24):
        """Get sensor data from last N hours"""
        try:
            cutoff_time = int(time.time() * 1000) - (hours * 3600 * 1000)
            return [
                d for d in self.data_store['sensors']['history']
                if d['timestamp'] > cutoff_time
            ]
        except Exception as e:
            logger.error(f"Error getting sensor history: {e}")
            return []
    
    def get_current_actuator_status(self):
        """Get current actuator status"""
        return self.data_store['actuators']
    
    def publish_to_dashboard(self):
        """Publish data to dashboard via MQTT"""
        try:
            dashboard_data = {
                'sensors': self.data_store['sensors']['current'],
                'actuators': self.data_store['actuators'],
                'timestamp': int(time.time() * 1000)
            }
            
            self.client.publish(
                "plant-iot/dashboard/data",
                json.dumps(dashboard_data),
                qos=1
            )
            
        except Exception as e:
            logger.error(f"Error publishing to dashboard: {e}")
    
    def __del__(self):
        """Cleanup"""
        try:
            self.client.loop_stop()
            self.client.disconnect()
        except:
            pass


if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        level=os.getenv('LOG_LEVEL', 'INFO'),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("Starting Firebase Service...")
    service = FirebaseService()
    
    try:
        logger.info("Firebase service running, waiting for MQTT messages...")
        while True:
            time.sleep(5)
            # Periodically publish aggregated data to dashboard
            service.publish_to_dashboard()
            
    except KeyboardInterrupt:
        logger.info("Firebase service shutting down...")
    except Exception as e:
        logger.error(f"Fatal error in Firebase service: {e}")
        raise
