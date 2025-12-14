"""
Publisher - Publishes processed sensor data to MQTT topics
"""

import json
import logging
import os
import time
import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)


class DataPublisher:
    """Publish processed sensor data and analytics to MQTT"""
    
    def __init__(self):
        """Initialize MQTT publisher"""
        self.mqtt_broker = os.getenv('MQTT_BROKER', 'localhost')
        self.mqtt_port = int(os.getenv('MQTT_PORT', 1883))
        self.client = mqtt.Client(client_id="sensor-data-service")
        self.connected = False
        
        # Set callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_publish = self._on_publish
        
        self._connect()
    
    def _on_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            self.connected = True
            logger.info("Publisher connected to MQTT broker")
        else:
            logger.error(f"Failed to connect to MQTT broker: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback"""
        self.connected = False
        if rc != 0:
            logger.warning(f"Unexpected disconnection from MQTT: {rc}")
    
    def _on_publish(self, client, userdata, mid):
        """MQTT publish callback"""
        logger.debug(f"Message published with id: {mid}")
    
    def _connect(self):
        """Connect to MQTT broker with retry logic"""
        max_retries = 5
        for attempt in range(max_retries):
            try:
                self.client.connect(self.mqtt_broker, self.mqtt_port, keepalive=60)
                self.client.loop_start()
                logger.info(f"Publisher connecting to {self.mqtt_broker}:{self.mqtt_port}")
                time.sleep(1)  # Give connection time to establish
                return
            except Exception as e:
                logger.warning(f"Connection attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Failed to connect to MQTT broker after {max_retries} attempts")
    
    def publish_aggregated(self, data):
        """Publish aggregated sensor data"""
        try:
            payload = json.dumps({
                'timestamp': data.get('timestamp'),
                'temperature': data.get('temperature'),
                'humidity': data.get('humidity'),
                'soil_moisture': data.get('soil_moisture'),
                'light_intensity': data.get('light_intensity'),
                'quality': data.get('quality', 'good')
            })
            
            self.client.publish("plant-iot/sensors/aggregated", payload, qos=1)
            logger.debug(f"Published aggregated data: {payload}")
            return True
            
        except Exception as e:
            logger.error(f"Error publishing aggregated data: {e}")
            return False
    
    def publish_anomalies(self, anomalies):
        """Publish detected anomalies"""
        try:
            payload = json.dumps({
                'timestamp': int(time.time() * 1000),
                'anomalies': anomalies
            })
            
            self.client.publish("plant-iot/analytics/anomalies", payload, qos=1)
            logger.debug(f"Published anomalies: {payload}")
            return True
            
        except Exception as e:
            logger.error(f"Error publishing anomalies: {e}")
            return False
    
    def publish_health(self, health_status):
        """Publish plant health assessment"""
        try:
            payload = json.dumps(health_status)
            self.client.publish("plant-iot/analytics/health", payload, qos=1)
            logger.debug(f"Published health status: {payload}")
            return True
            
        except Exception as e:
            logger.error(f"Error publishing health status: {e}")
            return False
    
    def publish_statistics(self, stats):
        """Publish aggregated statistics"""
        try:
            payload = json.dumps(stats)
            self.client.publish("plant-iot/analytics/statistics", payload, qos=1)
            logger.debug(f"Published statistics: {payload}")
            return True
            
        except Exception as e:
            logger.error(f"Error publishing statistics: {e}")
            return False
    
    def __del__(self):
        """Cleanup on deletion"""
        try:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("Publisher disconnected from MQTT broker")
        except:
            pass
