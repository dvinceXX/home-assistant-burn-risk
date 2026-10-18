"""Fetch and parse burn-risk information."""
from __future__ import annotations

import re
from html.parser import HTMLParser
from typing import Any

from aiohttp import ClientError, ClientSession, ClientTimeout
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DEFAULT_SCAN_INTERVAL_MINUTES, DOMAIN, RISK_LEVELS


class _VisibleTextParser(HTMLParser):
    """Extract visible text and text inside likely active/status elements."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.active_parts: list[str] = []
        self._active_depth = 0
        self._ignored_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {key.lower(): (value or "").lower() for key, value in attrs}
        if tag in ("script", "style", "noscript"):
            self._ignored_depth += 1
        classes = attrs_dict.get("class", "")
        marker = " ".join(
            [classes, attrs_dict.get("id", ""), attrs_dict.get("aria-label", "")]
        )
        if any(word in marker for word in ("active", "current", "selected", "status", "risk-level")):
            self._active_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style", "noscript") and self._ignored_depth:
            self._ignored_depth -= 1
        # Active elements are captured best-effort; closing nested tags can
        # make exact depth tracking ambiguous, so the full page remains fallback.
        if self._active_depth:
            self._active_depth -= 1

    def handle_data(self, data: str) -> None:
        text = " ".join(data.split())
        if text and not self._ignored_depth:
            self.parts.append(text)
            if self._active_depth:
                self.active_parts.append(text)


def parse_risk_page(html: str) -> tuple[int, str]:
    """Return the current numeric risk level and label from the page HTML."""
    parser = _VisibleTextParser()
    parser.feed(html)
    active_text = " ".join(parser.active_parts)
    full_text = " ".join(parser.parts)

    # Prefer status-like elements, which helps avoid matching a page legend.
    for source in (active_text, full_text):
        if not source:
            continue
        normalized = re.sub(r"\s+", " ", source).casefold()
        patterns = (
            (5, r"\btotal\s+ban\b|\btotal\s+burn\s+ban\b"),
            (4, r"\bextreme(?:\s+risk)?\b"),
            (3, r"\bhigh(?:\s+risk)?\b"),
            (2, r"\bmoderate(?:\s+risk)?\b"),
            (1, r"\blow(?:\s+risk)?\b"),
        )
        for level, pattern in patterns:
            if re.search(pattern, normalized):
                return level, RISK_LEVELS[level]

    raise ValueError("Could not find a recognized burn-risk status in the page")


class BurnRiskCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinate periodic updates and retain the last successful value."""

    def __init__(self, hass: HomeAssistant, url: str) -> None:
        self.url = url
        self.session: ClientSession = async_get_clientsession(hass)
        self._stale = False
        super().__init__(
            hass,
            logger=__import__("logging").getLogger(__name__),
            name=DOMAIN,
            update_interval=__import__("datetime").timedelta(
                minutes=DEFAULT_SCAN_INTERVAL_MINUTES
            ),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch the page, parse the status, and preserve last-known data on errors."""
        try:
            timeout = ClientTimeout(total=20)
            async with self.session.get(self.url, timeout=timeout) as response:
                response.raise_for_status()
                html = await response.text()
            level, status = parse_risk_page(html)
            self._stale = False
            return {"level": level, "status": status, "stale": False, "source": self.url}
        except (ClientError, TimeoutError, ValueError) as err:
            if self.data is not None:
                self._stale = True
                return {**self.data, "stale": True}
            raise UpdateFailed(f"Unable to retrieve burn-risk status: {err}") from err
