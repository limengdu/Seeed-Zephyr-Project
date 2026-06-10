# 阶段 3: VS Code Plugin

## 1. 目标

阶段 3 把 CLI 和元数据基础变成 VS Code 内面向开发者的产品。

该插件应专注于 Seeed 独有的部分: 选择 XIAO 开发板、扩展板和 Grove 模块，检查兼容性，预览接线，配置选项，并生成正确项目。这里有意不重新实现构建、烧录、监视和调试步骤。

官方 Zephyr VS Code 扩展，以及 nRF Connect for VS Code 等供应商扩展，已经为 Zephyr 项目提供环境设置、构建、烧录、监视和调试，并且做得很好。重建这一层会重复成熟工具，并增加维护量，却没有独特价值。这个插件改为生成一个标准 Zephyr 项目，然后把工具链步骤交给这些扩展。

理想体验结合了三个已验证的思路，而且都位于构建前这一独特价值所在的位置:

- CubeMX 风格硬件配置
- ESPHome 风格组件选择和低摩擦设置
- Wokwi 风格接线预览和项目可视化

插件第一版不应试图成为完整电子设计工具、完整硬件模拟器，或官方 Zephyr 工具链扩展的替代品。

一句话总结: 阶段 3 负责硬件选择、兼容性、接线和生成，并把构建与烧录工具链交给官方 Zephyr 扩展。

## 2. 产品定位

推荐产品名称:

```text
Seeed XIAO Project Assistant
```

插件应定位为:

```text
A VS Code assistant for choosing, configuring, and generating XIAO + Grove Zephyr projects, ready to build with the official Zephyr extension.
```

不应定位为:

```text
A replacement for Zephyr
A replacement for VS Code
A replacement for the official Zephyr or vendor toolchain extensions
A complete simulator
A universal embedded IDE
```

一句话总结: 这个插件是一个聚焦的项目创建助手，停在官方构建工具链的门口。

## 3. 用户旅程

### 步骤 1: 打开插件

用户在 VS Code 中打开 XIAO Project Assistant 面板。

插件显示:

- 创建新项目
- 打开已有生成项目
- 检查本地环境
- 查看受支持的开发板和模块

一句话总结: 第一个界面应帮助用户选择一个明确的开始路径。

### 步骤 2: 选择 XIAO 开发板

用户选择一块开发板，例如:

- XIAO ESP32C6
- XIAO ESP32S3
- XIAO nRF54L15
- XIAO MG24
- XIAO RP2350

插件显示:

- Zephyr board target
- 受支持接口
- 无线支持状态
- 验证状态
- 已知问题
- 推荐工具链

一句话总结: 开发板选择决定项目其余部分可以支持什么。

### 步骤 3: 选择扩展板

用户选择:

- XIAO Grove Shield
- XIAO Expansion Board
- XIAO Round Display
- XIAO ePaper Driver Board
- custom wiring

扩展板会把物理端口映射到 XIAO 接口。

一句话总结: 扩展板选择告诉插件模块可以连接到哪里。

### 步骤 4: 选择 Grove 模块

用户选择模块，例如:

- Grove SHT40
- Grove Button
- Grove Relay
- Grove Light Sensor
- Grove OLED
- Grove IMU

插件检查:

- 所需接口
- 默认地址
- driver 可用性
- 电源要求
- 端口可用性
- 兼容性状态

一句话总结: 用户选择产品名称，而插件处理技术约束。

### 步骤 5: 配置设置

插件显示一个类似轻量级 CubeMX 体验的设置面板。

可能的设置:

- GPIO pin
- I2C bus
- I2C address
- SPI bus
- SPI frequency
- UART baud rate
- ADC channel
- sampling interval
- logging level
- BLE device name
- MQTT host and topic
- low-power wake interval
- west or PlatformIO output

默认值必须在无需手动更改的情况下工作。

一句话总结: 高级用户可以调整设置，但入门用户应能够直接使用默认值。

### 步骤 6: 查看接线预览

插件渲染接线图。

第一版应使用 SVG 或 Webview 渲染的图表。

图表应显示:

- 所选 XIAO 开发板
- 所选扩展板
- 所选 Grove 模块
- 端口名称
- 信号映射
- 电压要求
- 警告

示例映射:

```text
Grove SHT40
VCC -> 3V3
GND -> GND
SDA -> xiao_i2c.sda
SCL -> xiao_i2c.scl
```

一句话总结: 接线预览应降低用户对硬件接错的担心。

### 步骤 7: 生成项目

用户点击 Generate。

插件调用 CLI:

```bash
seeed-zephyr generate ...
```

生成的项目包含:

- 源代码
- Zephyr 配置
- Devicetree overlay
- 构建文件
- README
- 接线图
- 元数据快照

一句话总结: 项目生成应保持确定性，并由 CLI 驱动。

### 步骤 8: 交接给官方工具链

生成后，插件不自己运行构建。它以官方 Zephyr VS Code 扩展可识别的方式打开生成项目，并引导用户使用该扩展已有的 Build、Flash、Monitor 和 Debug 操作。

插件只提供属于自身范围的操作:

- 打开生成项目
- 打开 README
- 打开接线图
- 检测官方 Zephyr 扩展是否已安装，并在缺失时提示安装
- 通过单击触发官方扩展的构建操作，从而启动推荐构建

这保持了清晰边界: 插件负责选择、兼容性、接线和生成；官方扩展负责构建、烧录、监视和调试。

一句话总结: 生成正确项目后，插件会把用户交给官方 Zephyr 扩展进行构建和烧录，而不是重复实现它。

## 4. 插件架构

推荐模块:

```text
Hardware Catalog
Compatibility Engine
Wiring Renderer
Config Panel
Project Generator Adapter
Toolchain Handoff
Grove Error Hints
```

上面的模块是插件自己的范围。构建、烧录、监视、调试和完整环境设置有意不作为这里的模块；它们通过 Toolchain Handoff 委托给官方 Zephyr 扩展。

### Hardware Catalog

加载开发板、Grove、扩展板、模板和兼容性元数据。

一句话总结: catalog 是插件的产品数据库。

### Compatibility Engine

检查所选硬件和模板能否一起工作。

它应检测:

- 缺失接口
- 引脚冲突
- 重复 I2C 地址
- 不受支持的开发板功能
- build-only 或 experimental 状态

一句话总结: compatibility engine 防止用户生成已知有问题的项目。

### Wiring Renderer

根据元数据创建可视化接线图。

第一版应优先保证正确性，而不是视觉复杂度。

一句话总结: wiring renderer 把元数据变成用户可以照着连接的东西。

### Config Panel

显示可编辑选项并验证它们。

一句话总结: config panel 是用户无需手动编辑 Zephyr 文件即可自定义项目的地方。

### Project Generator Adapter

调用 CLI 并报告进度。

一句话总结: adapter 把图形插件连接到确定性生成器。

### Toolchain Handoff

把生成的项目连接到官方 Zephyr VS Code 扩展。它检测该扩展是否已安装，在缺失时提示安装，打开项目以便该扩展接管，并触发该扩展自己的构建操作。

它不直接运行 west、flash、monitor 或 debug，也不重新检查工具链环境；官方扩展已经负责环境设置和这些命令。

一句话总结: handoff 模块是通往官方扩展的薄桥，而不是第二套工具链。

### Grove Error Hints

把少量 Seeed 特定失败模式映射为人可读的建议: 某个已知 Grove 模块的 I2C 地址错误、所选 driver 缺少 Kconfig、模块插入了 shield 不暴露的端口。

通用 Zephyr、west、CMake 和 Devicetree 错误交给官方扩展和更广泛的 Zephyr 社区处理，它们已经对此有文档。这个模块保持窄范围，只覆盖 XIAO 和 Grove 独有的问题。它一开始是基于规则的查询；之后可以加入 AI，但不是必需。

一句话总结: 错误提示专注于 XIAO 和 Grove 错误，而不是通用 Zephyr 工具链错误。

## 5. 技术选择

推荐实现:

- 使用 TypeScript 编写 VS Code extension
- 使用 Webview UI 构建项目配置器
- 使用 SVG 绘制接线图
- 集成 CLI 进行生成
- 将官方 Zephyr VS Code 扩展作为构建、烧录、监视和调试的依赖
- 使用 VS Code extension API 检测、安装并触发该扩展

一句话总结: 使用常规 VS Code 扩展技术，依靠官方 Zephyr 扩展处理工具链，并避免不必要的自定义基础设施。

## 6. MVP 范围

推荐的首个插件版本:

### 开发板

- XIAO ESP32C6
- XIAO nRF54L15
- XIAO MG24

### 扩展板

- XIAO Grove Shield
- XIAO Expansion Board

### Grove 模块

- Grove SHT40
- Grove Button
- Grove Relay
- Grove Light Sensor
- Grove OLED

### 模板

- Sensor to Serial
- Button to Serial
- Relay Control
- I2C Scan

### 工具链

- 生成标准 west 项目
- 将构建、烧录、监视和调试委托给官方 Zephyr 扩展
- PlatformIO 输出只在后续版本中考虑，前提是存在真实需求

### 核心功能(插件自身范围)

- 硬件选择
- 兼容性显示
- 参数面板
- 接线图
- 项目生成
- 一键交接到官方 Zephyr 扩展的构建操作
- XIAO 和 Grove 特定错误提示

### 委托给官方 Zephyr 扩展

- build
- flash
- monitor
- debug
- toolchain environment setup and checks

一句话总结: MVP 负责从选择到生成，交接工具链，并保持小到足以完成，同时证明独特流程。

## 7. 第一版应避免的功能

不要从以下内容开始:

- 重新实现官方 Zephyr 扩展已经提供的构建、烧录、监视或调试
- 复制官方扩展的自定义工具链环境 doctor
- 完整 Wokwi 风格模拟
- 任意拖拽式电路编辑
- 所有 XIAO 开发板
- 所有 Grove 模块
- 云账号
- 在线构建服务
- AI 生成 drivers
- 完整包管理器

一句话总结: 不要重建官方工具链；先证明独特的选择到生成流程，再增加智能和规模。

## 8. 成功标准

当满足以下条件时，阶段 3 应视为成功:

- 用户可以创建项目，而无需手动编写 Zephyr boilerplate
- 所选组合显示清晰的兼容性状态
- 接线图与真实硬件一致
- 生成的项目可以通过官方 Zephyr 扩展构建，无需手动修补
- 与该扩展的交接一键完成，并且可在干净环境中工作
- 至少若干组合通过官方工具链烧录并在真实开发板上运行
- XIAO 和 Grove 特定错误能产生清晰提示
- 早期用户比手动设置 Zephyr 更快完成第一个项目

一句话总结: 当用户能从硬件选择走到一个可在官方扩展中干净构建的生成项目，而不必先学习每个 Zephyr 细节时，插件就成功了。

## 9. 未来扩展

MVP 之后，可能的扩展包括:

- PlatformIO 支持
- 更多 XIAO 开发板
- 更多 Grove 模块
- Home Assistant 模板
- MQTT 模板
- BLE 模板
- 低功耗模板
- AI 辅助错误解释
- AI 辅助项目选择
- 由同一套元数据生成的网页兼容性矩阵
- 在线项目预览

一句话总结: 插件可以从生成器成长为主要 XIAO 开发者体验。
