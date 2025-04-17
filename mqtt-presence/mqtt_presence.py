import os
import time
import random
import string
from paho.mqtt import client as mqtt_client

mqtt_host = os.getenv("MQTT_HOST")
mqtt_port = int(os.getenv("MQTT_PORT", "1883"))
mqtt_username = os.getenv("MQTT_USERNAME")
mqtt_password = os.getenv("MQTT_PASSWORD")
device_name = os.getenv("DEVICE_NAME")

if not device_name:
    device_name = "ha" + str(random.randint(100, 999))

topic = f"homeassistant/{device_name}/status"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[{device_name}] Connesso al broker MQTT")
        client.publish(topic, "online", qos=0, retain=True)
    else:
        print(f"[{device_name}] Connessione fallita: codice {rc}")

def main():
    client_id = f"ha-{device_name}-{random.randint(0,9999)}"
    client = mqtt_client.Client(client_id=client_id, clean_session=True)
    client.username_pw_set(mqtt_username, mqtt_password)

    # Set will
    client.will_set(topic, payload="offline", qos=0, retain=True)
    client.on_connect = on_connect

    client.connect(mqtt_host, mqtt_port, keepalive=60)
    client.loop_start()

    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        print("Uscita volontaria")

if __name__ == "__main__":
    main()
