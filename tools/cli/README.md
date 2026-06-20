# tools/cli

## English

This directory contains the lightweight command-line interface for operating
repository examples.

The CLI should help users list boards, build examples, flash hardware, run the
build matrix, and record hardware observations without remembering the lower
level Zephyr commands.

The user-facing command is installed by `scripts/setup-macos.sh` as
`seeed-zephyr`. The implementation lives here so the command can remain small
and repository-driven.

## 中文

这个目录保存用于操作仓库示例的轻量命令行工具。

CLI 应帮助用户列出开发板、构建示例、烧录硬件、运行构建矩阵，并记录硬件观察结果，让用户不用记住底层 Zephyr 命令。

面向用户的命令由 `scripts/setup-macos.sh` 安装为 `seeed-zephyr`。实现代码放在这里，让命令本身保持轻量，并始终由仓库内容驱动。
