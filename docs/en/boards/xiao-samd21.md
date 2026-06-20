# XIAO SAMD21 Zephyr Development Guide

This page records only board-level Zephyr development notes for Seeed Studio
XIAO SAMD21. For full setup, build, and flashing commands, see
[Getting Started](../getting-started.md).

## BOSSA Flashing

XIAO SAMD21 uses a BOSSA-compatible bootloader. During flashing, Zephyr's
`bossac` runner writes firmware to the board.

Common command:

```sh
seeed-zephyr flash xiao_samd21 --monitor
```

If the system reports that `bossac` is missing, install the flashing tool needed
by this board, then rerun the flash command.

## Repeated Flashing Without Double-Clicking RESET

Goal: after firmware is already running, the host can ask the board to reboot
into bootloader mode through USB CDC serial before the next flash.

For a custom XIAO SAMD21 example, handle these files:

- `prj.conf`: enable the legacy USB device stack, UART line control, USB CDC
  serial, and console.
- `app.overlay`: define `cdc_acm_uart0` and set `label = "CDC_ACM_0"`.
- `src/main.c`: call `usb_enable(NULL)` during startup so the USB CDC serial
  port appears.

Key configuration:

```conf
CONFIG_UART_LINE_CTRL=y
CONFIG_USB_DEVICE_STACK=y
CONFIG_USB_DEVICE_INITIALIZE_AT_BOOT=n
CONFIG_USB_DEVICE_STACK_NEXT=n
CONFIG_SERIAL=y
CONFIG_CONSOLE=y
CONFIG_UART_CONSOLE=y
```

Key `app.overlay` structure:

```dts
/ {
	chosen {
		zephyr,console = &cdc_acm_uart0;
	};
};

&zephyr_udc0 {
	cdc_acm_uart0: cdc_acm_uart0 {
		compatible = "zephyr,cdc-acm-uart";
		label = "CDC_ACM_0";
	};
};
```

Reference implementation: `examples/boards/xiao_samd21/blinky`.

## USB CDC Serial Output

Goal: make `printk()` output visible through the USB serial monitor.

Handle these files:

- `prj.conf`: enable `CONFIG_PRINTK`, `CONFIG_SERIAL`, `CONFIG_CONSOLE`,
  `CONFIG_UART_CONSOLE`, and the USB device stack.
- `app.overlay`: route `zephyr,console` to `cdc_acm_uart0`.
- `src/main.c`: call `usb_enable(NULL)` before printing runtime logs.

Open the monitor:

```sh
seeed-zephyr monitor xiao_samd21
```

Exit the monitor:

```text
Ctrl+]
```

## Manual Bootloader Mode

Use this only as the recovery path when automatic flashing cannot enter
bootloader mode:

1. Double-click `RESET`.
2. Wait for the bootloader serial port to appear.
3. Rerun the flash command.
