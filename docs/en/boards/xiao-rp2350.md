# XIAO RP2350 Zephyr Development Guide

This page records only board-level Zephyr development notes for Seeed Studio
XIAO RP2350. For full setup, build, and flashing commands, see
[Getting Started](../getting-started.md).

## UF2 Flashing

XIAO RP2350 uses UF2 download mode. During normal development, do not copy UF2
files manually; run:

```sh
seeed-zephyr flash xiao_rp2350 --monitor
```

When using Zephyr commands directly, add the RP2 boot mode retention snippet at
build time:

```sh
west build -p always -b xiao_rp2350/rp2350a/m33 -S rp2-boot-mode-retention <app>
west flash
```

The repository CLI adds this snippet automatically.

Zephyr provides both M33 and Hazard3 targets. This repository defaults to M33
because UF2 flashing and USB CDC monitoring have been verified on that target;
Hazard3 is not the default example target.

## Repeated Flashing Without BOOTSEL

Goal: after firmware is already running, the host can ask the board to enter UF2
mode through USB CDC serial before the next flash.

For a custom XIAO RP2350 example, handle these files:

- `prj.conf`: enable retained memory, boot mode, reboot, UART line control, USB
  CDC serial, and console.
- `app.overlay`: include `rp2350-boot-mode-retention.dtsi`, define
  `cdc_acm_uart0`, and route `zephyr,console` to it.
- `src/main.c`: read `UART_LINE_CTRL_BAUD_RATE`; when the host opens USB CDC at
  `1200` baud, set `BOOT_MODE_TYPE_BOOTLOADER` and call `sys_reboot()`.

Key configuration:

```conf
CONFIG_RETAINED_MEM=y
CONFIG_RETENTION=y
CONFIG_RETENTION_BOOT_MODE=y
CONFIG_REBOOT=y
CONFIG_UART_LINE_CTRL=y
CONFIG_USB_DEVICE_STACK_NEXT=y
CONFIG_CDC_ACM_SERIAL_INITIALIZE_AT_BOOT=y
```

Key `app.overlay` structure:

```dts
#include <vendor/raspberrypi/rp2350-boot-mode-retention.dtsi>

/ {
	chosen {
		zephyr,console = &cdc_acm_uart0;
	};
};

&zephyr_udc0 {
	cdc_acm_uart0: cdc_acm_uart0 {
		compatible = "zephyr,cdc-acm-uart";
	};
};
```

Reference implementation: `examples/boards/xiao_rp2350/blinky`.

## USB CDC Serial Output

Goal: make `printk()` output visible through the USB serial monitor.

Handle these files:

- `prj.conf`: enable `CONFIG_PRINTK`, `CONFIG_SERIAL`, `CONFIG_CONSOLE`,
  `CONFIG_UART_CONSOLE`, and USB CDC.
- `app.overlay`: route `zephyr,console` to `cdc_acm_uart0`.
- `src/main.c`: print runtime logs with `printk()`.

Open the monitor:

```sh
seeed-zephyr monitor xiao_rp2350
```

Exit the monitor:

```text
Ctrl+]
```

## Manual UF2 Download Mode

Use this only as the recovery path when automatic flashing cannot enter UF2
mode:

1. Hold `BOOTSEL`.
2. Plug in USB, or press `RESET`.
3. Wait for the `RP2350` storage volume, then rerun the flash command.
