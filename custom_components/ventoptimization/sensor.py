"""Calculates how long one has to vent for a given values."""
from __future__ import annotations

import logging
import math

import voluptuous as vol

from homeassistant import util
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_UNIT_OF_MEASUREMENT,
    CONF_NAME,
    UnitOfTime,
    PERCENTAGE,
    EVENT_HOMEASSISTANT_START,
    STATE_UNKNOWN,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, callback
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.util.unit_conversion import TemperatureConverter
from homeassistant.util.unit_system import METRIC_SYSTEM

from .const import *

_LOGGER = logging.getLogger(__name__)

ATTR_MAXIMUM_HUMIDITY = "maximum_possible_indoor_absolute_humidity"
ATTR_INDOOR_ABSOLUTE_HUMIDITY = "absolute_humidity_inside"
ATTR_OUTDOOR_ABSOLUTE_HUMIDITY = "absolute_humidity_outside"

# Parameters of the model
k_1 = 49.9737675 
k_2 = 2.28452262
k_3 = 49.3679433
k_4 = 8.39747826

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_INDOOR_TEMP): cv.entity_id,
        vol.Required(CONF_OUTDOOR_TEMP): cv.entity_id,
        vol.Required(CONF_INDOOR_HUMIDITY): cv.entity_id,
        vol.Required(CONF_OUTDOOR_HUMIDITY): cv.entity_id,
        vol.Optional(CONF_MAX_ALLOWED_HUMIDITY): vol.Coerce(float),
        vol.Optional(CONF_ROOM_VOLUME): vol.Coerce(float),
        vol.Optional(CONF_WINDOW_SIZE): vol.Coerce(float),
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up Vent time sensor."""
    name = config.get(CONF_NAME, DEFAULT_NAME)
    indoor_temp_sensor = config.get(CONF_INDOOR_TEMP)
    outdoor_temp_sensor = config.get(CONF_OUTDOOR_TEMP)
    indoor_humidity_sensor = config.get(CONF_INDOOR_HUMIDITY)
    outdoor_humidity_sensor = config.get(CONF_OUTDOOR_HUMIDITY)
    max_humidity_allowed = config.get(CONF_MAX_ALLOWED_HUMIDITY)
    window_size = config.get(CONF_WINDOW_SIZE)
    room_volume = config.get(CONF_ROOM_VOLUME)

    async_add_entities([
        VentTime(
            name,
            indoor_temp_sensor,
            outdoor_temp_sensor,
            indoor_humidity_sensor,
            outdoor_humidity_sensor,
            max_humidity_allowed,
            window_size,
            room_volume,
        )])

async def async_setup_entry(
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Vent time sensor through the UI."""
    name = config_entry.data.get(CONF_NAME, DEFAULT_NAME)
    indoor_temp_sensor = config_entry.data.get(CONF_INDOOR_TEMP)
    outdoor_temp_sensor = config_entry.data.get(CONF_OUTDOOR_TEMP)
    indoor_humidity_sensor = config_entry.data.get(CONF_INDOOR_HUMIDITY)
    outdoor_humidity_sensor = config_entry.data.get(CONF_OUTDOOR_HUMIDITY)
    max_humidity_allowed = config_entry.data.get(CONF_MAX_ALLOWED_HUMIDITY)
    window_size = config_entry.data.get(CONF_WINDOW_SIZE)
    room_volume = config_entry.data.get(CONF_ROOM_VOLUME)

    async_add_entities([
        VentTime(
            name,
            indoor_temp_sensor,
            outdoor_temp_sensor,
            indoor_humidity_sensor,
            outdoor_humidity_sensor,
            max_humidity_allowed,
            window_size,
            room_volume,
        )
    ])


class VentTime(SensorEntity):
    """Represents a Vent time sensor."""

    _attr_should_poll = False

    def __init__(
            self,
            name,
            indoor_temp_sensor,
            outdoor_temp_sensor,
            indoor_humidity_sensor,
            outdoor_humidity_sensor,
            max_humidity_allowed,
            window_size,
            room_volume,
    ):
        """Initialize the sensor."""
        self._name = name
        self._state = None
        self._unique_id = str(name).lower()

        self._indoor_temp_sensor = indoor_temp_sensor
        self._indoor_humidity_sensor = indoor_humidity_sensor
        self._outdoor_temp_sensor = outdoor_temp_sensor
        self._outdoor_humidity_sensor = outdoor_humidity_sensor
        self._max_hum_allowed = max_humidity_allowed
        self._window_size = window_size
        self._room_volume = room_volume
        self._available = False
        self._entities = {
            self._indoor_temp_sensor,
            self._indoor_humidity_sensor,
            self._outdoor_temp_sensor,
            self._outdoor_humidity_sensor,
        }

        self._indoor_absolute_humidity = None
        self._outdoor_absolute_humidity = None
        self._indoor_temp = None
        self._outdoor_temp = None
        self._indoor_hum = None
        self._outdoor_hum = None

    async def async_added_to_hass(self) -> None:
        """Register callbacks."""

        @callback
        def vent_time_sensors_state_listener(event):
            """Handle for state changes for dependent sensors."""
            new_state = event.data.get("new_state")
            old_state = event.data.get("old_state")
            entity = event.data.get("entity_id")
            _LOGGER.debug(
                "Sensor state change for %s that had old state %s and new state %s",
                entity,
                old_state,
                new_state,
            )

            if self._update_sensor(entity, old_state, new_state):
                self.async_schedule_update_ha_state(True)

        async_track_state_change_event(
            self.hass, list(self._entities), vent_time_sensors_state_listener
        )

        # Read initial state
        indoor_temp = self.hass.states.get(self._indoor_temp_sensor)
        outdoor_temp = self.hass.states.get(self._outdoor_temp_sensor)
        indoor_hum = self.hass.states.get(self._indoor_humidity_sensor)
        outdoor_hum = self.hass.states.get(self._outdoor_humidity_sensor)

        schedule_update = self._update_sensor(
            self._indoor_temp_sensor, None, indoor_temp
        )

        schedule_update = (
            False
            if not self._update_sensor(
                self._outdoor_temp_sensor, None, outdoor_temp
            )
            else schedule_update
        )

        schedule_update = (
            False
            if not self._update_sensor(
                self._indoor_humidity_sensor, None, indoor_hum
            )
            else schedule_update
        )

        schedule_update = (
            False
            if not self._update_sensor(
                self._outdoor_humidity_sensor, None, outdoor_hum
            )
            else schedule_update
        )

        if schedule_update:
            self.async_schedule_update_ha_state(True)

    def _update_sensor(self, entity, old_state, new_state):
        """Update information based on new sensor states."""
        _LOGGER.debug("Sensor update for %s", entity)
        if new_state is None:
            return False

        # If old_state is not set and new state is unknown then it means
        # that the sensor just started up
        if old_state is None and new_state.state == STATE_UNKNOWN:
            return False

        if entity == self._indoor_temp_sensor:
            self._indoor_temp = VentTime._update_temp_sensor(new_state)
        if entity == self._outdoor_temp_sensor:
            self._outdoor_temp = VentTime._update_temp_sensor(new_state)
        if entity == self._indoor_humidity_sensor:
            self._indoor_hum = VentTime._update_hum_sensor(new_state)
        if entity == self._outdoor_humidity_sensor:
            self._outdoor_hum = VentTime._update_hum_sensor(new_state)

        return True

    @staticmethod
    def _update_temp_sensor(state):
        """Parse temperature sensor value."""
        _LOGGER.debug("Updating temp sensor with value %s", state.state)

        # Return an error if the sensor change its state to Unknown.
        if state.state == STATE_UNKNOWN:
            _LOGGER.debug(
                "Unable to parse temperature sensor %s with state: %s",
                state.entity_id,
                state.state,
            )
            return None

        unit = state.attributes.get(ATTR_UNIT_OF_MEASUREMENT)

        if (temp := util.convert(state.state, float)) is None:
            _LOGGER.debug(
                "Unable to parse temperature sensor %s with state: %s",
                state.entity_id,
                state.state,
            )
            return None

        # convert to celsius if necessary
        if unit == UnitOfTemperature.FAHRENHEIT:
            return TemperatureConverter.convert(
                temp, UnitOfTemperature.FAHRENHEIT, UnitOfTemperature.CELSIUS
            )
        if unit == UnitOfTemperature.CELSIUS:
            return temp
        _LOGGER.error(
            "Temp sensor %s has unsupported unit: %s (allowed: %s, %s)",
            state.entity_id,
            unit,
            UnitOfTemperature.CELSIUS,
            UnitOfTemperature.FAHRENHEIT,
        )

        return None

    @staticmethod
    def _update_hum_sensor(state):
        """Parse humidity sensor value."""
        _LOGGER.debug("Updating humidity sensor with value %s", state.state)

        # Return an error if the sensor change its state to Unknown.
        if state.state == STATE_UNKNOWN:
            _LOGGER.debug(
                "Unable to parse humidity sensor %s, state: %s",
                state.entity_id,
                state.state,
            )
            return None

        if (hum := util.convert(state.state, float)) is None:
            _LOGGER.debug(
                "Unable to parse humidity sensor %s, state: %s",
                state.entity_id,
                state.state,
            )
            return None

        if (unit := state.attributes.get(ATTR_UNIT_OF_MEASUREMENT)) != PERCENTAGE:
            _LOGGER.error(
                "Humidity sensor %s has unsupported unit: %s %s",
                state.entity_id,
                unit,
                " (allowed: %)",
            )
            return None

        if hum > 100 or hum < 0:
            _LOGGER.error(
                "Humidity sensor %s is out of range: %s %s",
                state.entity_id,
                hum,
                "(allowed: 0-100%)",
            )
            return None

        return hum

    async def async_update(self) -> None:
        """Calculate latest state."""
        _LOGGER.debug("Update state for %s", self.entity_id)
        # check all sensors
        if None in (self._indoor_temp, self._indoor_hum, self._outdoor_temp, self._outdoor_hum):
            self._available = False
            self._outdoor_absolute_humidity = None
            self._indoor_absolute_humidity = None
            return

        # re-calculate e_s and vent time
        self._calc_indoor_absolute_humidity()
        self._calc_outdoor_absolute_humidity()
        self._calc_time_to_vent()
        if self._state is None:
            self._available = False
            self._outdoor_absolute_humidity = None
            self._indoor_absolute_humidity = None
        else:
            self._available = True

    def _calc_e_s(self, temp):
        """Calculate the maximum possible absolute humidity for the indoor temperature"""
        # According to https://journals.ametsoc.org/view/journals/bams/86/2/bams-86-2-225.xml?tab_body=pdf Equation 6 p.226
        C_1 = 610.94 # Kp
        A_1 = 17.625
        B_1 = 243.04 # °C
        return C_1*math.exp((A_1*temp)/(B_1+temp))

    def _calc_indoor_absolute_humidity(self):
        self._indoor_absolute_humidity = (self._indoor_hum/100)*self._calc_e_s(self._indoor_temp)
        _LOGGER.debug("Indoor absolute humidity: %f", self._indoor_absolute_humidity)
    
    def _calc_outdoor_absolute_humidity(self):
        self._outdoor_absolute_humidity = (self._outdoor_hum/100)*self._calc_e_s(self._outdoor_temp)
        _LOGGER.debug("Outdoor absolute humidity: %f", self._outdoor_absolute_humidity)

    def _humidity_model(self, time):
        return (self._indoor_absolute_humidity - self._outdoor_absolute_humidity)/((time+1)**((k_1*self._window_size)/(k_2*self._room_volume))) + self._outdoor_absolute_humidity

    def _temperature_model(self, time):
        return (self._indoor_temp - self._outdoor_temp)/((time+1)**((k_3*self._window_size)/(k_4*self._room_volume))) + self._outdoor_temp

    def _calc_time_to_vent(self):
        """Calculate the time until the humidity is under max_allowed_hum"""

        if self._indoor_absolute_humidity <= self._outdoor_absolute_humidity:
            _LOGGER.debug("Venting has no point, the outside is to humid")
            self._state = 0
        else:
            # One could use a binary search here, but it is unecessary
            for i in range(301):
                if (self._humidity_model(i)/self._calc_e_s(self._temperature_model(i)))*100 <= self._max_hum_allowed:
                    self._state = i
                    break
            else:
                self._state = 300
                _LOGGER.debug("Venting would take longer than 5h")


        _LOGGER.debug("You have to vent %s minutes", self._state)

    @property
    def name(self):
        """Return the name."""
        return self._name

    @property
    def unique_id(self) -> str:
        return self._unique_id

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return UnitOfTime.MINUTES

    @property
    def native_value(self):
        """Return the state of the entity."""
        return self._state

    @property
    def available(self):
        """Return the availability of this sensor."""
        return self._available

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            ATTR_INDOOR_ABSOLUTE_HUMIDITY: round(self._indoor_absolute_humidity, 2),
            ATTR_OUTDOOR_ABSOLUTE_HUMIDITY: round(self._outdoor_absolute_humidity, 2)
        }
