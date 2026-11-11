# Hardware Verification / 硬件验证

## English

This file records hardware observations captured by the `seeed-zephyr`
CLI. Build-only examples become hardware-tested only after real board behavior
is observed and recorded.

Entry format:

```text
## ISO-8601 timestamp - board_id - PASS/FAIL

- Board: `board_id`
- Example: `examples/...`
- Result: `PASS/FAIL`
- Serial output: ...
- Notes: ...
```

## 中文

这个文件记录 `seeed-zephyr` CLI 捕获的真实硬件观察结果。只有在真实开发板现象被观察并记录后，build-only 示例才能升级为 hardware-tested。

记录格式：

```text
## ISO-8601 时间 - board_id - PASS/FAIL

- Board: `board_id`
- Example: `examples/...`
- Result: `PASS/FAIL`
- Serial output: ...
- Notes: ...
```

## 2026-11-11 - xiao_nrf54lm20b - PASS

- Board: `xiao_nrf54lm20b`
- Example: `examples/boards/xiao_nrf54lm20b/blinky`
- Result: `PASS`
- Serial output: `*** Booting Zephyr OS build v4.5.0 ***`; `*** Seeed XIAO Zephyr Base | board: xiao_nrf54lm20b | demo: blinky ***`; repeated `LED state: OFF` and `LED state: ON` after all three successful uploads.
- Notes: Built with Zephyr v4.5.0 / SDK 1.0.1. Manual Button 0 (P0.09) plus RESET entered the factory loader (`2886:0013`, `CDC ACM serial backend`). A 32-byte SHA-256 transfer digest and 64-byte chunks uploaded the compact signed image (78465 bytes), which booted as application USB id `2886:8013`, product `XIAO nRF54LM20B`, on `/dev/cu.usbmodem1201`. Consecutive 9600/1200-baud requests entered the loader automatically. A full `zephyr.signed.confirmed.bin` upload (1826816 bytes) then booted successfully. The final run used the production CLI command `python3 tools/cli/seeed_zephyr.py flash xiao_nrf54lm20b --port /dev/cu.usbmodem1201`, rebuilt the example, uploaded the full confirmed image with the bundled SMP helper, and detected the application serial port after reset. The serial capture after that run contains the Zephyr boot banner and alternating LED state lines.

## 2026-11-10 - xiao_stm32c5 - PASS

- Board: `xiao_stm32c5`
- Example: `examples/boards/xiao_stm32c5/blinky`
- Result: `PASS`
- Serial output: `*** Booting Zephyr OS build v4.5.0 ***`; `*** Seeed XIAO Zephyr Base | board: xiao_stm32c5 | demo: blinky ***`; repeated `LED state: OFF` and `LED state: ON` after both uploads.
- Notes: Built `zephyr.uf2` (94208 bytes, start address `0x08008000`, family id `0x00C5C5C5`) with the USB clock/pin overlay and application USB id `2886:00C5`. The first upload copied the image to `/Volumes/XIAOC5BOOT` after manual double RESET entry, and the application enumerated on `/dev/cu.usbmodem1201`. The consecutive upload requested TinyUF2 through that port at 1200 baud, detected the boot volume, copied the image, and restored the application serial port automatically. Both serial captures contain the Zephyr boot banner and alternating LED state lines.

## 2026-11-10 - xiao_nrf54lm20a - PASS

- Board: `xiao_nrf54lm20a`
- Example: `examples/boards/xiao_nrf54lm20a/blinky`
- Result: `PASS`
- Notes: The board tester confirmed that the published blinky example passed physical-board testing through the VS Code extension.

## 2026-11-10T00:00:00+08:00 - xiao_esp32c5 - PASS

- Board: `xiao_esp32c5`
- Example: `examples/boards/xiao_esp32c5/blinky`
- Result: `PASS`
- Serial output: `*** Booting Zephyr OS build v4.5.0 ***`; repeated `LED state: OFF` and `LED state: ON`
- Notes: Upload wrote and verified 135296 bytes on `/dev/cu.usbmodem1201` and finished with an RTS hard reset. The serial console then showed the Zephyr v4.5.0 boot banner followed by repeated LED state lines, and the user LED (GPIO27, active low) blinked. The plugin test of the published release passed afterwards. One serial monitor holding the port blocks the reset, so the extension closes its earlier Upload and Monitor terminals before a new upload or monitor.

## 2026-06-20T11:23:51+08:00 - xiao_esp32c6 - PASS

- Board: `xiao_esp32c6`
- Example: `examples/boards/xiao_esp32c6/blinky`
- Result: `PASS`
- Serial output: `*** Booting Zephyr OS build v4.4.0 ***`; repeated `LED state: OFF` and `LED state: ON`
- Notes: `seeed-zephyr flash xiao_esp32c6 --monitor` built the repository example, flashed `/dev/cu.usbmodem101`, verified the written hash, opened `idf_monitor`, and observed Zephyr boot plus LED state toggles in serial output.

## 2026-06-20T18:59:44+08:00 - xiao_samd21 - PASS

- Board: `xiao_samd21`
- Example: `examples/boards/xiao_samd21/blinky`
- Result: `PASS`
- Serial output: `*** Booting Zephyr OS build v4.4.0 ***`; repeated `LED state: OFF` and `LED state: ON`
- Notes: `seeed-zephyr flash xiao_samd21 --monitor` built the repository example, flashed through Zephyr's BOSSA runner, verified flash contents, opened pyserial miniterm on `/dev/cu.usbmodem1101`, and observed Zephyr boot plus LED state toggles. A second consecutive `seeed-zephyr flash xiao_samd21 --monitor` run passed without manual reset.

## 2026-06-20T19:37:00+08:00 - xiao_rp2040 - PASS

- Board: `xiao_rp2040`
- Example: `examples/boards/xiao_rp2040/blinky`
- Result: `PASS`
- Serial output: repeated `LED state: OFF` and `LED state: ON`
- Notes: `seeed-zephyr flash xiao_rp2040 --monitor` first produced the expected BOOTSEL/UF2 hint when the board was running firmware without automatic UF2 request support and no UF2 volume was mounted. After the board entered UF2 mode manually once, the command built the repository example, copied `zephyr.uf2` to `/Volumes/RPI-RP2`, opened pyserial miniterm on `/dev/cu.usbmodem1101`, and observed repeated LED state output. The repository firmware then handled USB CDC 1200-baud UF2 requests. Second, third, and fourth consecutive `seeed-zephyr flash xiao_rp2040 --monitor` runs passed without manual BOOTSEL entry: each run requested UF2 mode via `/dev/cu.usbmodem1101`, detected `/Volumes/RPI-RP2`, copied `zephyr.uf2`, reopened pyserial miniterm, and observed repeated LED state output.

## 2026-06-20T21:49:00+08:00 - xiao_rp2350 - PASS

- Board: `xiao_rp2350`
- Example: `examples/boards/xiao_rp2350/blinky`
- Result: `PASS`
- Serial output: repeated `LED state: OFF` and `LED state: ON`
- Notes: `xiao_rp2350/rp2350a/hazard3` built and copied by UF2, but did not enumerate a USB CDC serial device after flashing. `xiao_rp2350/rp2350a/m33` built, copied `zephyr.uf2` to `/Volumes/RP2350`, enumerated `/dev/cu.usbmodem1101` as `Seeed XIAO RP2350 blinky`, opened pyserial miniterm through `seeed-zephyr flash xiao_rp2350 --monitor`, and observed repeated LED state output. The repository firmware handled USB CDC 1200-baud UF2 requests and re-entered UF2 automatically.

## 2026-06-20T23:13:50+08:00 - xiao_nrf52840 - PASS

- Board: `xiao_nrf52840`
- Example: `examples/boards/xiao_nrf52840/blinky`
- Result: `PASS`
- Serial output: repeated `LED state: OFF` and `LED state: ON`
- Notes: `seeed-zephyr flash xiao_nrf52840 --monitor` built the repository example, requested UF2 mode via `/dev/cu.usbmodem1101` at 1200 baud, detected `/Volumes/XIAO-SENSE`, copied `zephyr.uf2` through Zephyr's UF2 runner, waited for the UF2 volume to detach, opened pyserial miniterm on `/dev/cu.usbmodem1101`, and observed repeated LED state output. A consecutive run passed without double-tapping RESET.

## 2026-06-21T09:37:05+08:00 - xiao_nrf54l15 - PASS

- Board: `xiao_nrf54l15`
- Example: `examples/boards/xiao_nrf54l15/blinky`
- Result: `PASS`
- Serial output: n/a
- Notes: Hardware test reported `seeed-zephyr flash xiao_nrf54l15 --monitor` working normally.

## 2026-06-21T09:58:49+08:00 - xiao_mg24 - PASS

- Board: `xiao_mg24`
- Example: `examples/boards/xiao_mg24/blinky`
- Result: `PASS`
- Serial output: `*** Booting Zephyr OS build v4.4.0 ***`; repeated `LED state: OFF` and `LED state: ON`
- Notes: Installed the Silicon Labs `EFR32MG24B220F1536IM48` CMSIS pack for pyOCD, then `seeed-zephyr flash xiao_mg24 --monitor` built the repository example, flashed `/Users/mengdu/zephyrproject/build/zephyr/zephyr.hex` through Zephyr's `pyocd` runner, opened pyserial miniterm on `/dev/cu.usbmodem71E9F3B93`, and observed repeated LED state output.

## 2026-06-22T17:13:26+08:00 - xiao_esp32s3 - PASS

- Board: `xiao_esp32s3`
- Example: `examples/boards/xiao_esp32s3/blinky`
- Result: `PASS`
- Serial output: n/a
- Notes: Hardware test reported `seeed-zephyr flash xiao_esp32s3 --monitor` working normally.

## 2026-06-22T17:13:26+08:00 - xiao_esp32c3 - PASS

- Board: `xiao_esp32c3`
- Example: `examples/boards/xiao_esp32c3/hello_world`
- Result: `PASS`
- Serial output: n/a
- Notes: Hardware test reported `seeed-zephyr flash xiao_esp32c3 --monitor` working normally.

## 2026-06-22T17:13:26+08:00 - xiao_ra4m1 - PASS

- Board: `xiao_ra4m1`
- Example: `examples/boards/xiao_ra4m1/blinky`
- Result: `PASS`
- Serial output: n/a
- Notes: Hardware test reported `seeed-zephyr flash xiao_ra4m1 --monitor` working normally over the USB DFU bootloader.
