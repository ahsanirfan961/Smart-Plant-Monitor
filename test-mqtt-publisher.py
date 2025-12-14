import paho.mqtt.client as mqtt
import json
import time
import random

print("Starting MQTT Test Publisher...")

client = mqtt.Client()
try:
    client.connect('localhost', 1883, 60)
    client.loop_start()
    print("Connected to MQTT broker")
    
    for i in range(60):  # Run for 60 iterations (3 minutes at 3 sec intervals)
        data = {
            'temperature': round(20 + random.uniform(-5, 15), 1),
            'humidity': round(50 + random.uniform(-20, 30), 1),
            'soil_moisture': round(40 + random.uniform(-20, 30), 1),
            'light_intensity': round(50 + random.uniform(-30, 50), 1),
            'timestamp': int(time.time() * 1000)
        }
        
        payload = json.dumps(data)
        result = client.publish('plant-iot/sensors/aggregated', payload, qos=1)
        
        if result.rc == 0:
            print(f"✓ Published: temp={data['temperature']}°C, humidity={data['humidity']}%, moisture={data['soil_moisture']}%")
        else:
            print(f"✗ Failed to publish (rc={result.rc})")
        
        time.sleep(3)
    
    client.loop_stop()
    client.disconnect()
    print("Test publisher stopped")
    
except Exception as e:
    print(f"Error: {e}")
