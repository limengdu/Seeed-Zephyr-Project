# XIAO SAMD21 Board Notes

This page records the verified Zephyr behavior for Seeed Studio XIAO SAMD21.

One-sentence summary: after the verified repository `blinky` firmware is on the
board, repeated flashing should not require manually entering bootloader mode.

## Verified Repository Example

Repository example:

```sh
examples/boards/xiao_samd21/blinky
```

Build, flash, and open the serial monitor:

```sh
seeed-zephyr flash xiao_samd21 --monitor
```

When one USB serial device is visible, the CLI can auto-detect the port. If
multiple USB serial devices are connected, pass the port explicitly:

```sh
seeed-zephyr flash xiao_samd21 --monitor --port /dev/cu.usbmodem1101
```

One-sentence summary: use the normal CLI command first, and add `--port` only
when auto-detection cannot choose one serial device.

## Why Manual Reset Is Normally Not Needed

XIAO SAMD21 uses a BOSSA-compatible bootloader. In practical terms, the
bootloader is the small program that receives a new firmware image before the
main application starts.

SAMD21 boards commonly support a 1200-baud touch reset. This means the host
computer briefly opens the board's USB serial port at 1200 baud. The running
firmware sees that request and reboots into the bootloader. Zephyr's BOSSA
runner then uses `bossac` to write the new firmware.

The repository `xiao_samd21/blinky` example enables USB CDC ACM serial output
and gives the CDC ACM device the name expected by Zephyr's SAMD21 BOSSA reset
hook. That is why repeated flashing works after the verified firmware is
installed.

One-sentence summary: the running firmware must expose the right USB serial
device so Zephyr can ask the board to reboot into its bootloader.

## Expected Flashing Behavior

After the verified firmware is installed:

- The second, third, and later `seeed-zephyr flash xiao_samd21 --monitor` runs
  should not require double-clicking reset.
- Unplugging and plugging USB back in should not require manual bootloader
  entry, as long as the same verified firmware starts normally and the USB
  serial port appears again.
- If the board was previously flashed with firmware that does not expose the
  required USB CDC ACM behavior, one manual bootloader entry may be needed to
  install the verified firmware once.

One-sentence summary: once the correct firmware is running, repeated upload
should behave like a normal automatic upload flow.

## When Manual Bootloader Entry May Still Be Needed

Manual bootloader entry can still be needed if:

- the current firmware does not enable USB CDC ACM serial;
- the current firmware crashes before USB serial is ready;
- another firmware overwrote the verified repository example;
- the USB serial port is hidden by a bad cable, hub, operating-system issue, or
  another program holding the port;
- multiple serial devices are connected and the wrong port is selected.

To manually enter bootloader mode on XIAO SAMD21, double-click the reset button,
then rerun the flash command.

One-sentence summary: manual bootloader entry is a recovery path, not the
normal path for the verified repository example.

## Verified Evidence

The repository has hardware evidence for `xiao_samd21`:

- `seeed-zephyr flash xiao_samd21 --monitor` built, flashed, verified, and
  opened the serial monitor.
- Serial output showed Zephyr boot output and repeated LED state lines.
- A second consecutive `seeed-zephyr flash xiao_samd21 --monitor` run passed
  without manual reset.

The detailed hardware record lives in
[`AI use/HARDWARE_VERIFICATION.md`](../../../AI%20use/HARDWARE_VERIFICATION.md).

One-sentence summary: this behavior is based on real hardware validation, not
only on a successful build.
