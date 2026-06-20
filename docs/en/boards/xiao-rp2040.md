# XIAO RP2040 Zephyr Development Guide

Minimal build, flash, and serial-monitor workflow for Seeed Studio XIAO RP2040.

## Quick Start

Baseline example:

```sh
examples/boards/xiao_rp2040/blinky
```

Build, flash, and open the serial monitor:

```sh
seeed-zephyr flash xiao_rp2040 --monitor
```

When `LED state: ON/OFF` repeats in the monitor, build, flashing, and serial
output are working.

## Daily Development Loop

1. Edit `examples/boards/xiao_rp2040/blinky/src/main.c`.
2. Run:

```sh
seeed-zephyr flash xiao_rp2040 --monitor
```

Exit the monitor:

```text
Ctrl+]
```

## When To Use BOOTSEL

Normal repeated flashing should not require pressing `BOOTSEL` every time.

Use manual UF2 mode only when:

- first flashing cannot enter download mode automatically;
- the running program does not handle USB CDC 1200-baud download requests;
- `No matching UF2 partitions found` appears;
- no serial port is visible, so the CLI cannot request automatic download mode.

Manual UF2 entry:

1. Hold `BOOTSEL`.
2. Plug in USB, or press `RESET`.
3. Wait for the `RPI-RP2` storage volume, then rerun the flash command.

## Custom Example Checklist

For a custom XIAO RP2040 example to keep button-free repeated flashing, keep:

- USB CDC serial output;
- USB CDC 1200-baud handling for UF2 entry;
- the RP2 boot mode retention snippet.

The repository CLI adds the snippet automatically. With direct `west build`, add
it yourself:

```sh
west build -p always -b xiao_rp2040 -S rp2-boot-mode-retention <your-app>
```

Reference implementation:

```sh
examples/boards/xiao_rp2040/blinky/src/main.c
```

## Common Issues

### Multiple Serial Ports

Pass the port explicitly:

```sh
seeed-zephyr flash xiao_rp2040 --monitor --port /dev/cu.usbmodem1101
```

### No Monitor Output

Check the USB cable, selected serial port, and whether the example enables USB
CDC serial output.

### BOOTSEL Is Needed Every Time

Flash `xiao_rp2040/blinky` first to confirm automatic repeated flashing works,
then carry the same USB CDC 1200-baud handling into the custom example.
