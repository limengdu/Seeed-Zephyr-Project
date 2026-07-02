# metadata/form_factors

## English

This directory contains authored metadata for board form factors (physical footprints).

Each file describes one form factor: the set of pads, their type (gpio/power), the bus
assignments (I2C/UART/SPI), and the physical pad order used by tools that render a pinout.
Board metadata references a form factor via its `form_factor` field.

`metadata/boards/*.yaml` may add per-board pin data alongside this layout:

- `reserved_pins`: pads occupied by a board's system function (such as the console UART),
  with a reason. Grove examples cannot use these pads.
- `analog_pins`: pads that have ADC capability on that specific board.
- `pin_map`: the physical pad to chip pin translation (e.g. D0 -> P0.02), used to audit the
  upstream Zephyr `seeed_xiao_connector.dtsi` and to enrich the pinout view.

## 中文

这个目录保存开发板物理封装（form factor）的人工编写 metadata。

每个文件描述一种封装：焊盘集合、类型（gpio/power）、总线分配（I2C/UART/SPI），以及工具渲染引脚图时使用的焊盘物理排列顺序。开发板 metadata 通过 `form_factor` 字段引用封装。

`metadata/boards/*.yaml` 可在该布局基础上补充按板引脚数据：

- `reserved_pins`：被板子系统功能占用（如控制台 UART）的焊盘及原因，Grove 示例不可使用这些焊盘。
- `analog_pins`：该板上具备 ADC 能力的焊盘。
- `pin_map`：物理焊盘到芯片引脚的翻译表（如 D0 -> P0.02），用于审计上游 Zephyr 的 `seeed_xiao_connector.dtsi` 并丰富引脚图展示。
