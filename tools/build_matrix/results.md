# Board Build Matrix Results

Generated on: 2026-11-10

Values below come from real per-board repository example builds. The default example is `examples/boards/<board_id>/blinky`; board-specific overrides are listed in `board-overrides.tsv`. Replace the placeholder date when recording a formal validation pass.

| board id | vendor | example | final target | result (PASS/FAIL/UNSUPPORTED) | notes |
| --- | --- | --- | --- | --- | --- |
| xiao_esp32c3 | espressif | `examples/boards/xiao_esp32c3/hello_world` | `xiao_esp32c3` | PASS | Build succeeded. Hardware-tested example; see AI use/HARDWARE_VERIFICATION.md. XIAO ESP32-C3 has no on-board LED; hello_world validates the board/toolchain baseline without LED hardware. |
| xiao_esp32c5 | espressif | `examples/boards/xiao_esp32c5/blinky` | `xiao_esp32c5/esp32c5/hpcore` | PASS | Build succeeded. Hardware-tested example; see AI use/HARDWARE_VERIFICATION.md. blinky validates the XIAO ESP32-C5 board/toolchain baseline through the user LED and USB serial console. |
| xiao_esp32c6 | espressif | `examples/boards/xiao_esp32c6/blinky` | `xiao_esp32c6/esp32c6/hpcore` | PASS | Build succeeded. Hardware-tested example; see AI use/HARDWARE_VERIFICATION.md. |
| xiao_esp32s3 | espressif | `examples/boards/xiao_esp32s3/blinky` | `xiao_esp32s3/esp32s3/procpu` | PASS | Build succeeded. Hardware-tested example; see AI use/HARDWARE_VERIFICATION.md. |
| xiao_mg24 | silabs | `examples/boards/xiao_mg24/blinky` | `xiao_mg24` | PASS | Build succeeded. Hardware-tested example; see AI use/HARDWARE_VERIFICATION.md. |
| xiao_nrf52840 | nordic | `examples/boards/xiao_nrf52840/blinky` | `xiao_ble` | PASS | Build succeeded. Hardware-tested example; see AI use/HARDWARE_VERIFICATION.md. |
| xiao_nrf54l15 | nordic | `examples/boards/xiao_nrf54l15/blinky` | `xiao_nrf54l15/nrf54l15/cpuapp` | PASS | Build succeeded. Hardware-tested example; see AI use/HARDWARE_VERIFICATION.md. |
| xiao_nrf54lm20a | nordic | `examples/boards/xiao_nrf54lm20a/blinky` | `xiao_nrf54lm20a/nrf54lm20a/cpuapp` | PASS | Build succeeded. Hardware-tested example; see AI use/HARDWARE_VERIFICATION.md. blinky validates the XIAO nRF54LM20A board/toolchain baseline through the blue LED and the SAMD11 USB console. |
| xiao_nrf54lm20b | nordic | `examples/boards/xiao_nrf54lm20b/blinky` | `xiao_nrf54lm20b/nrf54lm20b/cpuapp` | PASS | Build succeeded. Hardware-tested example; see AI use/HARDWARE_VERIFICATION.md. Signed USB upload, application serial output, and consecutive uploads through automatic 1200-baud loader entry passed. |
| xiao_ra4m1 | renesas | `examples/boards/xiao_ra4m1/blinky` | `xiao_ra4m1` | PASS | Build succeeded. Hardware-tested example; see AI use/HARDWARE_VERIFICATION.md. |
| xiao_rp2040 | raspberrypi | `examples/boards/xiao_rp2040/blinky` | `xiao_rp2040` | PASS | Build succeeded. Hardware-tested example; see AI use/HARDWARE_VERIFICATION.md. |
| xiao_rp2350 | raspberrypi | `examples/boards/xiao_rp2350/blinky` | `xiao_rp2350/rp2350a/m33_0` | PASS | Build succeeded. Hardware-tested example; see AI use/HARDWARE_VERIFICATION.md. |
| xiao_samd21 | microchip | `examples/boards/xiao_samd21/blinky` | `seeeduino_xiao` | PASS | Build succeeded. Hardware-tested example; see AI use/HARDWARE_VERIFICATION.md. |
| xiao_stm32c5 | st | `examples/boards/xiao_stm32c5/blinky` | `xiao_stm32c5/stm32c5a3xx` | PASS | Build succeeded. Hardware-tested example; see AI use/HARDWARE_VERIFICATION.md. blinky validates the XIAO STM32C5 board/toolchain baseline through the user LED and a TinyUF2 image. |
