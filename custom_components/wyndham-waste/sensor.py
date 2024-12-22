import logging
from datetime import timedelta
import requests
import re
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

# Constants
BASE_URL = "https://digital.wyndham.vic.gov.au/myWyndham/init-map-data.asp"
PATTERNS = {
    "garbage": r"Next Garbage Collection:\s*(.*?)\s*</div>",
    "green_waste": r"Next Green Waste Collection:\s*(.*?)\s*</div>",
    "recycling": r"Next Recycling Collection:\s*(.*?)\s*</div>",
    "week": r"Waste Collection Week:\s*(\d+)",
}
UPDATE_INTERVAL = timedelta(hours=12)  # Update every 12 hours

_LOGGER = logging.getLogger(__name__)

def fetch_waste_info(propnum):
    """Fetch waste collection data from the Wyndham API."""
    params = {
        "propnum": propnum,
        "radius": "3000",
        "mapfeatures": "",
    }
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
    except requests.RequestException as e:
        _LOGGER.error("Error fetching waste info: %s", e)
        return None

    _LOGGER.debug("Raw response: %s", response.text)
    data = {}
    for key, pattern in PATTERNS.items():
        match = re.search(pattern, response.text)
        if match:
            data[key] = match.group(1)
    _LOGGER.debug("Parsed waste data: %s", data)
    return data

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Wyndham Waste sensors."""
    _LOGGER.debug("Setting up Wyndham Waste platform...")
    propnum = config.get("propnum")
    if not propnum:
        _LOGGER.error("Property number (propnum) is required.")
        return

    waste_data = WasteData(propnum)
    sensors = [
        WasteSensor(waste_data, "garbage"),
        WasteSensor(waste_data, "green_waste"),
        WasteSensor(waste_data, "recycling"),
    ]
    add_entities(sensors, True)
    _LOGGER.debug("Added sensors: %s", sensors)

class WasteData:
    """Class to manage fetching waste data."""

    def __init__(self, propnum):
        self._propnum = propnum
        self._data = None

    @Throttle(UPDATE_INTERVAL)
    def update(self):
        """Fetch new data for the sensor."""
        _LOGGER.debug("Updating sensor: %s", self.name)
        self._waste_data.update()
        if self._waste_data.data:
            self._state = self._waste_data.data.get(self._sensor_type)
            _LOGGER.debug("Updated state for %s: %s", self.name, self._state)
    

    @property
    def data(self):
        return self._data

class WasteSensor(Entity):
    """Representation of a Waste Collection Sensor."""

    def __init__(self, waste_data, sensor_type):
        self._waste_data = waste_data
        self._sensor_type = sensor_type
        self._state = None

    def update(self):
        """Fetch new data for the sensor."""
        self._waste_data.update()
        if self._waste_data.data:
            self._state = self._waste_data.data.get(self._sensor_type)

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"Wyndham {self._sensor_type.replace('_', ' ').title()}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state