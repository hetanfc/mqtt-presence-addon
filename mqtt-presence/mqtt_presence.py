import os
import time
import random
import string
import json
import requests
from paho.mqtt import client as mqtt_client

# Configurazione MQTT
mqtt_host = os.getenv("MQTT_HOST")
mqtt_port = int(os.getenv("MQTT_PORT", "1883"))
mqtt_username = os.getenv("MQTT_USERNAME")
mqtt_password = os.getenv("MQTT_PASSWORD")
device_name = os.getenv("DEVICE_NAME")

if not device_name:
    device_name = "ha" + str(random.randint(100, 999))

# Configurazione Home Assistant API
SUPERVISOR_TOKEN = os.environ.get('SUPERVISOR_TOKEN')
headers = {
    "Authorization": f"Bearer {SUPERVISOR_TOKEN}",
    "Content-Type": "application/json"
}

def update_ha_state(state):
    """Aggiorna lo stato del sensore in Home Assistant"""
    try:
        payload = {
            "state": state,
            "attributes": {
                "friendly_name": f"Connessione {device_name}",
                "device_class": "connectivity"
            }
        }
        response = requests.post(
            "http://supervisor/core/api/states/binary_sensor.mqtt_presence_connection",
            headers=headers,
            json=payload
        )
        if response.status_code == 200:
            print(f"Stato Home Assistant aggiornato: {state}")
        else:
            print(f"Errore nell'aggiornamento dello stato: {response.status_code}")
    except Exception as e:
        print(f"Errore nella comunicazione con Home Assistant: {e}")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[{device_name}] Connesso al broker MQTT")
        client.publish(f"home-assistant/status/{device_name}", "online", qos=1, retain=True)
        update_ha_state("on")
    else:
        print(f"[{device_name}] Connessione fallita: codice {rc}")
        update_ha_state("off")

def on_disconnect(client, userdata, rc):
    print(f"[{device_name}] Disconnesso dal broker MQTT")
    update_ha_state("off")

def main():
    # Crea il sensore in Home Assistant
    update_ha_state("off")  # Stato iniziale

    client_id = f"ha-{device_name}-{random.randint(0,9999)}"
    client = mqtt_client.Client(client_id=client_id, clean_session=True)
    client.username_pw_set(mqtt_username, mqtt_password)

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    # Imposta il will message per il broker esterno
    client.will_set(f"home-assistant/status/{device_name}", payload="offline", qos=1, retain=True)

    try:
        client.connect(mqtt_host, mqtt_port, keepalive=60)
        client.loop_start()

        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("Uscita volontaria")
        update_ha_state("off")
        client.disconnect()
    except Exception as e:
        print(f"Errore: {e}")
        update_ha_state("off")

if __name__ == "__main__":
    main()
