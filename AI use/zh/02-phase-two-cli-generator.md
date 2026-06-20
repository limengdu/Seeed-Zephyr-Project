# 阶段 2: 用于发现、构建、验证和生成的 CLI

## 1. 目标

阶段 2 把示例/项目基础变成实用的命令行工具。

CLI 是共享引擎，帮助用户、CI、维护者、AI 和未来 UI 工具从仓库资产中发现、构建、验证、
复制和生成项目。

一句话总结: 阶段 2 让示例和项目目录可以被一套可重复命令操作。

## 2. 必备能力

CLI 应支持五类工作流。

### 发现内容

```bash
seeed-zephyr list boards
seeed-zephyr list grove
seeed-zephyr list capabilities
seeed-zephyr list examples
seeed-zephyr list projects
```

一句话总结: 用户在生成任何东西之前，应该先能找到内容。

### 查看详情

```bash
seeed-zephyr show board xiao_esp32c6
seeed-zephyr show example boards/xiao_esp32c6/blinky
seeed-zephyr show project xiao_esp32c6_grove_as5600_display
```

一句话总结: CLI 应解释一个资产需要什么、验证状态是什么。

### 构建和烧录仓库资产

```bash
seeed-zephyr build xiao_esp32c6
seeed-zephyr flash xiao_esp32c6
seeed-zephyr flash xiao_esp32c6 --monitor
seeed-zephyr build-project xiao_esp32c6_grove_as5600_display
```

build、flash、monitor 和 debug 的执行应委托给 Zephyr 的 `west` 命令或 Zephyr 模块自带工具。
CLI 应选择仓库资产和已验证 metadata，再交给 Zephyr 工具执行。

一句话总结: 用户应通过 CLI 构建仓库资产，而 CLI 应使用 Zephyr 工具完成执行。

### 验证贡献

```bash
seeed-zephyr validate metadata
seeed-zephyr validate example examples/grove/grove_as5600/basic_read
seeed-zephyr validate project projects/xiao_esp32c6_grove_as5600_display
```

一句话总结: 社区示例和项目需要自动结构检查和构建检查。

### 生成新项目

```bash
seeed-zephyr create \
  --from example/grove/grove_as5600/basic_read \
  --board xiao_esp32c6 \
  --output ./my-as5600-project
```

生成应复制和改造已知可用资产。driver、引脚路由和源代码应来自已验证模板、示例或
Zephyr 原生文件。

一句话总结: 生成基于验证过的示例、模板和证据。

## 3. 确定性生成规则

CLI 必须使用:

- metadata
- 仓库示例
- 仓库项目
- templates
- 验证证据
- 兼容性规则

大语言模型可以帮助解释或选择选项。仓库 metadata、模板、示例和验证证据才是生成源代码、
overlay、引脚和配置的权威。

一句话总结: 正确性来自已检查仓库资产和证据。

## 4. 项目快照

每个生成或复制出的项目都应包含快照，例如:

```json
{
  "generator": "seeed-zephyr",
  "source_asset": "examples/grove/grove_as5600/basic_read",
  "board": "xiao_esp32c6",
  "zephyr_version": "v4.4.0",
  "validation_status": "build-only"
}
```

一句话总结: 生成项目需要收据，方便支持团队和 AI 复现。

## 5. 阶段 2 成功标准

阶段 2 成功条件:

- 用户可以列出并查看示例/项目
- 用户可以从仓库根目录构建首批开发板示例
- 贡献者可以在提交前验证示例结构
- CI 可以调用同一套 CLI 命令
- 生成项目来自已知示例/模板
- 错误消息具体且可操作
- CLI 可被未来 VS Code 插件复用

一句话总结: 阶段 2 成功时，仓库内容变得容易操作和验证。

## 6. 阶段 2 交付边界

阶段 2 工作通过能操作仓库资产的命令行流程验收:

- 发现开发板、模块、示例、项目和状态的命令
- 查看接线、构建目标、预期输出和证据的命令
- 验证 metadata、示例结构和项目结构的命令
- 调用所选 Zephyr workspace 的构建编排命令
- 从已知模板或示例创建项目的命令
- 为生成或验证结果输出机器可读收据
- 供未来编辑器工具使用的稳定输出契约

一句话总结: 阶段 2 完成时，仓库资产可以通过稳定 CLI 命令被发现、检查、构建、生成和记录。
