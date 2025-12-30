"""Central Heating Control integration"""

import asyncio
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the Central Heating Controller from a UI config entry."""
    # This single line tells HA to load your sensor.py
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # This cleans up if you delete or disable the integration
    return await hass.config_entries.async_unload_platforms(entry, ["sensor"])