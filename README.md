# MQTT Presence Reporter — Home Assistant Add-on

A lightweight Home Assistant add-on that announces the online/offline status of your Home Assistant instance to an external MQTT broker.

## How it works

When the add-on starts, it connects to the configured MQTT broker and immediately publishes an `online` message to the topic:

```
homeassistant/<device_name>/status
```

It also registers an MQTT **last-will** message so the broker automatically publishes `offline` on that same topic if the connection is ever lost unexpectedly.

Both messages are sent with the **retain** flag, so any subscriber that connects later will immediately see the current status.

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

### Example

```yaml
device_name: "home-assistant"
mqtt_host: "192.168.1.10"
mqtt_port: 1883
mqtt_username: "mqttuser"
mqtt_password: "secret"
```

With this configuration the add-on publishes to:

```
homeassistant/home-assistant/status  →  "online" / "offline"
```

## MQTT topics

| Topic | Value | When |
|---|---|---|
| `homeassistant/<device_name>/status` | `online` | Add-on starts and connects successfully |
| `homeassistant/<device_name>/status` | `offline` | Connection is lost (last-will) |

## Supported architectures

`amd64` · `aarch64` · `armv7` · `armhf`

## Requirements

- An external MQTT broker reachable from your Home Assistant instance (e.g. Mosquitto running on a NAS, a VPS, or another machine).
- This add-on does **not** depend on the Home Assistant internal MQTT integration — it talks directly to the broker.
