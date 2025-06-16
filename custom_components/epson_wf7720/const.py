"""Constants for the EPSON WF-7720 Series integration."""
from typing import Final

DOMAIN: Final = "epson_wf7720"
DEFAULT_NAME = "EPSON WF-7720"
DEFAULT_PORT = 161

# SNMP OIDs for EPSON printers
SNMP_COMMUNITY = "public"

# Base OIDs for Epson printers
BASE_OID = "1.3.6.1.4.1.1248.1.2.2"

# Status OIDs
STATUS_OID = f"{BASE_OID}.1.1.1.4.1"
MODEL_OID = "1.3.6.1.2.1.25.3.2.1.3.1"
DESCRIPTION_OID = "1.3.6.1.2.1.1.1.0"

# Ink level OIDs - these are common for Epson printers
INK_LEVEL_BASE = f"{BASE_OID}.1.1.1.4.1"

# Color mappings
INK_COLORS = {
    1: "Black",
    2: "Cyan", 
    3: "Magenta",
    4: "Yellow"
}

# Printer status codes
STATUS_CODES = {
    0: "Unknown",
    1: "Other",
    2: "Unknown",
    3: "Idle",
    4: "Printing",
    5: "Warming Up"
}