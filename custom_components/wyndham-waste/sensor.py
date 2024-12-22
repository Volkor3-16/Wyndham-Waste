"""Sensor platform for wyndham_waste."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.const import DEVICE_CLASS_TIMESTAMP

from .entity import WyndhamWasteEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import WyndhamWasteDataUpdateCoordinator
    from .data import WyndhamWasteConfigEntry

# Define entity descriptions for the waste sensors
ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="garbage",
        name="Garbage Collection",
        icon="mdi:trash-can",
        device_class=DEVICE_CLASS_TIMESTAMP,
    ),
    SensorEntityDescription(
        key="green_waste",
        name="Green Waste Collection",
        icon="mdi:leaf",
        device_class=DEVICE_CLASS_TIMESTAMP,
    ),
    SensorEntityDescription(
        key="recycling",
        name="Recycling Collection",
        icon="mdi:recycle",
        device_class=DEVICE_CLASS_TIMESTAMP,
    ),
)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: WyndhamWasteConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    async_add_entities(
        WyndhamWasteSensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class WyndhamWasteSensor(WyndhamWasteEntity, SensorEntity):
    """Sensor class for Wyndham Waste Collection."""

    def __init__(
        self,
        coordinator: WyndhamWasteDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description

    @property
    def native_value(self) -> str | None:
        """Return the next collection date for the sensor."""
        return self.coordinator.data.get(self.entity_description.key)