"""The EPSON WF-7720 Series integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, DEFAULT_PORT, SNMP_COMMUNITY
from .epson_printer import EpsonPrinter

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up EPSON WF-7720 from a config entry."""
    host = entry.data[CONF_HOST]
    port = entry.data.get(CONF_PORT, DEFAULT_PORT)
    
    printer = EpsonPrinter(host, port, SNMP_COMMUNITY)
    
    coordinator = EpsonDataUpdateCoordinator(hass, printer)
    
    await coordinator.async_config_entry_first_refresh()
    
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok

class EpsonDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the printer."""
    
    def __init__(self, hass: HomeAssistant, printer: EpsonPrinter) -> None:
        """Initialize."""
        self.printer = printer
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )
    
    async def _async_update_data(self):
        """Update data via library."""
        try:
            return await self.hass.async_add_executor_job(self.printer.get_data)
        except Exception as exception:
            raise UpdateFailed() from exception