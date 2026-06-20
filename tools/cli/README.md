# tools/cli

## English

This directory contains the lightweight command-line interface for selecting
and operating repository examples.

The CLI should help users list boards, build examples, flash hardware, start
debug sessions, run the build matrix, and record hardware observations without
memorizing board ids, example paths, or Zephyr target strings.

The CLI is a repository knowledge layer, not a replacement build system. Build,
flash, monitor, and debug execution must delegate to Zephyr `west` commands,
Zephyr module-provided tools, or tools already installed in the Zephyr venv:

- `build` selects a repository example, then calls `west build`.
- `flash` builds with `west build`, then calls `west flash`.
- `monitor` calls the Zephyr Espressif module monitor through
  `west espressif monitor` for Espressif boards. Other boards use pyserial
  miniterm from the Zephyr venv.
- `debug` builds with `west build`, then calls `west debug`.

The user-facing command is installed by `scripts/setup-macos.sh` as
`seeed-zephyr`. The implementation lives here so the command can remain small
and repository-driven.

`seeed-zephyr flash <board_id> --monitor` builds, flashes, and opens the board
monitor after a successful flash.

For Raspberry Pi UF2 boards such as XIAO RP2040 and XIAO RP2350, flash failures
include a BOOTSEL hint when the UF2 mass-storage volume is not visible.

`seeed-zephyr monitor <board_id> --port <device> --baud <rate>` opens a serial
monitor. If `--port` is omitted, the CLI tries to auto-detect one USB serial
device.

`seeed-zephyr debug <board_id>` builds and starts Zephyr's debug flow. It
requires a hardware debugger supported by the board runner.

## 中文

这个目录保存用于选择和操作仓库示例的轻量命令行工具。

CLI 应帮助用户列出开发板、构建示例、烧录硬件、启动调试会话、运行构建矩阵，
并记录硬件观察结果，让用户不用记住开发板 id、示例路径或 Zephyr target 字符串。

CLI 是仓库知识层，不是替代 Zephyr 的构建系统。build、flash、monitor、debug 的执行必须
委托给 Zephyr 的 `west` 命令、Zephyr 模块自带工具，或 Zephyr venv 中已经安装的工具：

- `build` 选择仓库示例，然后调用 `west build`。
- `flash` 先用 `west build` 构建，然后调用 `west flash`。
- `monitor` 在 Espressif 开发板上通过 `west espressif monitor` 调用 Zephyr Espressif
  模块的 monitor。其他开发板使用 Zephyr venv 中的 pyserial miniterm。
- `debug` 先用 `west build` 构建，然后调用 `west debug`。

面向用户的命令由 `scripts/setup-macos.sh` 安装为 `seeed-zephyr`。实现代码放在这里，让命令本身保持轻量，并始终由仓库内容驱动。

`seeed-zephyr flash <board_id> --monitor` 会构建、烧录，并在烧录成功后打开开发板 monitor。

对于 XIAO RP2040 和 XIAO RP2350 这类 Raspberry Pi UF2 开发板，如果看不到 UF2 存储卷，
烧录失败信息会包含 BOOTSEL 提示。

`seeed-zephyr monitor <board_id> --port <device> --baud <rate>` 会打开串口 monitor。
如果省略 `--port`，CLI 会尝试自动检测一个 USB 串口设备。

`seeed-zephyr debug <board_id>` 会构建并启动 Zephyr 的 debug 流程。它需要开发板 runner
支持的硬件调试器。
