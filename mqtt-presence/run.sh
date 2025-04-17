#!/usr/bin/env bash

# Legge i parametri dal file options.json (generato da HA)
export DEVICE_NAME=$(jq -r '.device_name' /data/options.json)
export MQTT_HOST=$(jq -r '.mqtt_host' /data/options.json)
export MQTT_PORT=$(jq -r '.mqtt_port' /data/options.json)
export MQTT_USERNAME=$(jq -r '.mqtt_username' /data/options.json)
export MQTT_PASSWORD=$(jq -r '.mqtt_password' /data/options.json)

echo "💡 Avvio con DEVICE_NAME=$DEVICE_NAME su $MQTT_HOST:$MQTT_PORT"

python3 /app/mqtt_presence.py