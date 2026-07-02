# MQTT Presence Reporter — Home Assistant Add-on

A lightweight Home Assistant add-on that announces the online/offline status of your Home Assistant instance to an external MQTT broker.

## How it works

When the add-on starts, it connects to the configured MQTT broker and immediately publishes an `online` message to the topic:

```
homeassistant/<device_name>/status
```

It also registers an MQTT **last-will** message so the broker automatically publishes `offline` on that same topic if the connection is ever lost unexpectedly.

Both messages are sent with the **retain** flag, so any subscriber that connects later will immediately see the current status. The payload is a JSON object containing the status and (if configured) the Telegram chat ID to notify, e.g. `{"status": "offline", "telegram_chat_id": "123456789"}` — this lets a monitoring server tell which Telegram chat to alert without any extra configuration on its side.

## Installation

1. In Home Assistant, go to **Settings → Add-ons → Add-on Store**.
2. Click the three-dot menu (top right) and choose **Repositories**.
3. Add the following URL:
   ```
   https://github.com/hetanfc/mqtt-presence-addon
   ```
4. Find **MQTT Presence Reporter** in the store and click **Install**.

## Configuration

| Option | Required | Default | Description |
|---|---|---|---|
| `device_name` | No | auto-generated | Name used in the MQTT topic. If left empty, a random name like `ha123` is generated. |
| `mqtt_host` | Yes | — | Hostname or IP address of the MQTT broker. |
| `mqtt_port` | Yes | `1883` | Port of the MQTT broker. |
| `mqtt_username` | Yes | — | Username for broker authentication. |
| `mqtt_password` | Yes | — | Password for broker authentication. |
| `telegram_chat_id` | No | empty | Telegram chat ID that a monitoring server should notify when this device goes offline/online. Included in the status payload; ignored if left empty. |

### Example

```yaml
device_name: "home-assistant"
mqtt_host: "192.168.1.10"
mqtt_port: 1883
mqtt_username: "mqttuser"
mqtt_password: "secret"
telegram_chat_id: "123456789"
```

With this configuration the add-on publishes to:

```
homeassistant/home-assistant/status  →  {"status": "online", "telegram_chat_id": "123456789"}
```

## MQTT topics

| Topic | Value | When |
|---|---|---|
| `homeassistant/<device_name>/status` | `{"status": "online", "telegram_chat_id": "..."}` | Add-on starts and connects successfully |
| `homeassistant/<device_name>/status` | `{"status": "offline", "telegram_chat_id": "..."}` | Connection is lost (last-will) |

## Supported architectures

`amd64` · `aarch64` · `armv7` · `armhf`

## Requirements

- An external MQTT broker reachable from your Home Assistant instance (e.g. Mosquitto running on a NAS, a VPS, or another machine).
- This add-on does **not** depend on the Home Assistant internal MQTT integration — it talks directly to the broker.
