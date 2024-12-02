"""Predicts how long you have to vent given temperature and humidity from inside and outside"""

from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """
    Set up this integration using the UI.

    This function is called by Home Assistant when the integration is set up with the UI.
    """
    # Forward entry setup for the sensor platform
    await entry.async_create_task(await hass.config_entries.async_forward_entry_setups(entry, SENSOR_DOMAIN))

    # Add an update listener for this entry
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(_hass: HomeAssistant, _entry: ConfigEntry) -> bool:
    """
    Handle removal of an entry.

    This function is called by Home Assistant when the integration is being removed.
    """
    return await _hass.config_entries.async_forward_entry_unload(_entry, SENSOR_DOMAIN)


async def async_reload_entry(_hass: HomeAssistant, _entry: ConfigEntry) -> None:
    """
    Reload config entry.

    This function is called by Home Assistant when the integration configuration is updated.
    """
    # Unload the entry and its dependent components
    await async_unload_entry(_hass, _entry)

    # Set up the entry again
    await async_setup_entry(_hass, _entry)
