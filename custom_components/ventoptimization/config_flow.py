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
                vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                vol.Required(CONF_INDOOR_TEMP): temperature_entity_selector,
                vol.Required(CONF_OUTDOOR_TEMP): temperature_entity_selector,
                vol.Required(CONF_INDOOR_HUMIDITY): humidity_entity_selector,
                vol.Required(CONF_OUTDOOR_HUMIDITY): humidity_entity_selector,
                vol.Optional(CONF_WINDOW_SIZE, default=0.75): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=0, max=10, step=0.1, unit_of_measurement=UnitOfVolume.CUBIC_METERS)
                ),
                vol.Optional(CONF_ROOM_VOLUME, default=30): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=0, max=100, step=0.1, unit_of_measurement=UnitOfVolume.CUBIC_METERS)
                ),
                vol.Optional(CONF_MAX_ALLOWED_HUMIDITY, default=65): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=1, max=100, step=1, unit_of_measurement=PERCENTAGE)
                ),
            }),
        )
