# seeed-zephyr

CLI for [Seeed Studio XIAO](https://www.seeedstudio.com/xiao-series-page) boards
with [Zephyr RTOS](https://zephyrproject.org/).

## Install

```bash
pip install seeed-zephyr
```

Or with [pipx](https://pipx.pypa.io/) for isolated installation:

```bash
pipx install seeed-zephyr
```

## Quick Start

```bash
# List supported boards
seeed-zephyr list boards

# List available examples for a board
seeed-zephyr list examples xiao_esp32c6

# Build an example
seeed-zephyr build xiao_esp32c6 blinky

# Build and flash
seeed-zephyr flash xiao_esp32c6 blinky

# Build and flash with serial monitor
seeed-zephyr flash xiao_esp32c6 blinky --monitor

# Build your own app
seeed-zephyr flash xiao_esp32c6 --app ~/my-zephyr-app --monitor

# Open serial monitor
seeed-zephyr monitor
```

## Prerequisites

This CLI requires a Zephyr development environment. Run the setup command
after installation:

```bash
# macOS
curl -fsSL https://raw.githubusercontent.com/limengdu/Seeed-Zephyr-Project/main/install.sh | bash

# Or set up manually — see the full guide:
# https://github.com/limengdu/Seeed-Zephyr-Project/blob/main/docs/en/getting-started.md
```

## Supported Boards

| Board | SoC | Vendor |
|-------|-----|--------|
| XIAO ESP32C3 | ESP32-C3 | Espressif |
| XIAO ESP32C5 | ESP32-C5 | Espressif |
| XIAO ESP32C6 | ESP32-C6 | Espressif |
| XIAO ESP32S3 | ESP32-S3 | Espressif |
| XIAO MG24 | EFR32MG24 | Silicon Labs |
| XIAO nRF52840 | nRF52840 | Nordic |
| XIAO nRF54L15 | nRF54L15 | Nordic |
| XIAO RA4M1 | RA4M1 | Renesas |
| XIAO RP2040 | RP2040 | Raspberry Pi |
| XIAO RP2350 | RP2350 | Raspberry Pi |
| XIAO SAMD21 | SAMD21 | Microchip |

## License

Apache-2.0
