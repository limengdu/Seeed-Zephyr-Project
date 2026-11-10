# XIAO STM32C5 Zephyr Development Guide

This page records board-level Zephyr development notes for Seeed Studio
XIAO STM32C5 on the Zephyr v4.5.0 baseline. For full setup, build, and flashing
commands, see [Getting Started](../getting-started.md).

## TinyUF2 Image

The factory TinyUF2 bootloader occupies the first 32 KiB of flash. The
application starts at `0x08008000` and the build output is `zephyr.uf2` with
family id `0x00C5C5C5`.

```conf
CONFIG_BUILD_OUTPUT_UF2=y
CONFIG_BUILD_OUTPUT_UF2_FAMILY_ID="0x00C5C5C5"
```

Upload copies that file onto the boot volume:

```sh
seeed-zephyr flash xiao_stm32c5 --monitor
```

The factory volume name on this board is `XIAOC5BOOT`. Upstream board notes also
use `XIAOSTM32C5`. Upload accepts either label, and a volume whose
`INFO_UF2.TXT` names this board (`Model: Seeed XIAO C5`,
`Board-ID: STM32C5A3-XIAO-C5`).

## USB Clock and Pins

The v4.5.0 board definition enables the USB device and leaves the 48 MHz clock
mux disabled and the USB pin settings unset. Startup clears the clock
configuration left by the bootloader, so the application does not appear on USB
after the UF2 copy.

The blinky overlay enables the existing `clk48` node, selects the board's 48 MHz
HSE, and assigns PA11 (USB DM) and PA12 (USB DP):

```dts
&clk48 {
	clocks = <&rcc STM32_SRC_HSE CK48_SEL(3)>;
	status = "okay";
};

&usb {
	pinctrl-0 = <&usb_dm_pa11 &usb_dp_pa12>;
	pinctrl-names = "default";
};
```

A custom application on this baseline keeps the same overlay at
`boards/xiao_stm32c5_stm32c5a3xx.overlay`. The pin names come from the STM32
devicetree shipped with the Zephyr modules.

Reference: `examples/boards/xiao_stm32c5/blinky/boards/xiao_stm32c5_stm32c5a3xx.overlay`.

## Application USB Identity

The console is USB CDC ACM at 115200 baud. Upload finds the running application
by USB id `2886:00C5`.

```conf
CONFIG_UART_LINE_CTRL=y
CONFIG_CDC_ACM_SERIAL_VID=0x2886
CONFIG_CDC_ACM_SERIAL_PID=0x00C5
CONFIG_CDC_ACM_SERIAL_MANUFACTURER_STRING="Seeed Studio"
CONFIG_CDC_ACM_SERIAL_PRODUCT_STRING="XIAO STM32C5"
```

## Repeated Upload

While this application is running, upload opens the CDC port at 1200 baud. The
application reads `UART_LINE_CTRL_BAUD_RATE` every 50 ms. At 1200 baud it writes
`0xf01669ef` to the last word of SRAM and resets into the factory bootloader.

The bootloader is a mass-storage device and has no serial port, so the 1200 baud
request is handled by the running application. The first upload onto a board
that is not running this application uses manual entry below. After this image
is running, the next upload sends the 1200 baud request on its own.

Reference: `examples/boards/xiao_stm32c5/blinky/src/main.c`.

## Manual Bootloader Entry

Use this path for the first image, or when the application serial port is not
visible:

1. Press RESET twice within about half a second.
2. Wait for the `XIAOC5BOOT` or `XIAOSTM32C5` volume.
3. Run the flash command again. An already mounted volume is used directly.

## BOOT Pad

The BOOT pad (PH2) is sampled while the board resets. Leave it released during
power-on and reset.

## Project Files

A project created from release 0.5.4 or later includes the overlay, the USB
identity, and the 1200 baud reset handling. Create a fresh `blinky` project
after updating to that release.
