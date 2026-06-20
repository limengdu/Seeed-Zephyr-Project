# Board Build Matrix Results

Generated on: 2026-06-20

Values below come from real per-board repository example builds. The default example is `examples/boards/<board_id>/blinky`; board-specific overrides are listed in `board-overrides.tsv`. Replace the placeholder date when recording a formal validation pass.

| board id | vendor | example | final target | result (PASS/FAIL/UNSUPPORTED) | notes |
| --- | --- | --- | --- | --- | --- |
| xiao_esp32c3 | espressif | `examples/boards/xiao_esp32c3/hello_world` | `xiao_esp32c3` | PASS | Build succeeded. XIAO ESP32C3 has no on-board LED; hello_world validates the board/toolchain baseline without LED hardware. |
| xiao_esp32c5 | espressif | `examples/boards/xiao_esp32c5/hello_world` | `xiao_esp32c5` | UNSUPPORTED | Zephyr v4.4.0 does not provide a xiao_esp32c5 board target; the repository keeps the demo record until the selected baseline supports the board. |
| xiao_esp32c6 | espressif | `examples/boards/xiao_esp32c6/blinky` | `xiao_esp32c6/esp32c6/hpcore` | PASS | Build succeeded. |
| xiao_esp32s3 | espressif | `examples/boards/xiao_esp32s3/blinky` | `xiao_esp32s3/esp32s3/procpu` | PASS | Build succeeded. |
| xiao_mg24 | silabs | `examples/boards/xiao_mg24/blinky` | `xiao_mg24` | PASS | Build succeeded. |
| xiao_nrf52840 | nordic | `examples/boards/xiao_nrf52840/blinky` | `xiao_ble` | PASS | Build succeeded. |
| xiao_nrf54l15 | nordic | `examples/boards/xiao_nrf54l15/blinky` | `xiao_nrf54l15/nrf54l15/cpuapp` | PASS | Build succeeded. |
| xiao_ra4m1 | renesas | `examples/boards/xiao_ra4m1/blinky` | `xiao_ra4m1` | PASS | Build succeeded. |
| xiao_rp2040 | raspberrypi | `examples/boards/xiao_rp2040/blinky` | `xiao_rp2040` | PASS | Build succeeded. Hardware-tested example; see AI use/HARDWARE_VERIFICATION.md. |
| xiao_rp2350 | raspberrypi | `examples/boards/xiao_rp2350/blinky` | `xiao_rp2350/rp2350a/hazard3` | PASS | Build succeeded. |
| xiao_samd21 | microchip | `examples/boards/xiao_samd21/blinky` | `seeeduino_xiao` | PASS | Build succeeded. Hardware-tested example; see AI use/HARDWARE_VERIFICATION.md. |
