"""Config flow for EPSON WF-7720 Series integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, DEFAULT_PORT, DEFAULT_NAME
from .epson_printer import EpsonPrinter

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
    }
)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for EPSON WF-7720 Series."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            info = await self._validate_input(user_input)
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def _validate_input(self, data: dict[str, Any]) -> dict[str, Any]:
        """Validate the user input allows us to connect."""
        host = data[CONF_HOST]
        port = data.get(CONF_PORT, DEFAULT_PORT)
        
        printer = EpsonPrinter(host, port, "public")
        
        # Test connection
        result = await self.hass.async_add_executor_job(printer.get_data)
        
        if not result:
            raise Exception("Cannot connect to printer")

        return {"title": f"{DEFAULT_NAME} ({host})"}