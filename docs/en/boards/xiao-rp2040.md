# XIAO RP2040 Board Notes

This page records the verified Zephyr behavior for Seeed Studio XIAO RP2040.

One-sentence summary: XIAO RP2040 flashing still uses UF2 mass-storage mode,
but the repository firmware can request UF2 mode automatically after it has
been installed once.

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

After the repository `xiao_rp2040/blinky` firmware is installed, the CLI opens
the board's USB CDC serial port at 1200 baud. The running firmware treats that
as a bootloader request, reboots into UF2 mode, and then Zephyr's UF2 runner
copies the new firmware.

If the board is running older firmware that does not implement the 1200-baud
request, enter UF2 mode manually: hold BOOTSEL while plugging in USB, or hold
BOOTSEL and press RESET. On macOS, the drive commonly appears as
`/Volumes/RPI-RP2`. On Linux, Windows, or WSL2 USB pass-through setups, the name
or path can be different. The important signal is that the UF2 mass-storage
volume is mounted and visible to the environment running `west flash`.

If the board is not in UF2 mode, Zephyr reports:

```text
No matching UF2 partitions found
```

The repository CLI tries the automatic 1200-baud request first. If it cannot
find a running USB CDC serial port or cannot see the UF2 volume after the
request, it adds a BOOTSEL recovery hint.

One-sentence summary: RP2040 flashing is still a UF2 file copy, and the serial
port is used only to ask the running repository firmware to enter UF2 mode.

## Expected Repeated Flashing Behavior

The verified behavior is:

- A first install from older firmware may require manual BOOTSEL entry so the
  UF2 volume is visible.
- After flashing, the board reboots into the application, the UF2 drive
  disappears, and the USB CDC serial port appears for monitor output.
- Consecutive second, third, and fourth
  `seeed-zephyr flash xiao_rp2040 --monitor` runs passed without manually
  entering UF2 mode again.
- Normal USB replug should continue to work as long as the board boots the
  repository firmware and exposes one USB CDC serial port. If it does not,
  manual BOOTSEL remains the recovery path.

One-sentence summary: manual BOOTSEL is needed for first install or recovery,
not for normal repeated flashing after this repository firmware is running.

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
- Second, third, and fourth consecutive `seeed-zephyr flash xiao_rp2040 --monitor`
  runs succeeded without manual BOOTSEL entry by requesting UF2 mode through the
  USB CDC serial port at 1200 baud.

The detailed hardware record lives in
[`AI use/HARDWARE_VERIFICATION.md`](../../../AI%20use/HARDWARE_VERIFICATION.md).

One-sentence summary: the example is hardware-tested, and repeated flashing is
verified to work without manual BOOTSEL after the repository firmware is
installed.
