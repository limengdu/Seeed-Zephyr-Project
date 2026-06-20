# XIAO RP2040 Zephyr Development Guide

This page records only board-level Zephyr development notes for Seeed Studio
XIAO RP2040. For full setup, build, and flashing commands, see
[Getting Started](../getting-started.md).

## UF2 Flashing

XIAO RP2040 uses UF2 download mode. During normal development, do not copy UF2
files manually; run:

```sh
seeed-zephyr flash xiao_rp2040 --monitor
```

When using Zephyr commands directly, add the RP2 boot mode retention snippet at
build time:

```sh
west build -p always -b xiao_rp2040 -S rp2-boot-mode-retention <app>
west flash
```

The repository CLI adds this snippet automatically.

## Repeated Flashing Without BOOTSEL

Goal: after firmware is already running, the host can ask the board to enter UF2
mode through USB CDC serial before the next flash.

For a custom XIAO RP2040 example, handle these files:

- `prj.conf`: enable reboot, UART line control, USB CDC serial, and console.
- `app.overlay`: define `cdc_acm_uart0` and route `zephyr,console` to it.
- `src/main.c`: read `UART_LINE_CTRL_BAUD_RATE`; when the host opens USB CDC at
  `1200` baud, set `BOOT_MODE_TYPE_BOOTLOADER` and call `sys_reboot()`.
- Build command: use `-S rp2-boot-mode-retention`.

Key configuration:

```conf
CONFIG_REBOOT=y
CONFIG_UART_LINE_CTRL=y
CONFIG_SERIAL=y
CONFIG_CONSOLE=y
CONFIG_UART_CONSOLE=y
CONFIG_USB_DEVICE_STACK_NEXT=y
CONFIG_CDC_ACM_SERIAL_INITIALIZE_AT_BOOT=y
```

Key code shape:

```c
ret = uart_line_ctrl_get(cdc_acm, UART_LINE_CTRL_BAUD_RATE, &baudrate);
if (ret == 0 && baudrate == 1200) {
	bootmode_set(BOOT_MODE_TYPE_BOOTLOADER);
	k_sleep(K_MSEC(50));
	sys_reboot(SYS_REBOOT_COLD);
}
```

Reference implementation: `examples/boards/xiao_rp2040/blinky/src/main.c`.

## USB CDC Serial Output

Goal: make `printk()` output visible through the USB serial monitor.

Handle these files:

- `prj.conf`: enable `CONFIG_PRINTK`, `CONFIG_SERIAL`, `CONFIG_CONSOLE`,
  `CONFIG_UART_CONSOLE`, and USB CDC.
- `app.overlay`: route `zephyr,console` to `cdc_acm_uart0`.
- `src/main.c`: print runtime logs with `printk()`.

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
	};
};
```

Open the monitor:

```sh
seeed-zephyr monitor xiao_rp2040
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
3. Wait for the `RPI-RP2` storage volume, then rerun the flash command.
