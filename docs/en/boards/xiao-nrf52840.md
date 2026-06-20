# XIAO nRF52840 Zephyr Development Guide

This page records only board-level Zephyr development notes for Seeed Studio
XIAO nRF52840. For full setup, build, and flashing commands, see
[Getting Started](../getting-started.md).

## UF2 Flashing

XIAO nRF52840 ships with the Adafruit nRF52 Bootloader. Use UF2 for normal
flashing:

```sh
seeed-zephyr flash xiao_nrf52840 --monitor
```

The repository CLI calls Zephyr's `uf2` runner instead of the default `nrfutil`
runner.

When the board is already running this repository example, the CLI first asks
the board to enter UF2 download mode through USB CDC at 1200 baud, then calls
Zephyr's UF2 runner.

When using Zephyr commands directly, double-tap `RESET` to enter UF2 download
mode, then run:

```sh
west flash --runner uf2
```

## Repeated Flashing Without Double-Tap RESET

Goal: after firmware is already running, the host can ask the board to enter
UF2 mode through the USB CDC serial port.

For custom examples, keep these pieces:

- `prj.conf`: enable reboot, UART line control, USB CDC serial, and console.
- `src/main.c`: watch `UART_LINE_CTRL_BAUD_RATE`.
- When the baud rate becomes `1200`, write `0x57` to `GPREGRET`, then call
  `sys_reboot(SYS_REBOOT_COLD)`.
- If the main loop has long `k_msleep()` calls, split them into short intervals
  and check for the 1200 baud request between intervals.

Use the repository example as the reference:

```text
examples/boards/xiao_nrf52840/blinky/prj.conf
examples/boards/xiao_nrf52840/blinky/src/main.c
```

## Manual UF2 Download Mode

Use this recovery path when the current firmware does not support automatic UF2
requests, or when the USB CDC serial port is not visible:

1. Double-tap `RESET` quickly.
2. Wait for the UF2 storage volume.
3. Rerun the flash command.

## USB CDC Serial Output

Goal: make `printk()` output visible through the USB serial monitor.

The XIAO nRF52840 Zephyr board provides a USB CDC console by default. For custom
examples, keep at least:

```conf
CONFIG_PRINTK=y
CONFIG_SERIAL=y
CONFIG_CONSOLE=y
CONFIG_UART_CONSOLE=y
```

If the application prints immediately after boot and the monitor misses the
first lines, add a boot delay:

```conf
CONFIG_BOOT_DELAY=5000
```

Exit the monitor:

```text
Ctrl+]
```
