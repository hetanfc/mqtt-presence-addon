#!/usr/bin/env bash

# Legge i parametri dal file options.json (generato da HA)
export DEVICE_NAME=$(jq -r '.device_name' /data/options.json)
export MQTT_HOST=$(jq -r '.mqtt_host' /data/options.json)
export MQTT_PORT=$(jq -r '.mqtt_port' /data/options.json)
export MQTT_USERNAME=$(jq -r '.mqtt_username' /data/options.json)
export MQTT_PASSWORD=$(jq -r '.mqtt_password' /data/options.json)

# Installa l'integrazione custom in /config/custom_components/ se non è già aggiornata
INTEGRATION_DST="/config/custom_components/mqtt_presence"
INTEGRATION_SRC="/app/integration"
MANIFEST_SRC="$INTEGRATION_SRC/manifest.json"
MANIFEST_DST="$INTEGRATION_DST/manifest.json"

BUNDLED_VERSION=$(jq -r '.version' "$MANIFEST_SRC")
INSTALLED_VERSION=$(jq -r '.version' "$MANIFEST_DST" 2>/dev/null || echo "none")

if [ "$BUNDLED_VERSION" != "$INSTALLED_VERSION" ]; then
    echo "Installo integrazione mqtt_presence v$BUNDLED_VERSION in $INTEGRATION_DST"
    mkdir -p "$INTEGRATION_DST"
    cp -r "$INTEGRATION_SRC"/. "$INTEGRATION_DST/"
else
    echo "Integrazione mqtt_presence già aggiornata (v$INSTALLED_VERSION)"
fi

echo "Avvio con DEVICE_NAME=$DEVICE_NAME su $MQTT_HOST:$MQTT_PORT"

python3 /app/mqtt_presence.py