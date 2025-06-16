# EPSON WF-7720 Series Home Assistant Integration

This custom integration allows you to monitor your EPSON WF-7720 Series printer directly in Home Assistant.

## Features

- Monitor all 4 ink levels (Black, Cyan, Magenta, Yellow) as percentage
- Track printer status (Idle, Printing, etc.)
- Direct IP connection to printer via SNMP
- Real-time updates every 30 seconds

## Installation

### HACS (Recommended)
1. Add this repository to HACS as a custom repository
2. Install "EPSON WF-7720 Series Printer"
3. Restart Home Assistant

### Manual Installation
1. Download the latest release
2. Copy the `custom_components/epson_wf7720` folder to your Home Assistant `custom_components` directory
3. Restart Home Assistant

## Configuration

1. Go to Settings → Devices & Services
2. Click "Add Integration"
3. Search for "EPSON WF-7720 Series"
4. Enter your printer's IP address
5. Complete the setup

## Sensors Created

- `sensor.epson_wf7720_black_ink` - Black ink level percentage
- `sensor.epson_wf7720_cyan_ink` - Cyan ink level percentage  
- `sensor.epson_wf7720_magenta_ink` - Magenta ink level percentage
- `sensor.epson_wf7720_yellow_ink` - Yellow ink level percentage
- `sensor.epson_wf7720_status` - Current printer status

## Requirements

- EPSON WF-7720 Series printer connected to your network
- Printer IP address
- SNMP enabled on printer (usually enabled by default)

## Troubleshooting

If ink levels show as 0%, the printer may use different SNMP OIDs. Please open an issue with your printer's exact model number.

## Contributing

Feel free to contribute improvements or report issues on GitHub.
