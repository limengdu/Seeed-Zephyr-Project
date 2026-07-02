# metadata

## English

This directory contains structured product metadata for boards, Grove modules,
expansion boards, form factors, and validation status.

- `boards/` — XIAO board identity, target, plus per-board `reserved_pins`,
  `analog_pins`, and a `pin_map` baseline.
- `grove_modules/` — Grove module identity, interface, and Zephyr driver/Kconfig needs.
- `expansion_boards/` — expansion board identity and on-board resources.
- `form_factors/` — physical pin layout (e.g. the XIAO 14-pin footprint), the data
  source for the editor extension's pinout diagram.
- `status/` — the Grove example x board build/hardware status matrix.

Metadata should describe identity, discovery, category, interface, and validation
links. Hardware pin truth should live in Zephyr-native files such as Devicetree,
overlays, and shields when those files are the correct source of truth.

## 中文

这个目录保存开发板、Grove 模块、扩展板、形态因子与验证状态的结构化产品 metadata。

- `boards/`——XIAO 开发板身份与 target，以及按板的 `reserved_pins`、`analog_pins`、`pin_map` 基准。
- `grove_modules/`——Grove 模块身份、接口与所需 Zephyr 驱动/Kconfig。
- `expansion_boards/`——扩展板身份与板载资源。
- `form_factors/`——物理引脚排布（如 XIAO 14 脚封装），是编辑器插件引脚图的数据源。
- `status/`——Grove 示例 × 板子 的构建/硬件状态矩阵。

Metadata 应描述身份、发现信息、分类、接口和验证链接。当硬件引脚事实应由 Zephyr
原生文件表达时，应放在 Devicetree、overlay 或 shield 中。
