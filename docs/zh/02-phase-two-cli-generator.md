# 阶段 2: CLI Generator

## 1. 目标

阶段 2 把 Zephyr 基础变成一个确定性的项目生成器。

命令行界面应让用户和工具能够从经过验证的元数据和模板生成完整的 XIAO + Grove Zephyr 项目。

CLI 不是 AI 代码编写器。它是一个基于规则的生成器。

一句话总结: 阶段 2 把基础从“存在的数据”变成“可以生成的项目”。

## 2. 为什么 CLI 先于插件

CLI 是未来界面的最佳共享引擎。

同一个生成器可以被以下内容使用:

- VS Code 插件
- 网页项目构建器
- 文档生成器
- CI 验证
- AI 助手
- 内部工程脚本

如果生成逻辑只写在 VS Code 插件内部，它会更难测试和复用。

一句话总结: CLI 是引擎；图形工具是方向盘。

## 3. 用户体验

示例命令:

```bash
seeed-zephyr generate \
  --board xiao_esp32c6 \
  --expansion xiao_grove_shield \
  --grove grove_sht40 \
  --template sensor_to_serial \
  --toolchain west \
  --output ./xiao-sht40-demo
```

预期输出:

```text
xiao-sht40-demo/
  CMakeLists.txt
  prj.conf
  app.overlay
  README.md
  wiring.svg
  seeed-project.json
  src/
    main.c
```

一句话总结: 用户描述硬件和意图，CLI 写出一个完整项目。

## 4. 确定性生成

生成器应使用:

- 元数据
- 模板
- 兼容性规则
- 验证规则

它不应要求大语言模型发明源代码、drivers、overlays 或引脚分配。

大语言模型之后可以解释错误，或帮助用户选择选项，但生成的项目本身必须来自经过验证的输入。

一句话总结: 正确性应来自经过验证的模板，而不是概率式代码生成。

## 5. 生成流程

生成器应遵循一个简单流程。

### 步骤 1: 验证输入

检查:

- 开发板存在
- Grove 模块存在
- 扩展板存在
- 模板存在
- 请求的选项被允许

一句话总结: 先确认用户的选择是真实存在的。

### 步骤 2: 解析兼容性

检查:

- 开发板暴露所需接口
- 扩展板映射这些接口
- Grove 模块可以连接到其中一个接口
- 模板所需功能受到支持
- 没有引脚或总线冲突

一句话总结: 然后确认所选部件可以一起工作。

### 步骤 3: 组合项目数据

合并:

- 开发板元数据
- Grove 元数据
- 扩展板元数据
- 模板元数据
- 用户设置
- 推荐的 Zephyr 版本

一句话总结: 这会在写入任何文件前创建一个完整项目计划。

### 步骤 4: 渲染文件

渲染:

- 源文件
- Devicetree overlay
- prj.conf
- CMakeLists.txt
- west manifest 或 PlatformIO config
- README
- 接线图
- 项目元数据快照

一句话总结: 文件渲染把项目计划变成真实文件夹。

### 步骤 5: 验证输出

可选验证模式:

```bash
seeed-zephyr verify ./xiao-sht40-demo
seeed-zephyr build ./xiao-sht40-demo
```

验证应检查:

- 所需文件存在
- 元数据快照有效
- 生成的 config 可解析
- 项目可以用所选工具链构建

一句话总结: 生成器应检查自己的工作。

## 6. 核心命令

推荐的首批命令:

```bash
seeed-zephyr list boards
seeed-zephyr list grove
seeed-zephyr list expansions
seeed-zephyr list templates
seeed-zephyr check --board xiao_esp32c6 --grove grove_sht40
seeed-zephyr generate ...
seeed-zephyr build ./project
seeed-zephyr flash ./project
seeed-zephyr monitor ./project
```

一句话总结: CLI 应支持发现、生成和常见开发任务。

## 7. 模板类型

初始模板应专注于有用但简单的场景。

推荐的首批模板:

- `blinky`
- `button_to_serial`
- `sensor_to_serial`
- `relay_control`
- `i2c_scan`

第二批模板:

- `sensor_to_mqtt`
- `ble_sensor`
- `low_power_sensor`
- `home_assistant_mqtt`

一句话总结: 从简单本地流程开始，再添加网络和低功耗场景。

## 8. 工具链输出

### west 输出

west 是 Zephyr 的标准命令行流程。

生成的 west 项目应包含:

- `CMakeLists.txt`
- `prj.conf`
- `app.overlay`
- `src/main.c`
- 关于 `west build`、`west flash` 和 `west debug` 的 README 说明

一句话总结: west 支持应作为参考路径，因为它最接近上游 Zephyr。

### PlatformIO 输出

PlatformIO 支持应在 west 生成稳定之后添加。

生成的 PlatformIO 项目应包含:

- `platformio.ini`
- Zephyr 特定项目结构
- 关于已知 PlatformIO 差异的文档

PlatformIO 对用户友好，但它可能落后于上游 Zephyr，或使用不同的板卡 ID。生成器应清楚暴露这一点。

一句话总结: PlatformIO 有价值，但 west 应保持为主要参考路径。

## 9. 项目元数据快照

每个生成项目都应包含一个快照文件，例如:

```json
{
  "generator": "seeed-zephyr",
  "generator_version": "0.1.0",
  "board": "xiao_esp32c6",
  "expansion": "xiao_grove_shield",
  "grove": ["grove_sht40"],
  "template": "sensor_to_serial",
  "toolchain": "west",
  "zephyr_version": "v4.4.0",
  "generated_at": "2026-06-10T00:00:00Z"
}
```

这有助于支持团队复现用户问题。

一句话总结: 每个生成项目都应携带一张说明它如何创建的收据。

## 10. 错误设计

CLI 错误应具体且可操作。

不好:

```text
Generation failed.
```

好:

```text
Grove SHT40 requires I2C, but the selected expansion board does not expose an I2C Grove port.
Choose XIAO Grove Shield or use custom wiring.
```

一句话总结: 错误消息应告诉用户发生了什么，以及下一步该做什么。

## 11. 阶段 2 成功标准

当满足以下条件时，阶段 2 应视为成功:

- CLI 可以列出受支持的开发板、模块、扩展板和模板
- CLI 可以生成完整的 west 项目
- 生成的项目在 CI 中可构建
- 生成的 README 文件可理解
- 生成的接线图对受支持组合来说是准确的
- 至少若干项目被烧录并在真实硬件上测试
- 生成器可被未来的 VS Code 插件复用

一句话总结: 当生成可重复、可测试，并且在单一界面之外也有用时，阶段 2 就成功了。

## 12. 阶段 2 非目标

阶段 2 不应包括:

- 完整图形界面
- 基于浏览器的 IDE
- 完整 AI 代码生成
- 完整硬件仿真
- 所有 Grove 模块
- 所有高级 Zephyr 场景

一句话总结: 阶段 2 应在添加精致座舱前先打磨好引擎。
