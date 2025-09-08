from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import CONF_NAME, PERCENTAGE, UnitOfVolume
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import *


class VentOptimizationFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow."""

    VERSION = 1

    def __init__(self, *args, **kwargs):
        self._name = DEFAULT_NAME
        self._indoor_temp = None
        self._outdoor_temp = None
        self._indoor_humidity = None
        self._outdoor_humidity = None
        self._window_size = 0.75
        self._room_volume = 30
        self._max_allowed_humidity = 65
        super().__init__(*args, **kwargs)

    async def async_step_user(self, _user_input=None) -> FlowResult:
        if _user_input is not None:
            return self.async_create_entry(title=_user_input[CONF_NAME], data=_user_input)

        humidity_entity_selector = selector.EntitySelector(
            selector.EntitySelectorConfig(device_class=SensorDeviceClass.HUMIDITY)
        )

        temperature_entity_selector = selector.EntitySelector(
            selector.EntitySelectorConfig(device_class=SensorDeviceClass.TEMPERATURE)
        )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_NAME, default=self._name): str,
                vol.Required(CONF_INDOOR_TEMP, default=self._indoor_temp): temperature_entity_selector,
                vol.Required(CONF_OUTDOOR_TEMP, default=self._outdoor_temp): temperature_entity_selector,
                vol.Required(CONF_INDOOR_HUMIDITY, default=self._indoor_humidity): humidity_entity_selector,
                vol.Required(CONF_OUTDOOR_HUMIDITY, default=self._outdoor_humidity): humidity_entity_selector,
                vol.Optional(CONF_WINDOW_SIZE, default=self._window_size): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=0, max=10, step=0.1, unit_of_measurement=UnitOfVolume.CUBIC_METERS)
                ),
                vol.Optional(CONF_ROOM_VOLUME, default=self._room_volume): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=0, max=100, step=0.1, unit_of_measurement=UnitOfVolume.CUBIC_METERS)
                ),
                vol.Optional(CONF_MAX_ALLOWED_HUMIDITY, default=self._max_allowed_humidity): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=1, max=100, step=1, unit_of_measurement=PERCENTAGE)
                ),
            }),
        )


    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        self._existing_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        assert self._existing_entry is not None
        if user_input is None:
            self._name = self._existing_entry.data.get(CONF_NAME, self._indoor_temp)
            self._indoor_temp = self._existing_entry.data.get(CONF_INDOOR_TEMP, self._indoor_temp)
            self._outdoor_temp = self._existing_entry.data.get(CONF_OUTDOOR_TEMP, self._outdoor_temp)
            self._indoor_humidity = self._existing_entry.data.get(CONF_INDOOR_HUMIDITY, self._indoor_humidity)
            self._outdoor_humidity = self._existing_entry.data.get(CONF_OUTDOOR_HUMIDITY, self._outdoor_humidity)
            self._window_size = self._existing_entry.data.get(CONF_WINDOW_SIZE, self._window_size)
            self._room_volume = self._existing_entry.data.get(CONF_ROOM_VOLUME, self._room_volume)
            self._max_allowed_humidity = self._existing_entry.data.get(CONF_MAX_ALLOWED_HUMIDITY, self._max_allowed_humidity)
        return await self.async_step_user(user_input)
