"""DataUpdateCoordinator for wyndham_waste."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import WyndhamWasteApiClient, WyndhamWasteApiError, WyndhamWasteAuthError
from .const import DOMAIN, LOGGER

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from .data import WyndhamWasteConfigEntry


class WyndhamWasteDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching waste collection data."""

    config_entry: WyndhamWasteConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        client: WyndhamWasteApiClient,
    ) -> None:
        """Initialize the coordinator."""
        self.client = client

        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=1),
        )

    async def _async_update_data(self) -> dict[str, str]:
        """Fetch data from the API."""
        try:
            data = await self.client.async_get_waste_data()
            # Validate and structure data
            if not isinstance(data, dict):
                raise UpdateFailed("Invalid data format received")
            return data
        except WyndhamWasteAuthError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except WyndhamWasteApiError as exception:
            raise UpdateFailed(exception) from exception
