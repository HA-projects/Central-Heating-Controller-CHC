"""Sensor platform for Central Heating Controller."""
from __future__ import annotations

import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_state_change_event

from .const import (
    DOMAIN,
    CONF_HVAC_ENTITY,
    CONF_TRV_ENTITIES,
    CONF_MAX_TEMP,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    """Set up the CHC sensor platform from a config entry."""
    # This is the entry point HA was looking for
    async_add_entities([CHCTargetSensor(hass, entry)])


class CHCTargetSensor(SensorEntity):
    """The 'Brain' sensor that calculates the target temperature."""

    _attr_has_entity_name = True
    _attr_name = "Calculated Target"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_icon = "mdi:calculator-variant"

    def __init__(self, hass: HomeAssistant, entry):
        """Initialize the sensor."""
        self.hass = hass
        self._config = entry.data
        self._hvac_entity = self._config.get(CONF_HVAC_ENTITY)
        self._trv_entities = self._config.get(CONF_TRV_ENTITIES)
        self._max_temp = self._config.get(CONF_MAX_TEMP, 24.0)

        # Unique ID allows you to customize the entity via the UI later
        self._attr_unique_id = f"{entry.entry_id}_chc_target"

        # Internal state storage
        self._total_demand = 0.0
        self._attr_native_value = None

    @property
    def extra_state_attributes(self):
        """Return extra state attributes for the dashboard."""
        return {
            "total_demand": self._total_demand,
            "linked_trv_count": len(self._trv_entities),
            "hvac_reference": self._hvac_entity,
        }

    async def async_added_to_hass(self):
        """Register listeners when the sensor is added to HA."""

        @callback
        def _async_on_state_change(_event=None):
            """Handle state changes of watched entities."""
            self.hass.async_create_task(self._async_calculate())

        # Watch all TRVs and the main HVAC unit
        watch_list = self._trv_entities + [self._hvac_entity]

        self.async_on_remove(
            async_track_state_change_event(self.hass, watch_list, _async_on_state_change)
        )

        # Run initial calculation
        await self._async_calculate()

    async def _async_calculate(self):
        """The core math engine."""
        total_delta = 0.0

        # 1. Sum up Delta T from all active TRVs
        for trv_id in self._trv_entities:
            state = self.hass.states.get(trv_id)
            if state and state.state not in ["unavailable", "unknown"]:
                curr = state.attributes.get("current_temperature")
                targ = state.attributes.get("temperature")

                # Check if heating and there's a positive demand
                if curr is not None and targ is not None and targ > curr:
                    total_delta += (targ - curr)

        self._total_demand = round(total_delta, 2)

        # 2. Get reference temperature from HVAC
        hvac_state = self.hass.states.get(self._hvac_entity)
        if not hvac_state or hvac_state.state in ["unavailable", "unknown"]:
            return

        hvac_room_temp = hvac_state.attributes.get("current_temperature")
        if hvac_room_temp is None:
            return

        # 3. Apply your Node-Red logic
        if total_delta > 0.9:
            new_target = hvac_room_temp + 1.0
        elif total_delta > 0.5:
            new_target = hvac_room_temp + 0.5
        elif total_delta > 0.0:
            new_target = hvac_room_temp + 0.1
        else:
            new_target = hvac_room_temp - 2.0

        # 4. Cap and update
        final_target = min(round(new_target, 1), self._max_temp)

        if self._attr_native_value != final_target:
            self._attr_native_value = final_target
            self.async_write_ha_state()

