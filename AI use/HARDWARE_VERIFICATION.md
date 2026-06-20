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
