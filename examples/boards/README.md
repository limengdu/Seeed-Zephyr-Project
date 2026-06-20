# examples/boards

## English

This directory contains one minimum board demo for each XIAO board tracked by
`metadata/boards/`.

Each board directory should contain at least one buildable Zephyr application or
an explicit unsupported record when the pinned Zephyr baseline lacks the board
target.

## 中文

这个目录为 `metadata/boards/` 中记录的每块 XIAO 开发板保存至少一个最小开发板 demo。

每个开发板目录都应包含至少一个可构建的 Zephyr 应用；如果当前固定 Zephyr 基线没有对应 board target，则必须明确记录 unsupported 状态。
