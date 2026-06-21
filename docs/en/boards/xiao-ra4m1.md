# XIAO RA4M1 Zephyr Development Guide

This page records board-specific Zephyr development notes for Seeed Studio XIAO RA4M1.
For the full setup, build, and flash flow, see [Getting Started](../getting-started.md).

## RFP Flashing

XIAO RA4M1's default Zephyr flash path is the `rfp` runner. It uses Renesas
Flash Programmer CLI to write firmware through the built-in RA USB bootloader.

```sh
seeed-zephyr flash xiao_ra4m1 --monitor
```

When repository setup is run with `--board xiao_ra4m1`, or without a board for
full setup, the script prepares `rfp-cli`.

## Enter USB Bootloader

Before flashing, enter bootloader mode:

1. Connect the XIAO RA4M1 USB port.
2. Hold the right Boot button.
3. Tap the left Reset button.
4. Keep holding Boot for about 1 to 2 seconds after releasing Reset.
5. Run the flash command again.

## Serial Monitor

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
