from homeassistant.components.climate import ClimateEntity, ClimateEntityFeature, HVACMode
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.components.climate import DOMAIN as CLIMATE_DOMAIN, SERVICE_SET_TEMPERATURE
from homeassistant.const import ATTR_TEMPERATURE, ATTR_ENTITY_ID
import logging

_LOGGER = logging.getLogger(__name__)

class CentralHeatingController(ClimateEntity):
    def __init__(self, hass, config):
        self._hass = hass
        self._hvac_entity = config.get(CONF_HVAC_ENTITY)
        self._trv_entities = config.get(CONF_TRV_ENTITIES)
        self._max_temp = config.get(CONF_MAX_TEMP)

    async def async_added_to_hass(self):
        """Run when entity about to be added to hass."""
        # Subscribe to TRV changes (The Event Listener)
        self.async_on_remove(
            async_track_state_change_event(
                self._hass, self._trv_entities, self._async_calculate_and_update
            )
        )

    # TRV loop that checks any linked TRV for their Delta T
    async def _async_calculate_and_update(self, event):
        """The Math Engine."""
        total_delta = 0.0

        for entity_id in self._trv_entities:
            state = self._hass.states.get(entity_id)
            if state is None or state.state in ["unavailable", "unknown"]:
                continue  # Your safety check

            current_temp = state.attributes.get("current_temperature")
            target_temp = state.attributes.get("temperature")

            if current_temp and target_temp and state.state == HVACMode.HEAT:
                diff = target_temp - current_temp
                if diff > 0:
                    total_delta += diff

        # Now call the service to update the Ecodan
        # Logic: total_delta > 0.9 -> +1.0, etc. (per your Node-Red logic)
        await self._update_ecodan(total_delta)

    # Update Target Temp sensor value:
    async def _async_apply_hvac_update(self, new_target_temp):
        """Send the calculated temperature to the real HVAC device."""

        # 1. Validation: Don't send if the temperature hasn't changed
        # self._current_hvac_target is a variable we store in __init__
        if new_target_temp == self._current_hvac_target:
            return

        # 2. Prepare the service data
        service_data = {
            ATTR_ENTITY_ID: self._hvac_entity,  # The Ecodan ID from your config flow
            ATTR_TEMPERATURE: new_target_temp,
        }

        try:
            # 3. Fire the standard climate service
            await self.hass.services.async_call(
                CLIMATE_DOMAIN,
                SERVICE_SET_TEMPERATURE,
                service_data,
                blocking=True,  # Set to True if you want to wait for confirmation
            )

            # 4. Update internal state tracking
            self._current_hvac_target = new_target_temp
            _LOGGER.info("Updated HVAC %s target to %s°C", self._hvac_entity, new_target_temp)

        except Exception as e:
            _LOGGER.error("Failed to update HVAC: %s", e)