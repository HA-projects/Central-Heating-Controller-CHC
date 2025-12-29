"""Constants for the Central Heating Controller integration."""

DOMAIN = "central_heating_controller"

# Configuration keys
CONF_HVAC_ENTITY = "hvac_entity"
CONF_TRV_ENTITIES = "trv_entities"
CONF_MAX_TEMP = "max_target_temp"
CONF_ROOM_TEMP_SENSOR = "room_temp_sensor"

# Operational Modes (mimicking your Node-Red logic)
MODE_OFF = "off"
MODE_ZONE_TEMP = "target_zone_temp"
MODE_FLOW_TEMP = "target_flow_temp"

# Attributes
ATTR_TOTAL_DEMAND = "total_heating_demand"
ATTR_LAST_CALCULATION = "last_calculation_timestamp"

# Defaults
DEFAULT_MAX_TEMP = 24.0