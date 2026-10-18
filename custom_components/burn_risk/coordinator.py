"""Fetch and parse burn-risk information."""
from __future__ import annotations

import logging
import re
from datetime import timedelta
from typing import Any

from aiohttp import ClientError, ClientTimeout
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DEFAULT_SCAN_INTERVAL_MINUTES, DOMAIN, RISK_LEVELS

_LOGGER = logging.getLogger(__name__)


def parse_risk_page(html: str) -> tuple[int, str]:
    """Parse the numeric value field used by mm.burnpermits.com."""
    # Match the field the original shell script reads, rather than matching
    # words in a page legend that may list every possible risk category.
    match = re.search(r"\bvalue\s*:\s*[\"']?([0-5])[\"']?", html, re.IGNORECASE)
    if match is None:
        raise ValueError("Could not find a burn-risk value in the page")
    level = int(match.group(1))
    if level not in RISK_LEVELS:
        raise ValueError(f"Unsupported burn-risk value: {level}")
    return level, RISK_LEVELS[level]


class BurnRiskCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinate periodic updates and retain the last successful value."""

    def __init__(self, hass: HomeAssistant, url: str) -> None:
        self.url = url
        self.session = async_get_clientsession(hass)
        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=DEFAULT_SCAN_INTERVAL_MINUTES),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch the page and preserve the last known value when a refresh fails."""
        try:
            timeout = ClientTimeout(total=20)
            async with self.session.get(self.url, timeout=timeout) as response:
                response.raise_for_status()
                html = await response.text()
            level, status = parse_risk_page(html)
            return {
                "level": level,
                "status": status,
                "stale": False,
                "source": self.url,
            }
        except (ClientError, TimeoutError, ValueError) as err:
            if self.data is not None:
                _LOGGER.warning("Burn-risk refresh failed; keeping last known value: %s", err)
                return {**self.data, "stale": True}
            raise UpdateFailed(f"Unable to retrieve burn-risk status: {err}") from err
