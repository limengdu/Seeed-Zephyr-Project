# Grove SCD41 basic_read

A board-agnostic Zephyr example for the **Grove - CO2, Temperature & Humidity Sensor (SCD41)**.

The source tree is written once and builds for every Seeed XIAO board that has an
upstream Zephyr board target. It relies on the upstream `seeed_xiao_connector`
abstraction: `app.overlay` references the `xiao_i2c` label, which each XIAO board
maps to its own I2C controller.

## Wiring

Plug the SCD41 module into a Grove I2C port on a XIAO expansion board, or wire it
to the XIAO I2C pins (D4 = SDA, D5 = SCL). No pin selection is needed because I2C
is a fixed bus on the XIAO footprint.

## Build

```bash
seeed-zephyr build xiao_esp32c6 grove/grove_scd41_co2_temperature_humidity_sensor/basic_read
seeed-zephyr build xiao_nrf52840 grove/grove_scd41_co2_temperature_humidity_sensor/basic_read
```

The same source builds on both boards without changes.

## Expected output

Every five seconds:

```
CO2: 604 ppm  Temp: 23.120000 C  RH: 45.670000 %
```
