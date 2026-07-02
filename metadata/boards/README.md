# metadata/boards

## English

This directory contains authored metadata for XIAO boards.

Each file should identify one board, its display name, vendor, Zephyr target,
chip information, and product-facing notes. Build and hardware status should be
derived from validation evidence, not guessed.

Optional per-board pin fields support the Grove framework and the pinout diagram:

- `reserved_pins` — pins occupied by system functions (e.g. `console-uart` on D6/D7).
- `analog_pins` — pads with ADC capability on this board.
- `pin_map` — Dn -> chip pin baseline used to audit the upstream connector dtsi;
  `pin_map_source` records where it came from.

## 中文

这个目录保存 XIAO 开发板的人工编写 metadata。

每个文件应标识一块开发板，包括显示名称、vendor、Zephyr target、芯片信息和面向产品的说明。构建和硬件状态应来自验证证据，而不是猜测。

按板可选的引脚字段用于支持 Grove 框架与引脚图：

- `reserved_pins`——被系统功能占用的引脚（如 D6/D7 的 `console-uart`）。
- `analog_pins`——该板具备 ADC 能力的焊盘。
- `pin_map`——Dn → 芯片引脚基准表，用于审计上游 connector dtsi；`pin_map_source` 记录其来源。
