# scripts

## English

This directory contains user-facing helper scripts.

Scripts should make repository examples, projects, setup, build, flash, or
validation easier to run. They should point users back to repository examples
and projects, and delegate Zephyr-specific execution to `west` and Zephyr
module tools.

Current scripts:

- `setup-macos.sh`: prepares the macOS Zephyr workspace and prints the next
  repository example command. It also asks whether to install the global
  `seeed-zephyr` command, defaulting to installation.
- `setup-linux.sh`: installs Linux host dependencies and device access, then
  delegates the Zephyr workspace, SDK, blob, CLI, and next-step flow to
  `lib/common.sh`. It is marked not yet verified on real Linux.
- `lib/common.sh`: contains the shared setup flow used by platform setup
  entrypoints. Platform scripts install system dependencies, then reuse this
  file for Zephyr workspace, SDK, Python package, blob, CLI, and next-step
  behavior.
- `seeed-zephyr`: runs the lightweight CLI implementation. It can be symlinked
  into a user PATH directory by `setup-macos.sh`. The CLI selects repository
  metadata and examples, then calls Zephyr tooling for build, flash, and
  monitor operations.
- `build-example.sh`: builds one repository example from the project root by
  calling `west build`.

## 中文

这个目录保存面向用户的辅助脚本。

脚本应让仓库示例、项目、环境搭建、构建、烧录或验证更容易运行。它们应把用户引回本仓库示例和项目，
并把 Zephyr 相关执行委托给 `west` 和 Zephyr 模块工具。

当前脚本:

- `setup-macos.sh`: 准备 macOS Zephyr 工作区，并打印下一条仓库示例命令。它也会询问是否安装全局 `seeed-zephyr` 命令，默认安装。
- `setup-linux.sh`: 安装 Linux 主机依赖和设备访问配置，然后把 Zephyr 工作区、SDK、blob、CLI
  和下一步提示流程交给 `lib/common.sh`。它已标记为尚未在真实 Linux 上验证。
- `lib/common.sh`: 保存平台 setup 入口共用的安装流程。平台脚本先安装系统依赖，然后复用这里的
  Zephyr 工作区、SDK、Python 包、blob、CLI 和下一步提示逻辑。
- `seeed-zephyr`: 运行轻量 CLI 实现。`setup-macos.sh` 可以把它符号链接到用户 PATH 目录。
  CLI 选择仓库 metadata 和示例，然后调用 Zephyr 工具执行构建、烧录和 monitor。
- `build-example.sh`: 从项目根目录调用 `west build` 构建一个仓库示例。
