"""API Client for Wyndham Waste."""

from __future__ import annotations

import socket
from typing import Any

import aiohttp
import async_timeout


class WyndhamWasteApiError(Exception):
    """Exception to indicate a general API error."""


class WyndhamWasteApiCommunicationError(WyndhamWasteApiError):
    """Exception to indicate a communication error."""


class WyndhamWasteAuthError(WyndhamWasteApiError):
    """Exception to indicate an authentication error."""


def _verify_response_or_raise(response: aiohttp.ClientResponse) -> None:
    """Verify that the response is valid."""
    if response.status in (401, 403):
        msg = "Invalid credentials"
        raise WyndhamWasteAuthError(msg)
    response.raise_for_status()


class WyndhamWasteApiClient:
    """API Client for Wyndham Waste."""

    def __init__(
        self,
        propnum: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """Initialize the API client."""
        self._propnum = propnum
        self._session = session

    async def async_get_waste_data(self) -> dict[str, str]:
        """Fetch waste collection data."""
        url = "https://digital.wyndham.vic.gov.au/myWyndham/init-map-data.asp"
        params = {
            "propnum": self._propnum,
            "radius": "3000",  # Adjust radius if needed
            "mapfeatures": "",
        }

        try:
            async with async_timeout.timeout(10):
                response = await self._session.get(url, params=params)
                _verify_response_or_raise(response)
                return self._parse_waste_data(await response.text())
        except TimeoutError as exception:
            msg = f"Timeout error fetching information - {exception}"
            raise WyndhamWasteApiCommunicationError(msg) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error fetching information - {exception}"
            raise WyndhamWasteApiCommunicationError(msg) from exception
        except Exception as exception:  # pylint: disable=broad-except
            msg = f"Unexpected error - {exception}"
            raise WyndhamWasteApiError(msg) from exception

    def _parse_waste_data(self, html: str) -> dict[str, str]:
        """Extract waste collection information from HTML."""
        import re

        patterns = {
            "garbage": r"Next Garbage Collection:\s*(.*?)\s*</div>",
            "green_waste": r"Next Green Waste Collection:\s*(.*?)\s*</div>",
            "recycling": r"Next Recycling Collection:\s*(.*?)\s*</div>",
            "week": r"Waste Collection Week:\s*(\d+)",
        }

        waste_data = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, html)
            if match:
                waste_data[key] = match.group(1)

        if not waste_data:
            raise WyndhamWasteApiError("Failed to parse waste data from response")

        return waste_data
