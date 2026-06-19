import logging
import os

import aiohttp
import voluptuous as vol
from homeassistant import config_entries

from .const import ADDON_NAME, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def _fetch_addon_options(hass) -> dict | None:
    """Legge la configurazione dell'add-on tramite la Supervisor API."""
    token = os.environ.get("SUPERVISOR_TOKEN")
    if not token:
        _LOGGER.warning("SUPERVISOR_TOKEN non disponibile — HA non è in modalità supervised?")
        return None

    headers = {"Authorization": f"Bearer {token}"}

    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get("http://supervisor/addons") as resp:
                if resp.status != 200:
                    _LOGGER.error("Supervisor /addons ha risposto %s", resp.status)
                    return None
                body = await resp.json()

            addon_slug = None
            for addon in body.get("data", {}).get("addons", []):
                if addon.get("name") == ADDON_NAME:
                    addon_slug = addon["slug"]
                    break

            if not addon_slug:
                _LOGGER.warning("Add-on '%s' non trovato nella lista Supervisor", ADDON_NAME)
                return None

            async with session.get(f"http://supervisor/addons/{addon_slug}/info") as resp:
                if resp.status != 200:
                    _LOGGER.error("Supervisor /addons/%s/info ha risposto %s", addon_slug, resp.status)
                    return None
                info = await resp.json()

            return info.get("data", {}).get("options")

    except aiohttp.ClientError as exc:
        _LOGGER.error("Errore Supervisor API: %s", exc)
        return None


class MqttPresenceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self):
        self._addon_options: dict | None = None

    async def async_step_user(self, user_input=None):
        if self._async_current_entries():
            return self.async_abort(reason="already_configured")

        if self._addon_options is None:
            self._addon_options = await _fetch_addon_options(self.hass)
            if not self._addon_options:
                return self.async_abort(reason="addon_not_found")

        if user_input is not None:
            opts = self._addon_options
            return self.async_create_entry(
                title="MQTT Presence",
                data={
                    "mqtt_host": opts.get("mqtt_host"),
                    "mqtt_port": opts.get("mqtt_port", 1883),
                    "mqtt_username": opts.get("mqtt_username"),
                    "mqtt_password": opts.get("mqtt_password"),
                    "device_name": opts.get("device_name") or "",
                },
            )

        opts = self._addon_options
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
            description_placeholders={
                "host": str(opts.get("mqtt_host", "?")),
                "port": str(opts.get("mqtt_port", 1883)),
                "device_name": opts.get("device_name") or "(generato automaticamente)",
            },
        )
