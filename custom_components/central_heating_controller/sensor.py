from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfTemperature
from .const import DOMAIN, CONF_HVAC_ENTITY, CONF_TRV_ENTITIES


class CHCTargetSensor(SensorEntity):
    """A sensor that calculates the ideal target temp based on house demand."""

    _attr_has_entity_name = True
    _attr_name = "Calculated Target Temperature"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_icon = "mdi:calculator-variant"

    def __init__(self, hass, config_entry):
        self.hass = hass
        self._config = config_entry.data
        self._hvac_entity = self._config.get(CONF_HVAC_ENTITY)
        self._trv_entities = self._config.get(CONF_TRV_ENTITIES)
        self._attr_unique_id = f"{config_entry.entry_id}_target_temp"

        # Internal states for attributes
        self._total_delta = 0.0
        self._attr_native_value = None

    @property
    def extra_state_attributes(self):
        """Attributes to show in the UI, like your screenshot."""
        return {
            "total_demand": self._total_delta,
            "linked_trvs": len(self._trv_entities),
        }

    async def async_added_to_hass(self):
        """Subscribe to TRV and HVAC state changes."""
        from homeassistant.helpers.event import async_track_state_change_event

        # Watch TRVs and the HVAC's internal room sensor
        entities_to_watch = self._trv_entities + [self._hvac_entity]

        self.async_on_remove(
            async_track_state_change_event(
                self.hass, entities_to_watch, self._async_calculate
            )
        )

    async def _async_calculate(self, event=None):
        """The core math logic."""
        total_delta = 0.0

        # 1. Calculate Sum of Delta T
        for trv_id in self._trv_entities:
            state = self.hass.states.get(trv_id)
            if state and state.state not in ["unavailable", "unknown"]:
                curr = state.attributes.get("current_temperature")
                targ = state.attributes.get("temperature")
                # Sum only if heating and there is a positive delta
                if curr and targ and targ > curr and state.state == "heat":
                    total_delta += (targ - curr)

        self._total_delta = round(total_delta, 2)

        # 2. Get the HVAC's current room temperature sensor
        hvac_state = self.hass.states.get(self._hvac_entity)
        if not hvac_state:
            return

        hvac_room_temp = hvac_state.attributes.get("current_temperature")
        if hvac_room_temp is None:
            return

        # 3. Apply your specific Node-Red logic
        if total_delta > 0.9:
            new_target = hvac_room_temp + 1.0
        elif total_delta > 0.5:
            new_target = hvac_room_temp + 0.5
        elif total_delta > 0.0:
            new_target = hvac_room_temp + 0.05
        else:
            new_target = hvac_room_temp - 2.0

        # 4. Update the entity value
        self._attr_native_value = round(new_target, 2)
        self.async_write_ha_state()