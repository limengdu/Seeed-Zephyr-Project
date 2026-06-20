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
