# XIAO RP2040 Board Notes

This page records the verified Zephyr behavior for Seeed Studio XIAO RP2040.

One-sentence summary: XIAO RP2040 flashing uses UF2 mass-storage mode, so the
UF2 volume must be visible before each flash command can copy the firmware.

## Verified Repository Example

Repository example:

```sh
examples/boards/xiao_rp2040/blinky
```

Build, flash, and open the serial monitor:

```sh
seeed-zephyr flash xiao_rp2040 --monitor
```

When one USB serial device is visible after flashing, the CLI can auto-detect
the port. If multiple USB serial devices are connected, pass the port
explicitly:

```sh
seeed-zephyr flash xiao_rp2040 --monitor --port /dev/cu.usbmodem1101
```

One-sentence summary: use the normal CLI command first, and add `--port` only
when auto-detection cannot choose one serial device.

## UF2 Flashing Behavior

XIAO RP2040 uses a UF2 bootloader. In practical terms, the bootloader exposes
the board as a temporary USB storage drive. Zephyr's UF2 runner then copies the
generated `zephyr.uf2` file to that drive.

To enter UF2 mode, hold BOOTSEL while plugging in USB, or hold BOOTSEL and press
RESET. On macOS, the drive commonly appears as `/Volumes/RPI-RP2`. On Linux,
Windows, or WSL2 USB pass-through setups, the name or path can be different.
The important signal is that the UF2 mass-storage volume is mounted and visible
to the environment running `west flash`.

If the board is not in UF2 mode, Zephyr reports:

```text
No matching UF2 partitions found
```

The repository CLI adds a BOOTSEL hint for this class of flash failure.

One-sentence summary: RP2040 flashing is a file copy to a bootloader drive, not
a serial-port upload.

## Expected Repeated Flashing Behavior

The verified behavior is:

- `seeed-zephyr flash xiao_rp2040 --monitor` succeeds when the board is in UF2
  mode and the UF2 volume is mounted.
- After flashing, the board reboots into the application, the UF2 drive
  disappears, and the USB CDC serial port appears for monitor output.
- A second consecutive flash without entering UF2 mode again fails with
  `No matching UF2 partitions found` and the CLI BOOTSEL hint.

One-sentence summary: unlike the verified XIAO SAMD21 flow, the current RP2040
flow should be treated as requiring UF2 mode for each flash.

## Serial Monitor Behavior

The repository `xiao_rp2040/blinky` example enables a USB CDC ACM console. This
allows `seeed-zephyr flash xiao_rp2040 --monitor` to open pyserial miniterm
after a successful flash and show the repeated LED state lines.

Exit the monitor with:

```text
Ctrl+]
```

If the monitor does not open, wait for the board to re-enumerate after flashing,
check that the USB cable supports data, and pass `--port` when more than one USB
serial device is connected.

One-sentence summary: flashing uses the UF2 drive, while logging uses the USB
CDC serial port exposed by the flashed application.

## Verified Evidence

The repository has hardware evidence for `xiao_rp2040`:

- A flash attempt without UF2 mode produced the expected BOOTSEL/UF2 hint.
- `seeed-zephyr flash xiao_rp2040 --monitor` built the repository example,
  copied `zephyr.uf2` to `/Volumes/RPI-RP2`, and opened the serial monitor.
- Serial output showed repeated `LED state: OFF` and `LED state: ON` lines.
- A second consecutive flash without UF2 mode failed with the expected
  `No matching UF2 partitions found` behavior and BOOTSEL hint.

The detailed hardware record lives in
[`AI use/HARDWARE_VERIFICATION.md`](../../../AI%20use/HARDWARE_VERIFICATION.md).

One-sentence summary: the example is hardware-tested, but repeated flashing
still requires the RP2040 UF2 bootloader volume.
