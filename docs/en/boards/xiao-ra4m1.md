# XIAO RA4M1 Zephyr Development Guide

This page records board-specific Zephyr development notes for Seeed Studio XIAO RA4M1.
For the full setup, build, and flash flow, see [Getting Started](../getting-started.md).

## USB DFU Flashing

This repository flashes XIAO RA4M1 through the board USB DFU bootloader:

```sh
seeed-zephyr flash xiao_ra4m1 --monitor
```

When repository setup is run with `--board xiao_ra4m1`, or without a board for
full setup, the script installs `dfu-util`. The CLI converts the Zephyr build
output into a compact bin suitable for the DFU bootloader, then uploads it with
`dfu-util`.

If the board is currently running firmware with a DFU runtime interface, the CLI
can switch from runtime to DFU and upload directly. If the running firmware does
not expose DFU runtime, enter the DFU bootloader manually before flashing.

## Application Start Address

XIAO RA4M1's board USB DFU bootloader occupies the first 16 KB of flash. Zephyr
examples must start at `0x4000`:

```conf
CONFIG_FLASH_LOAD_OFFSET=0x4000
```

Keep this configuration when creating new RA4M1 examples.

## Enter DFU Bootloader

If the host cannot see the DFU device during flashing, enter bootloader mode:

1. Connect the XIAO RA4M1 USB port.
2. Hold the right Boot button.
3. Tap the left Reset button.
4. Keep holding Boot for about 1 to 2 seconds after releasing Reset.
5. Run the flash command again.

## Serial Monitor

The repository baseline example routes Zephyr console output to USB CDC serial.
Open the serial monitor after flashing:

```sh
seeed-zephyr monitor xiao_ra4m1
```

If multiple USB serial devices are attached, pass the port:

```sh
seeed-zephyr monitor xiao_ra4m1 --port /dev/cu.usbmodem1101
```

Exit monitor:

```text
Ctrl+]
```

## Debugging

XIAO RA4M1 uses J-Link as Zephyr's default debug runner. Debugging requires an
external debugger connected to the SWD pads on the bottom of the board. Normal
flashing does not require J-Link.

Reference: [Zephyr XIAO RA4M1 documentation](https://docs.zephyrproject.org/latest/boards/seeed/xiao_ra4m1/doc/index.html).
