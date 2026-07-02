# Grove Ultrasonic basic_read

A board-agnostic Zephyr example for the **Grove - Ultrasonic Distance Sensor**.

The Grove Ultrasonic Ranger uses one `SIG` pin for both trigger and echo. The
application sends a 12 us trigger pulse on the selected XIAO D pin, switches the
same pin to input, measures the echo pulse width, and prints the calculated
distance.

## Wiring

Connect the Grove Ultrasonic module to a XIAO Grove digital port whose signal
line maps to the selected D pin.

Default wiring:

| Grove pin | XIAO pin |
| --- | --- |
| SIG | D2 |
| VCC | 3V3 |
| GND | GND |

## Build

Use the default `signal=D2` pin:

```bash
seeed-zephyr build xiao_esp32c6 grove/grove_ultrasonic_distance_sensor/basic_read
```

Choose another signal pin:

```bash
seeed-zephyr build xiao_nrf52840 grove/grove_ultrasonic_distance_sensor/basic_read --pin D3
seeed-zephyr build xiao_rp2040 grove/grove_ultrasonic_distance_sensor/basic_read --pin signal=D3
```

## Expected output

Once per second:

```text
Distance: 24.7 cm  Echo: 1453 us
```

`Distance: timeout` means the board did not see the echo pulse within the
measurement window.

## Reference

- [Grove - Ultrasonic Ranger | Seeed Studio Wiki](https://wiki.seeedstudio.com/Grove-Ultrasonic_Ranger/)
