# scripts

## English

This directory contains user-facing helper scripts.

Scripts should make repository examples, projects, setup, build, flash, or
validation easier to run. They should point users back to repository examples
and projects.

Current scripts:

- `setup-macos.sh`: prepares the macOS Zephyr workspace and prints the next
  repository example command. It also asks whether to install the global
  `seeed-zephyr` command, defaulting to installation.
- `seeed-zephyr`: runs the lightweight CLI implementation. It can be symlinked
  into a user PATH directory by `setup-macos.sh`.
- `build-example.sh`: builds one repository example from the project root.

## 中文

这个目录保存面向用户的辅助脚本。

脚本应让仓库示例、项目、环境搭建、构建、烧录或验证更容易运行。它们应把用户引回本仓库示例和项目。

当前脚本:

- `setup-macos.sh`: 准备 macOS Zephyr 工作区，并打印下一条仓库示例命令。它也会询问是否安装全局 `seeed-zephyr` 命令，默认安装。
- `seeed-zephyr`: 运行轻量 CLI 实现。`setup-macos.sh` 可以把它符号链接到用户 PATH 目录。
- `build-example.sh`: 从项目根目录构建一个仓库示例。
