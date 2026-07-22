"""Constants for the Jeedom API prototype."""
from datetime import timedelta

DOMAIN = "jeedom_api"
PLATFORMS = ["light", "switch", "cover", "button", "sensor", "binary_sensor"]

CONF_API_KEY = "api_key"
CONF_SELECTED_EQUIPMENT = "selected_equipment"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_SCAN_INTERVAL = 10
MIN_SCAN_INTERVAL = 5
MAX_SCAN_INTERVAL = 300

DEFAULT_TIMEOUT = 15
DEFAULT_UPDATE_INTERVAL = timedelta(seconds=DEFAULT_SCAN_INTERVAL)

CONF_AUTO_DISCOVER = "auto_discover_new_commands"
DEFAULT_AUTO_DISCOVER = True
