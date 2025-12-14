"""
Actuator Control Service - Main Entry Point
Subscribes to control commands and manages actuators
"""

import json
import logging
import os
import time
from datetime import datetime
import paho.mqtt.client as mqtt
from control_logic import ControlLogic
from safety import SafetyManager

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
MQTT_BROKER = os.getenv('MQTT_BROKER', 'localhost')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
AUTO_CONTROL = os.getenv('AUTO_CONTROL', 'true').lower() == 'true'

# Global state
current_sensor_data = {}
actuator_status = {
    'pump': {'status': 'OFF', 'last_command': None, 'duration': 0},
    'fan': {'status': 'OFF', 'last_command': None, 'duration': 0},
    'grow_light': {'status': 'OFF', 'last_command': None, 'duration': 0}
}

client = mqtt.Client()
control_logic = ControlLogic()
safety_manager = SafetyManager()


def on_connect(client, userdata, flags, rc):
    """MQTT connection callback"""
    if rc == 0:
        logger.info(f"Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
        # Subscribe to command topics
        client.subscribe("plant-iot/actuators/pump")
        client.subscribe("plant-iot/actuators/fan")
        client.subscribe("plant-iot/actuators/grow-light")
        client.subscribe("plant-iot/control/all")
        # Also subscribe to sensor data for auto-control
        client.subscribe("plant-iot/sensors/aggregated")
    else:
        logger.error(f"Failed to connect, return code {rc}")


def on_message(client, userdata, msg):
    """MQTT message callback"""
    try:
        topic = msg.topic
        payload = json.loads(msg.payload.decode('utf-8'))
        
        logger.debug(f"Received on {topic}: {payload}")
        
        # Handle sensor data (for auto-control)
        if topic == "plant-iot/sensors/aggregated":
            current_sensor_data.update({
                'temperature': payload.get('temperature'),
                'humidity': payload.get('humidity'),
                'soil_moisture': payload.get('soil_moisture_percent', payload.get('soil_moisture')),
                'light_intensity': payload.get('light_percent', payload.get('light_intensity'))
            })
            
            # Perform auto-control if enabled
            if AUTO_CONTROL:
                perform_auto_control()
        
        # Handle actuator commands
        elif topic == "plant-iot/actuators/pump":
            handle_pump_command(payload)
        elif topic == "plant-iot/actuators/fan":
            handle_fan_command(payload)
        elif topic == "plant-iot/actuators/grow-light":
            handle_light_command(payload)
        elif topic == "plant-iot/control/all":
            handle_global_control(payload)
            
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from {msg.topic}: {e}")
    except Exception as e:
        logger.error(f"Error processing message: {e}")


def handle_pump_command(payload):
    """Handle water pump control command"""
    try:
        action = payload.get('action', '').upper()
        duration = payload.get('duration', 0)
        
        # Validate
        if not safety_manager.validate_command('pump', action, duration):
            logger.warning(f"Invalid pump command: {payload}")
            return
        
        if action == 'ON':
            control_logic.activate_pump(duration)
            actuator_status['pump'] = {
                'status': 'ON',
                'last_command': int(time.time() * 1000),
                'duration': duration
            }
            logger.info(f"Pump turned ON (duration: {duration}s)")
        elif action == 'OFF':
            control_logic.deactivate_pump()
            actuator_status['pump'] = {
                'status': 'OFF',
                'last_command': int(time.time() * 1000),
                'duration': 0
            }
            logger.info("Pump turned OFF")
        
        publish_status('pump')
        
    except Exception as e:
        logger.error(f"Error handling pump command: {e}")


def handle_fan_command(payload):
    """Handle fan control command"""
    try:
        action = payload.get('action', '').upper()
        duration = payload.get('duration', 0)
        
        if not safety_manager.validate_command('fan', action, duration):
            logger.warning(f"Invalid fan command: {payload}")
            return
        
        if action == 'ON':
            control_logic.activate_fan(duration)
            actuator_status['fan'] = {
                'status': 'ON',
                'last_command': int(time.time() * 1000),
                'duration': duration
            }
            logger.info(f"Fan turned ON (duration: {duration}s)")
        elif action == 'OFF':
            control_logic.deactivate_fan()
            actuator_status['fan'] = {
                'status': 'OFF',
                'last_command': int(time.time() * 1000),
                'duration': 0
            }
            logger.info("Fan turned OFF")
        
        publish_status('fan')
        
    except Exception as e:
        logger.error(f"Error handling fan command: {e}")


def handle_light_command(payload):
    """Handle grow light control command"""
    try:
        action = payload.get('action', '').upper()
        duration = payload.get('duration', 0)
        
        if not safety_manager.validate_command('grow_light', action, duration):
            logger.warning(f"Invalid light command: {payload}")
            return
        
        if action == 'ON':
            # Check safety interlocks
            if current_sensor_data.get('temperature', 0) > 40:
                logger.warning("Cannot activate grow light: Temperature too high")
                return
            
            control_logic.activate_light(duration)
            actuator_status['grow_light'] = {
                'status': 'ON',
                'last_command': int(time.time() * 1000),
                'duration': duration
            }
            logger.info(f"Grow light turned ON (duration: {duration}s)")
        elif action == 'OFF':
            control_logic.deactivate_light()
            actuator_status['grow_light'] = {
                'status': 'OFF',
                'last_command': int(time.time() * 1000),
                'duration': 0
            }
            logger.info("Grow light turned OFF")
        
        publish_status('grow_light')
        
    except Exception as e:
        logger.error(f"Error handling light command: {e}")


def handle_global_control(payload):
    """Handle global emergency control"""
    try:
        enable = payload.get('enable', False)
        
        if enable:
            logger.info("Emergency stop - turning off all actuators")
            control_logic.deactivate_all()
            actuator_status['pump']['status'] = 'OFF'
            actuator_status['fan']['status'] = 'OFF'
            actuator_status['grow_light']['status'] = 'OFF'
        else:
            logger.info("All actuators disabled")
        
        publish_all_status()
        
    except Exception as e:
        logger.error(f"Error handling global control: {e}")


def perform_auto_control():
    """Implement automatic control based on sensor data"""
    try:
        temp = current_sensor_data.get('temperature')
        moisture = current_sensor_data.get('soil_moisture')
        light = current_sensor_data.get('light_intensity')
        
        # Auto-control water pump based on soil moisture
        if moisture is not None:
            if moisture < 30 and actuator_status['pump']['status'] == 'OFF':
                logger.info("Auto: Soil dry, activating pump")
                control_logic.activate_pump(duration=300)  # 5 minutes
                actuator_status['pump'] = {
                    'status': 'ON',
                    'last_command': int(time.time() * 1000),
                    'duration': 300
                }
                publish_status('pump')
            elif moisture > 70 and actuator_status['pump']['status'] == 'ON':
                logger.info("Auto: Soil moist enough, deactivating pump")
                control_logic.deactivate_pump()
                actuator_status['pump']['status'] = 'OFF'
                publish_status('pump')
        
        # Auto-control fan based on temperature
        if temp is not None:
            if temp > 30 and actuator_status['fan']['status'] == 'OFF':
                logger.info("Auto: High temperature, activating fan")
                control_logic.activate_fan()
                actuator_status['fan']['status'] = 'ON'
                publish_status('fan')
            elif temp < 25 and actuator_status['fan']['status'] == 'ON':
                logger.info("Auto: Temperature normal, deactivating fan")
                control_logic.deactivate_fan()
                actuator_status['fan']['status'] = 'OFF'
                publish_status('fan')
        
        # Auto-control light based on light intensity
        if light is not None:
            if light < 20 and actuator_status['grow_light']['status'] == 'OFF':
                logger.info("Auto: Low light, activating grow light")
                control_logic.activate_light()
                actuator_status['grow_light']['status'] = 'ON'
                publish_status('grow_light')
            elif light > 60 and actuator_status['grow_light']['status'] == 'ON':
                logger.info("Auto: Sufficient light, deactivating grow light")
                control_logic.deactivate_light()
                actuator_status['grow_light']['status'] = 'OFF'
                publish_status('grow_light')
        
    except Exception as e:
        logger.error(f"Error in auto-control: {e}")


def publish_status(actuator):
    """Publish status of a specific actuator"""
    try:
        if actuator in actuator_status:
            payload = json.dumps(actuator_status[actuator])
            client.publish(f"plant-iot/status/{actuator}", payload, qos=1)
    except Exception as e:
        logger.error(f"Error publishing status for {actuator}: {e}")


def publish_all_status():
    """Publish status of all actuators"""
    try:
        payload = json.dumps(actuator_status)
        client.publish("plant-iot/status/all", payload, qos=1)
    except Exception as e:
        logger.error(f"Error publishing all status: {e}")


def on_disconnect(client, userdata, rc):
    """MQTT disconnection callback"""
    if rc != 0:
        logger.warning(f"Unexpected disconnection (code {rc})")
    else:
        logger.info("Cleanly disconnected from MQTT broker")


def main():
    """Main entry point"""
    logger.info("Starting Actuator Control Service...")
    logger.info(f"Auto-control enabled: {AUTO_CONTROL}")
    
    # Set up MQTT client
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        client.loop_start()
        
        logger.info("MQTT client started, waiting for commands...")
        
        while True:
            time.sleep(1)
            
    except ConnectionRefusedError:
        logger.error(f"Failed to connect to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
        raise
    except KeyboardInterrupt:
        logger.info("Shutting down Actuator Control Service...")
        control_logic.deactivate_all()
        client.loop_stop()
        client.disconnect()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise


if __name__ == "__main__":
    main()
