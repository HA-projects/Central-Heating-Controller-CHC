import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector
from .const import DOMAIN, CONF_HVAC_ENTITY, CONF_TRV_ENTITIES, CONF_MAX_TEMP, DEFAULT_MAX_TEMP

class CHCConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for CHC."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step where the user selects entities."""
        if user_input is not None:
            return self.async_create_entry(title="Heating Zone Controller", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HVAC_ENTITY): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="climate")
                ),
                vol.Required(CONF_TRV_ENTITIES): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="climate", multiple=True)
                ),
                vol.Optional(CONF_MAX_TEMP, default=DEFAULT_MAX_TEMP): vol.Coerce(float),
            })
        )