"""EPSON Printer SNMP communication."""
import logging
from typing import Any, Dict

from pysnmp.hlapi import (
    CommunityData,
    ContextData,
    ObjectIdentity,
    ObjectType,
    SnmpEngine,
    UdpTransportTarget,
    getCmd,
)

from .const import (
    STATUS_OID,
    MODEL_OID,
    DESCRIPTION_OID,
    INK_COLORS,
    STATUS_CODES,
    BASE_OID,
)

_LOGGER = logging.getLogger(__name__)

class EpsonPrinter:
    """Epson printer SNMP interface."""
    
    def __init__(self, host: str, port: int, community: str) -> None:
        """Initialize the printer."""
        self.host = host
        self.port = port
        self.community = community
        
    def _snmp_get(self, oid: str) -> Any:
        """Get SNMP value."""
        try:
            iterator = getCmd(
                SnmpEngine(),
                CommunityData(self.community),
                UdpTransportTarget((self.host, self.port)),
                ContextData(),
                ObjectType(ObjectIdentity(oid)),
            )
            
            error_indication, error_status, error_index, var_binds = next(iterator)
            
            if error_indication:
                _LOGGER.error("SNMP error indication: %s", error_indication)
                return None
            elif error_status:
                _LOGGER.error("SNMP error status: %s", error_status.prettyPrint())
                return None
            else:
                for var_bind in var_binds:
                    return var_bind[1]
        except Exception as e:
            _LOGGER.error("SNMP request failed: %s", e)
            return None
    
    def _parse_ink_levels(self, status_data: bytes) -> Dict[str, int]:
        """Parse ink levels from status data."""
        ink_levels = {}
        
        if not status_data or len(status_data) < 50:
            return ink_levels
            
        try:
            # This is a simplified parser - actual parsing depends on the @BDC ST2 format
            # For WF-7720, we need to identify the ink level section in the status response
            
            # Look for ink level indicators in the status data
            for i, color in INK_COLORS.items():
                # Try to extract ink level - this may need adjustment based on actual data format
                if len(status_data) > i * 10 + 20:
                    level_byte = status_data[i * 10 + 20] if i * 10 + 20 < len(status_data) else 0
                    # Convert to percentage (assuming max value of 255)
                    percentage = min(100, max(0, int((level_byte / 255) * 100)))
                    ink_levels[color.lower()] = percentage
                else:
                    ink_levels[color.lower()] = 0
                    
        except Exception as e:
            _LOGGER.error("Error parsing ink levels: %s", e)
            # Return default values if parsing fails
            for color in INK_COLORS.values():
                ink_levels[color.lower()] = 0
                
        return ink_levels
    
    def _parse_printer_status(self, status_data: bytes) -> str:
        """Parse printer status from status data."""
        if not status_data or len(status_data) < 10:
            return "Unknown"
            
        try:
            # Extract status code from the beginning of status data
            status_code = status_data[8] if len(status_data) > 8 else 0
            return STATUS_CODES.get(status_code, "Unknown")
        except Exception as e:
            _LOGGER.error("Error parsing printer status: %s", e)
            return "Unknown"
    
    def get_data(self) -> Dict[str, Any]:
        """Get all printer data."""
        data = {}
        
        # Get printer model
        model = self._snmp_get(MODEL_OID)
        if model:
            data["model"] = str(model)
        
        # Get printer description
        description = self._snmp_get(DESCRIPTION_OID)
        if description:
            data["description"] = str(description)
        
        # Get status data
        status_data = self._snmp_get(STATUS_OID)
        if status_data:
            # Parse ink levels
            ink_levels = self._parse_ink_levels(bytes(status_data))
            data["ink_levels"] = ink_levels
            
            # Parse printer status
            printer_status = self._parse_printer_status(bytes(status_data))
            data["status"] = printer_status
        else:
            # Default values if no data available
            data["ink_levels"] = {color.lower(): 0 for color in INK_COLORS.values()}
            data["status"] = "Unavailable"
        
        # Try alternative OIDs for ink levels if main method doesn't work
        if all(level == 0 for level in data["ink_levels"].values()):
            data["ink_levels"] = self._get_ink_levels_alternative()
        
        return data
    
    def _get_ink_levels_alternative(self) -> Dict[str, int]:
        """Alternative method to get ink levels using different OIDs."""
        ink_levels = {}
        
        # Try different OID patterns that might work for WF-7720
        alternative_oids = [
            "1.3.6.1.4.1.1248.1.2.2.1.1.1.4.1",
            "1.3.6.1.4.1.1248.1.2.2.44.1.1.2.1",
        ]
        
        for base_oid in alternative_oids:
            try:
                for i, color in INK_COLORS.items():
                    # Try different offsets for each color
                    for offset in [i, i+10, i+20]:
                        oid = f"{base_oid}.{offset}"
                        value = self._snmp_get(oid)
                        if value and isinstance(value, (int, bytes)):
                            if isinstance(value, bytes) and len(value) > 0:
                                level = min(100, max(0, int((value[0] / 255) * 100)))
                            elif isinstance(value, int):
                                level = min(100, max(0, value))
                            else:
                                continue
                            ink_levels[color.lower()] = level
                            break
                
                # If we got some data, break out of the outer loop
                if any(level > 0 for level in ink_levels.values()):
                    break
                    
            except Exception as e:
                _LOGGER.debug("Alternative OID %s failed: %s", base_oid, e)
                continue
        
        # Ensure all colors are present
        for color in INK_COLORS.values():
            if color.lower() not in ink_levels:
                ink_levels[color.lower()] = 0
                
        return ink_levels