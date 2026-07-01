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
- `setup-windows.ps1`: prepares Windows for the WSL2 strategy by checking or
  installing WSL2 and usbipd-win, then directs users to run
  `scripts/setup-linux.sh` inside WSL2. It is marked not yet verified on real
  Windows.
- `lib/common.sh`: contains the shared setup flow used by platform setup
  entrypoints. Platform scripts install system dependencies, then reuse this
  file for Zephyr workspace, SDK, Python package, blob, CLI, and next-step
  behavior.
- `seeed-zephyr`: runs the lightweight CLI implementation. It can be symlinked
  into a user PATH directory by `setup-macos.sh`. The CLI is also available as
  a standalone package via `pip install seeed-zephyr`. The CLI selects
  repository metadata and examples, then calls Zephyr tooling for build, flash,
  and monitor operations.
- `build-example.sh`: builds one repository example from the project root by
  calling `west build`.
- `uninstall-macos.sh` / `uninstall-linux.sh`: remove the `seeed-zephyr` CLI
  symlink and, after asking, the Zephyr workspace and SDK. Shared system build
  tools are listed with removal commands rather than removed automatically.
  Accept `--yes` to remove the workspace and SDK without prompting and
  `--dry-run` to preview.
- `uninstall-windows.ps1`: prints how to run the WSL2 uninstall and how to
  remove WSL2 and usbipd-win by hand.
- `lib/uninstall-common.sh`: contains the shared uninstall flow used by the
  platform uninstall entrypoints.

## 中文

这个目录保存面向用户的辅助脚本。

脚本应让仓库示例、项目、环境搭建、构建、烧录或验证更容易运行。它们应把用户引回本仓库示例和项目，
并把 Zephyr 相关执行委托给 `west` 和 Zephyr 模块工具。

当前脚本:

- `setup-macos.sh`: 准备 macOS Zephyr 工作区，并打印下一条仓库示例命令。它也会询问是否安装全局 `seeed-zephyr` 命令，默认安装。
- `setup-linux.sh`: 安装 Linux 主机依赖和设备访问配置，然后把 Zephyr 工作区、SDK、blob、CLI
  和下一步提示流程交给 `lib/common.sh`。它已标记为尚未在真实 Linux 上验证。
- `setup-windows.ps1`: 按 WSL2 策略准备 Windows，检查或安装 WSL2 与
  usbipd-win，然后引导用户在 WSL2 内运行 `scripts/setup-linux.sh`。它已标记为尚未在真实 Windows 上验证。
- `lib/common.sh`: 保存平台 setup 入口共用的安装流程。平台脚本先安装系统依赖，然后复用这里的
  Zephyr 工作区、SDK、Python 包、blob、CLI 和下一步提示逻辑。
- `seeed-zephyr`: 运行轻量 CLI 实现。`setup-macos.sh` 可以把它符号链接到用户 PATH 目录。
  也可以通过 `pip install seeed-zephyr` 作为独立包安装。CLI 选择仓库 metadata 和示例，
  然后调用 Zephyr 工具执行构建、烧录和 monitor。
- `build-example.sh`: 从项目根目录调用 `west build` 构建一个仓库示例。
- `uninstall-macos.sh` / `uninstall-linux.sh`: 删除 `seeed-zephyr` CLI 符号链接，
  并在询问后删除 Zephyr 工作区和 SDK。共享的系统构建工具只列出清单和删除命令，
  不自动删除。可加 `--yes` 跳过询问直接删除工作区和 SDK，加 `--dry-run` 预览。
- `uninstall-windows.ps1`: 打印如何在 WSL2 内执行卸载，以及如何手动删除 WSL2 与
  usbipd-win。
- `lib/uninstall-common.sh`: 保存平台卸载入口共用的卸载流程。
