# Board Build Matrix Results

Generated on: 2026-06-19

Values below come from a real build run of `samples/basic/blinky`. Replace the placeholder date when recording a formal validation pass.

| board id | vendor | final target | result (PASS/FAIL) | notes |
| --- | --- | --- | --- | --- |
| xiao_esp32c3 | espressif | `xiao_esp32c3` | FAIL | west build exited with status 1.<br>First useful lines:<br>-- west build: making build dir /Users/mengdu/zephyrproject/zephyr/build pristine<br>-- west build: generating a build system<br>Loading Zephyr default modules (Zephyr base).<br>-- Application: /Users/mengdu/zephyrproject/zephyr/samples/basic/blinky<br>-- CMake version: 4.3.3<br>Last useful lines:<br>[43/233] Building C object zephyr/CMakeFiles/zephyr.dir/Users/mengdu/zephyrproject/modules/hal/espressif/components/efuse/src/esp_efuse_utility.c.obj<br>[44/233] Building C object zephyr/CMakeFiles/zephyr.dir/Users/mengdu/zephyrproject/modules/hal/espressif/components/efuse/src/esp_efuse_api.c.obj<br>[45/233] Building C object zephyr/CMakeFiles/zephyr.dir/soc/espressif/common/loader.c.obj<br>ninja: build stopped: subcommand failed.<br>FATAL ERROR: command exited with status 1: /opt/homebrew/bin/cmake --build /Users/mengdu/zephyrproject/zephyr/build |
| xiao_esp32c5 | espressif | `xiao_esp32c5` | FAIL | west build exited with status 1.<br>First useful lines:<br>-- west build: making build dir /Users/mengdu/zephyrproject/zephyr/build pristine<br>-- west build: generating a build system<br>Loading Zephyr default modules (Zephyr base).<br>-- Application: /Users/mengdu/zephyrproject/zephyr/samples/basic/blinky<br>-- CMake version: 4.3.3<br>Last useful lines:<br>  /Users/mengdu/zephyrproject/zephyr/share/zephyr-package/cmake/ZephyrConfig.cmake:66 (include)<br>  /Users/mengdu/zephyrproject/zephyr/share/zephyr-package/cmake/ZephyrConfig.cmake:92 (include_boilerplate)<br>  CMakeLists.txt:4 (find_package)<br>-- Configuring incomplete, errors occurred!<br>FATAL ERROR: command exited with status 1: /opt/homebrew/bin/cmake -DWEST_PYTHON=/Users/mengdu/zephyrproject/.venv/bin/python3.14 -B/Users/mengdu/zephyrproject/zephyr/build -GNinja -DBOARD=xiao_esp32c5 -S/Users/mengdu/zephyrproject/zephyr/samples/basic/blinky |
| xiao_esp32c6 | espressif | `xiao_esp32c6/esp32c6/hpcore` | PASS | Retried from xiao_esp32c6 after Zephyr board qualifier suggestion. |
| xiao_esp32s3 | espressif | `xiao_esp32s3/esp32s3/procpu` | PASS | Retried from xiao_esp32s3 after Zephyr board qualifier suggestion. |
| xiao_mg24 | silabs | `xiao_mg24` | PASS | Build succeeded. |
| xiao_nrf52840 | nordic | `xiao_ble` | PASS | Build succeeded. |
| xiao_nrf54l15 | nordic | `xiao_nrf54l15/nrf54l15/cpuapp` | PASS | Retried from xiao_nrf54l15 after Zephyr board qualifier suggestion. |
| xiao_ra4m1 | renesas | `xiao_ra4m1` | PASS | Build succeeded. |
| xiao_rp2040 | raspberrypi | `xiao_rp2040` | PASS | Build succeeded. |
| xiao_rp2350 | raspberrypi | `xiao_rp2350/rp2350a/hazard3` | PASS | Retried from xiao_rp2350 after Zephyr board qualifier suggestion. |
| xiao_samd21 | microchip | `seeeduino_xiao` | PASS | Build succeeded. |
