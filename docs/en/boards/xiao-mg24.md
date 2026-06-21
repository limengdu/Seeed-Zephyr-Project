# XIAO MG24 Zephyr Development Guide

This page records only board-level Zephyr development notes for Seeed Studio
XIAO MG24. For full setup, build, and flashing commands, see
[Getting Started](../getting-started.md).

## PyOCD Flashing

XIAO MG24 uses Zephyr's official `pyocd` runner by default:

```sh
seeed-zephyr flash xiao_mg24 --monitor
```

Before first use, install the MG24 CMSIS pack:

```sh
pyocd pack install EFR32MG24B220F1536IM48
```

Repository setup handles this automatically when `xiao_mg24` is selected, or
when setup runs without a board filter for full board-specific host tools.

## Debug Mate Serial And Debug Probe

XIAO MG24 includes an on-board SAMD11 CMSIS-DAP debug probe. After the host sees
the CMSIS-DAP device, Zephyr's `pyocd` runner can use it to connect to MG24.

Open the serial monitor:

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

## OpenOCD Fallback Path

Zephyr's official documentation also describes OpenOCD for MG24, but that
OpenOCD build must include MG24 flash support. If regular OpenOCD fails with
`target/efm32s2_g23.cfg` or flash-support errors, prefer this repository's
default `pyocd` path.

Reference: [Zephyr XIAO MG24 documentation](https://docs.zephyrproject.org/latest/boards/seeed/xiao_mg24/doc/index.html).
