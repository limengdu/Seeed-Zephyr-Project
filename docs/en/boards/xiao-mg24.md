# XIAO MG24 Zephyr Development Guide

This page records only board-level Zephyr development notes for Seeed Studio
XIAO MG24. For full setup, build, and flashing commands, see
[Getting Started](../getting-started.md).

## Debug Mate OpenOCD Flashing

When flashing XIAO MG24 through Seeed Studio XIAO Debug Mate, use Seeed's MG24
OpenOCD package. The regular Zephyr SDK OpenOCD package may not include
`target/efm32s2_g23.cfg`.

After downloading and extracting `XIAO_MG24_Mac_Linux_OpenOCD-v0.12.0` from the
Seeed guide, set:

```sh
export SEEED_ZEPHYR_MG24_OPENOCD=/path/to/XIAO_MG24_Mac_Linux_OpenOCD-v0.12.0
```

Then run:

```sh
seeed-zephyr flash xiao_mg24 --monitor
```

The CLI still calls Zephyr's `west flash`, with the OpenOCD runner pointed at
the MG24 OpenOCD package.

Reference: [Seeed XIAO Debug Mate - XIAO MG24](https://wiki.seeedstudio.com/xiao_debug_mate_debug/#for-seeed-studio-xiao-mg24).

## HEX Firmware

When calling OpenOCD manually instead of using the CLI, flash Zephyr's
`zephyr.hex` output. Do not use `zephyr.elf` as the MG24 Debug Mate flashing
file.

The CLI uses the correct `.hex` output from the Zephyr build directory.

## Serial Monitor

`--monitor` searches for one USB serial port and opens pyserial miniterm after a
successful flash:

```sh
seeed-zephyr monitor xiao_mg24
```

If more than one USB serial device is attached, pass the port:

```sh
seeed-zephyr monitor xiao_mg24 --port /dev/cu.usbmodem1101
```

Exit the monitor:

```text
Ctrl+]
```
