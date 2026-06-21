# XIAO RA4M1 Zephyr Development Guide

This page records XIAO RA4M1 board-specific development notes. For the full
command flow, see [Getting Started](../getting-started.md).

## USB DFU Flashing

Common command:

```sh
seeed-zephyr flash xiao_ra4m1 --monitor
```

Setup installs `dfu-util` when `xiao_ra4m1` is selected, or when full setup is
run without selecting a board. The CLI generates a bin file for the board USB
DFU bootloader and uploads it with `dfu-util`.

For the first repository firmware install, if the current firmware cannot enter
DFU automatically, enter DFU bootloader manually:

1. Hold Boot.
2. Tap Reset.
3. Keep holding Boot for about 1 to 2 seconds after releasing Reset.
4. Run the flash command again.

## Application Start Address

The RA4M1 board DFU bootloader occupies the first 16 KB of flash. Zephyr examples
must keep:

```conf
CONFIG_FLASH_LOAD_OFFSET=0x4000
```

## Flash Again Without Boot

Custom RA4M1 examples need these settings if later flashes should not require
manual DFU entry:

```conf
CONFIG_REBOOT=y
CONFIG_UART_LINE_CTRL=y
CONFIG_USB_DEVICE_STACK_NEXT=y
CONFIG_CDC_ACM_SERIAL_INITIALIZE_AT_BOOT=y
```

The application should detect a `1200` baud request on USB CDC serial, then:

1. Write `0x07738135` to `R_SYSTEM->VBTBKR[0]`.
2. Clear `R_USB_FS0->SYSCFG_b.DPRPU`.
3. Call `sys_reboot(SYS_REBOOT_COLD)`.

The repository baseline example already includes this entry path and can be used
as a reference for custom examples.

## RA USB Boot State

If the host sees `RA USB Boot` or `045B:0261`, the board is in Renesas ROM
bootloader, not the Seeed USB DFU device used by `dfu-util`. Tap Reset once to
return to the running application.

## Serial Monitor

Open the monitor:

```sh
seeed-zephyr monitor xiao_ra4m1
```

Exit monitor:

```text
Ctrl+]
```

## Debugging

Zephyr debug defaults to J-Link and requires an external debugger connected to
the SWD pads on the bottom of the board. Normal flashing does not require J-Link.

Reference: [Zephyr XIAO RA4M1 documentation](https://docs.zephyrproject.org/latest/boards/seeed/xiao_ra4m1/doc/index.html).
