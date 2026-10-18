"""Config flow for Burn Risk."""
from __future__ import annotations

from urllib.parse import urlparse

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import DEFAULT_URL, DOMAIN


def _valid_url(value: str) -> bool:
    parsed = urlparse(value.strip())
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


class BurnRiskConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Burn Risk."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, str] | None = None
    ) -> FlowResult:
        """Handle the initial user step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            url = user_input["url"].strip().rstrip("/")
            if not _valid_url(url):
                errors["url"] = "invalid_url"
            else:
                await self.async_set_unique_id(url.lower())
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title="Burn Risk", data={"url": url})

        schema = vol.Schema({vol.Required("url", default=DEFAULT_URL): str})
        return self.async_show_form(
            step_id="user", data_schema=schema, errors=errors
        )
