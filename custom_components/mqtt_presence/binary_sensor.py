import logging
import random

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = entry.data
    device_name = data.get("device_name") or f"ha{random.randint(100, 999)}"

    sensor = MqttBrokerSensor(
        hass=hass,
        host=data["mqtt_host"],
        port=data["mqtt_port"],
        username=data["mqtt_username"],
        password=data["mqtt_password"],
        device_name=device_name,
    )
    async_add_entities([sensor])
    hass.async_create_task(hass.async_add_executor_job(sensor.start_mqtt))


class MqttBrokerSensor(BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_name = "Broker MQTT esterno"
    _attr_should_poll = False

    def __init__(self, hass, host, port, username, password, device_name):
        self.hass = hass
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._device_name = device_name
        self._client = None
        self._attr_is_on = False
        self._attr_unique_id = f"mqtt_presence_{device_name}"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device_name)},
            "name": "MQTT Presence",
            "manufacturer": "hetanfc",
            "model": "MQTT Presence Reporter",
        }

    def start_mqtt(self) -> None:
        """Avvia la connessione MQTT (chiamata in un thread executor)."""
        from paho.mqtt import client as mqtt_client

        try:
            from paho.mqtt.client import CallbackAPIVersion
            client = mqtt_client.Client(
                callback_api_version=CallbackAPIVersion.VERSION1,
                client_id=f"ha-presence-sensor-{random.randint(0, 9999)}",
                clean_session=True,
            )
        except ImportError:
            # paho-mqtt < 2.0
            client = mqtt_client.Client(
                client_id=f"ha-presence-sensor-{random.randint(0, 9999)}",
                clean_session=True,
            )

        client.username_pw_set(self._username, self._password)
        client.on_connect = self._on_connect
        client.on_disconnect = self._on_disconnect
        self._client = client

        try:
            client.connect(self._host, self._port, keepalive=60)
            client.loop_start()
        except Exception as exc:
            _LOGGER.error(
                "Impossibile connettersi al broker %s:%s — %s",
                self._host, self._port, exc,
            )

    def _on_connect(self, client, userdata, flags, rc):
        self._attr_is_on = rc == 0
        if rc == 0:
            _LOGGER.debug("Connesso al broker esterno %s:%s", self._host, self._port)
        else:
            _LOGGER.warning("Connessione al broker fallita: rc=%s", rc)
        self.hass.loop.call_soon_threadsafe(self.async_write_ha_state)

    def _on_disconnect(self, client, userdata, rc):
        self._attr_is_on = False
        _LOGGER.debug("Disconnesso dal broker esterno (rc=%s)", rc)
        self.hass.loop.call_soon_threadsafe(self.async_write_ha_state)

    async def async_will_remove_from_hass(self) -> None:
        if self._client:
            await self.hass.async_add_executor_job(self._stop_mqtt)

    def _stop_mqtt(self) -> None:
        if self._client:
            self._client.disconnect()
            self._client.loop_stop()
