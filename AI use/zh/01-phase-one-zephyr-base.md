# 阶段 1: 示例、项目、元数据与验证基础

## 1. 目标

阶段 1 建立这个仓库可信的基础。

阶段 1 既证明上游 Zephyr 能构建，也创建本仓库自己的示例和项目，让用户可以找到、构建、
烧录、学习、修改和贡献。

阶段 1 结束时，本仓库应能回答:

- 哪些 XIAO 开发板在这里有最小 Zephyr 示例？
- 哪些开发板能力在这里有示例？
- 哪些 Grove 模块在这里有示例？
- 哪些扩展板在这里有示例？
- 哪些完整项目在这里存在？
- 哪些示例是 build-only、hardware-tested、blocked、unsupported 或 unknown？
- 用哪个 Zephyr 版本作为证据？

一句话总结: 阶段 1 把分散的 Zephyr 支持变成经过验证的 XIAO + Grove 示例和项目基础。

## 2. 不可妥协的产品原则

这个仓库面向用户的核心资产是示例和项目。

Metadata、脚本、setup 说明、构建矩阵和未来生成器都服务于示例和项目。

阶段 1 的每个任务都应改善至少一项:

- 用户可以构建的示例
- 用户可以学习或修改的项目
- 示例或项目的验证证据
- 未来示例和项目的贡献质量
- 帮助用户发现或验证示例/项目的 metadata

一句话总结: 阶段 1 的优先事项，是让示例、项目、验证或贡献更清楚。

## 3. 仓库资产

### 开发板示例

开发板示例一次证明一种板级能力。

推荐类别:

- `hello_world`
- 板子有 LED 时的 `blinky`
- `gpio`
- `button`
- `serial_log`
- `i2c_scan`
- `spi_loopback` 或受支持 SPI 设备示例
- `uart`
- `adc_read`
- `pwm_fade`
- `usb_cdc`
- `ble_beacon`
- `wifi_scan` 或 `wifi_mqtt`
- `display_basic`
- `storage_basic`
- `low_power_basic`

一句话总结: 开发板示例是证明 XIAO 某项能力能在 Zephyr 下工作的最小证据。

### Grove 示例

Grove 示例展示一个 Grove 模块如何与 Zephyr 和 XIAO 配合。

推荐类别:

- 传感器的 `basic_read`
- 执行器的 `basic_control`
- 显示屏的 `display_text`
- 需要时用于确认地址的 `i2c_address_scan`
- 模块支持时的 `interrupt` 示例
- 需要设置时的 `calibration` 示例

一句话总结: Grove 示例应让用户插上模块后看到第一个有用结果。

### 扩展板示例

扩展板示例展示 XIAO 如何使用 shield、显示屏、按钮、电池功能或 Grove 端口布局。

一句话总结: 扩展板示例证明真实附加板被正确表达。

### 完整项目

项目把多个部件组合成真实场景。

示例:

- XIAO ESP32C6 + Grove AS5600 + display 旋钮界面
- XIAO nRF52840 + sensor + BLE 广播
- XIAO MG24 + button + low-power wake 流程
- XIAO ESP32S3 + display + Wi-Fi dashboard

项目应比最小示例更完整，可以包含 README、接线说明、配置选择、预期日志和已知限制。

一句话总结: 项目展示积木如何组合成真实用户结果。

## 4. Metadata 边界

Metadata 描述产品层事实:

- 显示名称
- 分类
- 接口
- 支持的示例/项目
- 文档链接
- 默认设置
- 验证状态
- 已知问题

Zephyr 原生文件描述硬件事实:

- Devicetree
- overlays
- shields
- Kconfig
- drivers

当 Zephyr shield 或 overlay 拥有硬件事实时，引脚路由应保留在这些 Zephyr 文件中。

一句话总结: metadata 帮助发现和验证；Zephyr 文件拥有硬件描述。

## 5. 建议目录结构

```text
examples/
  boards/
    xiao_esp32c3/
      hello_world/
    xiao_esp32c6/
      blinky/
      i2c_scan/
  grove/
    grove_as5600/
      basic_read/
  expansion_boards/
    xiao_expansion_board/
      display_basic/

projects/
  xiao_esp32c6_grove_as5600_display/

metadata/
  boards/
  grove_modules/
  expansion_boards/
  examples/
  projects/
  status/

boards/
  shields/

tools/
  validate_metadata/
  build_matrix/
  sync_status/

scripts/
  setup-macos.sh
  seeed-zephyr
  build-example.sh

docs/
  getting-started.md
  examples.md
  contributing-examples.md
```

一句话总结: `examples/` 和 `projects/` 是用户资产；metadata 和 tools 让它们可发现且可信。

## 6. 验证策略

验证必须基于证据。

状态:

- `hardware-tested`: 已构建、烧录并在真实硬件观察
- `build-only`: 编译成功，但尚未硬件测试
- `experimental`: 预期可用，但还不够稳定，不能推荐
- `blocked`: 已知问题阻止正常使用
- `unsupported`: 当前 Zephyr 基线或硬件不支持
- `unknown`: 尚未评估

规则:

- 状态字段由证据派生。
- 每个示例和项目都应有构建 target 和预期结果。
- hardware-tested 示例必须记录开发板、模块、Zephyr 版本、日期和观察输出。
- 社区示例可以先以 build-only 接收，有硬件证据后再提升状态。

一句话总结: 支持声明是有证据支撑的测试输出。

## 7. 社区贡献

仓库应准备好接收外部示例和项目。

每个贡献示例都应包含:

- 支持的开发板
- 需要的模块或扩展板
- 通过项目工具运行的构建命令
- 预期串口输出或可见行为
- 需要硬件时的接线说明
- 验证状态
- 已知限制

一句话总结: 欢迎社区示例，但它必须结构清晰，能构建、能审查、能验证。

## 8. 阶段 1 成功标准

阶段 1 成功条件:

- 至少五块有代表性的 XIAO 开发板拥有本仓库自己的示例
- 至少十个高频 Grove 模块拥有示例计划或初始示例
- 至少一块扩展板拥有可工作示例
- 至少三个完整项目存在，或已有明确验收标准
- 示例可以从仓库根目录构建
- metadata 验证通过
- 构建矩阵覆盖首批示例
- 选定示例能在真实硬件运行
- 贡献规则清楚到外部作者可以使用

一句话总结: 阶段 1 成功时，即使没有精致 UI，仓库也已经是有用的示例和项目中心。

## 9. 阶段 1 交付边界

阶段 1 工作通过具体仓库资产验收:

- `examples/boards/` 下的开发板示例
- `examples/grove/` 下的 Grove 示例
- `examples/expansion_boards/` 下的扩展板示例
- `projects/` 下的完整项目
- 描述这些资产的 metadata
- 这些资产的验证证据
- 帮助用户构建、烧录、验证或贡献这些资产的文档

未来产品工作在阶段 1 中应体现为数据契约、模板需求、验证记录或贡献规则，并直接服务示例和项目。

一句话总结: 阶段 1 的完成物必须落到具体示例、项目、metadata、验证记录或贡献路径上。
