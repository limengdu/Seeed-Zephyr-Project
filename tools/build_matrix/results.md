# Board Build Matrix Results

Generated on: 2026-06-20

Values below come from real per-board baseline builds. The default sample is `samples/basic/blinky`; board-specific overrides are listed in `board-overrides.tsv`. Replace the placeholder date when recording a formal validation pass.

| board id | vendor | sample | final target | result (PASS/FAIL/UNSUPPORTED) | notes |
| --- | --- | --- | --- | --- | --- |
| xiao_esp32c3 | espressif | `samples/hello_world` | `xiao_esp32c3` | PASS | Build succeeded. XIAO ESP32C3 has no on-board LED; hello_world validates the board/toolchain baseline without LED hardware. |
| xiao_esp32c5 | espressif | `samples/basic/blinky` | `xiao_esp32c5` | UNSUPPORTED | Zephyr baseline does not provide this board target.<br>First useful lines:<br>-- west build: making build dir /Users/mengdu/zephyrproject/zephyr/build pristine<br>-- west build: generating a build system<br>Loading Zephyr default modules (Zephyr base).<br>-- Application: /Users/mengdu/zephyrproject/zephyr/samples/basic/blinky<br>-- CMake version: 4.3.3<br>Last useful lines:<br>  /Users/mengdu/zephyrproject/zephyr/share/zephyr-package/cmake/ZephyrConfig.cmake:66 (include)<br>  /Users/mengdu/zephyrproject/zephyr/share/zephyr-package/cmake/ZephyrConfig.cmake:92 (include_boilerplate)<br>  CMakeLists.txt:4 (find_package)<br>-- Configuring incomplete, errors occurred!<br>FATAL ERROR: command exited with status 1: /opt/homebrew/bin/cmake -DWEST_PYTHON=/Users/mengdu/zephyrproject/.venv/bin/python3.14 -B/Users/mengdu/zephyrproject/zephyr/build -GNinja -DBOARD=xiao_esp32c5 -S/Users/mengdu/zephyrproject/zephyr/samples/basic/blinky |
| xiao_esp32c6 | espressif | `samples/basic/blinky` | `xiao_esp32c6/esp32c6/hpcore` | PASS | Build succeeded. |
| xiao_esp32s3 | espressif | `samples/basic/blinky` | `xiao_esp32s3/esp32s3/procpu` | PASS | Build succeeded. |
| xiao_mg24 | silabs | `samples/basic/blinky` | `xiao_mg24` | PASS | Build succeeded. |
| xiao_nrf52840 | nordic | `samples/basic/blinky` | `xiao_ble` | PASS | Build succeeded. |
| xiao_nrf54l15 | nordic | `samples/basic/blinky` | `xiao_nrf54l15/nrf54l15/cpuapp` | PASS | Build succeeded. |
| xiao_ra4m1 | renesas | `samples/basic/blinky` | `xiao_ra4m1` | PASS | Build succeeded. |
| xiao_rp2040 | raspberrypi | `samples/basic/blinky` | `xiao_rp2040` | PASS | Build succeeded. |
| xiao_rp2350 | raspberrypi | `samples/basic/blinky` | `xiao_rp2350/rp2350a/hazard3` | PASS | Build succeeded. |
| xiao_samd21 | microchip | `samples/basic/blinky` | `seeeduino_xiao` | PASS | Build succeeded. |
