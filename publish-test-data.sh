#!/bin/bash
# Continuous test data publisher
while true; do
  TEMP=$(( RANDOM % 40 + 10 ))
  HUMID=$(( RANDOM % 30 + 50 ))
  MOIST=$(( RANDOM % 50 + 30 ))
  LIGHT=$(( RANDOM % 100 ))
  
  JSON="{\"temperature\": $TEMP, \"humidity\": $HUMID, \"soil_moisture\": $MOIST, \"light_intensity\": $LIGHT, \"timestamp\": $(date +%s000)}"
  
  mosquitto_pub -h mosquitto -t "plant-iot/sensors/aggregated" -m "$JSON"
  echo "Published: $JSON"
  sleep 3
done
