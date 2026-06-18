import os
import time
import random
import signal
import sys
from paho.mqtt import client as mqtt_client

mqtt_host = os.getenv("MQTT_HOST")
mqtt_port = int(os.getenv("MQTT_PORT", "1883"))
mqtt_username = os.getenv("MQTT_USERNAME")
mqtt_password = os.getenv("MQTT_PASSWORD")
device_name = os.getenv("DEVICE_NAME")

if not device_name:
    device_name = "ha" + str(random.randint(100, 999))

topic = f"homeassistant/{device_name}/status"
client = None

def on_connect(c, userdata, flags, rc):
    if rc == 0:
        print(f"[{device_name}] Connesso al broker MQTT")
        c.publish(topic, "online", qos=0, retain=True)
    else:
        print(f"[{device_name}] Connessione fallita: codice {rc}")

def on_disconnect(c, userdata, rc):
    if rc != 0:
        print(f"[{device_name}] Disconnessione inattesa: codice {rc}")

def shutdown(sig, frame):
    print(f"[{device_name}] Fermata richiesta, pubblicazione offline...")
    if client:
        client.publish(topic, "offline", qos=0, retain=True)
        client.disconnect()
        client.loop_stop()
    sys.exit(0)

def main():
    global client
    client_id = f"ha-{device_name}-{random.randint(0,9999)}"
    client = mqtt_client.Client(client_id=client_id, clean_session=True)
    client.username_pw_set(mqtt_username, mqtt_password)
    client.will_set(topic, payload="offline", qos=0, retain=True)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    client.connect(mqtt_host, mqtt_port, keepalive=60)
    client.loop_start()

    while True:
        time.sleep(3600)

if __name__ == "__main__":
    main()