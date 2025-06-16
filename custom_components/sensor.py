"""Support for EPSON WF-7720 Series printer sensors."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, INK_COLORS

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    host = config_entry.data[CONF_HOST]
    
    entities = []
    
    # Add ink level sensors
    for color in INK_COLORS.values():
        entities.append(
            EpsonInkSensor(coordinator, host, color.lower())
        )
    
    # Add printer status sensor
    entities.append(EpsonStatusSensor(coordinator, host))
    
    async_add_entities(entities)

class EpsonInkSensor(CoordinatorEntity, SensorEntity):
    """Representation of an ink level sensor."""
    
    def __init__(self, coordinator, host: str, color: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.host = host
        self.color = color
        self._attr_name = f"EPSON WF-7720 {color.title()} Ink"
        self._attr_unique_id = f"epson_wf7720_{host}_{color}_ink"
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:printer-3d-nozzle"
    
    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        if self.coordinator.data and "ink_levels" in self.coordinator.data:
            return self.coordinator.data["ink_levels"].get(self.color, 0)
        return None
    
    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Return additional attributes."""
        return {
            "color": self.color.title(),
            "printer_host": self.host,
        }

class EpsonStatusSensor(CoordinatorEntity, SensorEntity):
    """Representation of a printer status sensor."""
    
    def __init__(self, coordinator, host: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.host = host
        self._attr_name = "EPSON WF-7720 Status"
        self._attr_unique_id = f"epson_wf7720_{host}_status"
        self._attr_icon = "mdi:printer"
    
    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        if self.coordinator.data and "status" in self.coordinator.data:
            return self.coordinator.data["status"]
        return None
    
    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Return additional attributes."""
        attrs = {"printer_host": self.host}
        
        if self.coordinator.data:
            if "model" in self.coordinator.data:
                attrs["model"] = self.coordinator.data["model"]
            if "description" in self.coordinator.data:
                attrs["description"] = self.coordinator.data["description"]
        
        return attrs