<div align="center">

<img src="docs/assets/logo.png" alt="Seeed Zephyr Base logo" width="140" />

# Seeed Zephyr Base

**面向 [Zephyr RTOS](https://www.zephyrproject.org/) 的 XIAO + Grove 示例库、能力目录与命令行工作流。**

一眼看清 Seeed Studio XIAO 开发板在 Zephyr 上能做什么、哪些示例已通过验证，并用一条命令从全新检出走到烧录固件。

[![Metadata Validation](https://github.com/limengdu/Seeed-Zephyr-Project/actions/workflows/metadata.yml/badge.svg)](https://github.com/limengdu/Seeed-Zephyr-Project/actions/workflows/metadata.yml)
[![Zephyr](https://img.shields.io/badge/Zephyr-v4.4.0-7929d3)](https://docs.zephyrproject.org/4.4.0/)
[![Boards](https://img.shields.io/badge/XIAO%20boards-11%20tracked-00979d)](#支持的开发板)
[![Platform](https://img.shields.io/badge/host-macOS%20%7C%20Linux%20%7C%20Windows-blue)](#快速开始)

[快速开始](#快速开始) · [支持的开发板](#支持的开发板) · [命令行](#命令行工作流) · [文档](#文档) · [路线图](#路线图)

[English](README.md) · **简体中文**

</div>

---

## 项目简介

XIAO 是一个多芯片生态。不同的 XIAO 开发板使用不同的芯片厂商、无线协议栈、SDK、烧录工具和开发流程。Zephyr 正在成为贯穿这些开发板的统一技术底座——而本仓库则在它之上补齐 XIAO + Grove 的产品体验。

上游 Zephyr 回答的是一个问题：*「这块板子能跑 Zephyr 吗？」*

**Seeed Zephyr Base 回答的是接下来的几个：**

> XIAO + Grove 用户在 Zephyr 上究竟能做出什么？哪些示例在真实硬件上验证过？我能不能在不先啃完 Devicetree、Kconfig 和 `west` 的情况下，就把一个示例构建并烧录进去？

你将获得：每块支持的开发板对应的最小可构建示例、XIAO 与 Grove 的能力元数据、一份证明「什么能编译通过」的构建矩阵，以及一个轻量的 `seeed-zephyr` 命令行工具——它替你选好正确的板级目标和示例，再把真正的工作交给标准的 Zephyr 工具链。

## 核心亮点

- **🧩 每块板一个示例** —— 为每块在册的 XIAO 板提供最小、可构建的示例，开箱即可烧录。
- **⚡ 单命令工作流** —— 安装后 `seeed-zephyr build | flash | monitor | debug <板子>` 在任意目录都能用。
- **🔌 板级细节自动处理** —— UF2 模式进入、DFU、PyOCD、1200 波特率 bootloader 请求等都按板子自动完成，你无需记住每家厂商的烧录步骤。
- **📇 能力目录** —— 为 XIAO 开发板、Grove 模块和扩展板提供结构化元数据。
- **✅ 诚实的验证** —— 每块板都带有构建矩阵结果，真机验证过的板子会明确标注。
- **🌍 中英双语文档** —— 入门指南与板级说明均提供英文与中文。
- **🤖 刻意保持轻量** —— 命令行只是「仓库知识层」，固件的构建、烧录、监视、调试始终交给 Zephyr `west` 与厂商工具执行。

## 支持的开发板

下表状态取自[构建矩阵](tools/build_matrix/results.md)，基线为 Zephyr **v4.4.0**。

| 开发板 | 厂商 | Zephyr 目标 | 示例 | 状态 |
| --- | --- | --- | --- | --- |
| XIAO SAMD21 | Microchip | `seeeduino_xiao` | `blinky` | 🔵 真机验证 |
| XIAO nRF52840 | Nordic | `xiao_ble` | `blinky` | 🔵 真机验证 |
| XIAO nRF54L15 | Nordic | `xiao_nrf54l15/nrf54l15/cpuapp` | `blinky` | 🔵 真机验证 |
| XIAO MG24 | Silabs | `xiao_mg24` | `blinky` | 🔵 真机验证 |
| XIAO RP2040 | Raspberry Pi | `xiao_rp2040` | `blinky` | 🔵 真机验证 |
| XIAO RP2350 | Raspberry Pi | `xiao_rp2350/rp2350a/m33` | `blinky` | 🔵 真机验证 |
| XIAO ESP32-C6 | Espressif | `xiao_esp32c6/esp32c6/hpcore` | `blinky` | 🔵 真机验证 |
| XIAO ESP32-S3 | Espressif | `xiao_esp32s3/esp32s3/procpu` | `blinky` | 🔵 真机验证 |
| XIAO ESP32-C3 | Espressif | `xiao_esp32c3` | `hello_world` | 🔵 真机验证 · 板载无 LED |
| XIAO RA4M1 | Renesas | `xiao_ra4m1` | `blinky` | 🔵 真机验证 · USB DFU |
| XIAO ESP32-C5 | Espressif | `xiao_esp32c5` | `hello_world` | ⛔ v4.4.0 暂无目标 |

**图例** —— 🔵 真实硬件验证通过 · 🟢 CI 中可干净构建 · ⛔ 已在册，但所选 Zephyr 基线尚未提供该板级目标。

各开发板特有的烧录、复位、bootloader 行为，详见[板级说明](docs/zh/boards/README.md)。

## 快速开始

无需克隆本仓库即可使用这些工具——新用户直接从已发布的渠道安装即可。

> **目录分工：** `seeed-zephyr` 命令行会安装到你的 `PATH` 上；Zephyr 源码树、SDK 和 `west` 工作区则位于 `~/zephyrproject`。安装脚本会替你准备好这两部分。

### 1. 安装命令行与 Zephyr 环境

一行安装脚本会同时装好 `seeed-zephyr` 命令行**和**完整的 Zephyr 工具链（SDK、`west` 工作区、各板烧录工具）。支持 macOS 与 Linux（Windows 请在 WSL2 内运行）：

```sh
curl -fsSL https://raw.githubusercontent.com/limengdu/Seeed-Zephyr-Project/main/install.sh | bash
```

只想安装单块板子的依赖时，把 `--board` 通过管道传进去：

```sh
curl -fsSL https://raw.githubusercontent.com/limengdu/Seeed-Zephyr-Project/main/install.sh | bash -s -- --board xiao_esp32c6
```

只想单独装命令行？用 PyPI、[pipx](https://pipx.pypa.io/) 或 [Homebrew](https://brew.sh/) 安装,再照[入门指南](docs/zh/getting-started.md)准备 Zephyr 工具链：

```sh
pip install seeed-zephyr                        # 全平台
pipx install seeed-zephyr
brew install limengdu/seeed/seeed-zephyr        # macOS / Linux
```

Windows 未使用 WSL2 时，请按[入门指南](docs/zh/getting-started.md)里的 PowerShell 步骤配置。

### 2. 安装编辑器插件

**Seeed XIAO Zephyr Assistant** 插件可浏览带验证徽章的开发板与示例,并在编辑器内直接构建 / 烧录 / 监视。在 Cursor、Windsurf、VSCodium、Gitpod 或 Eclipse Theia 的扩展面板搜索 **Seeed XIAO Zephyr** 即可安装,也可从 [Open VSX 页面](https://open-vsx.org/extension/seeed-studio/seeed-xiao-zephyr-assistant)安装。

### 3. 构建你的第一个示例

在任意目录运行命令行：

```sh
seeed-zephyr build xiao_esp32c6
```

命令行读取板级元数据，找到匹配的示例，再用验证过的目标调用 Zephyr 的 `west build`。

### 卸载

删除 `seeed-zephyr` 命令，并按你的选择删除 Zephyr 工作区和 SDK:

```sh
bash uninstall.sh
```

它会先删除 `seeed-zephyr` CLI 符号链接，再询问是否删除 Zephyr 工作区(`~/zephyrproject`)和 SDK。通过 Homebrew 或 Linux 包管理器安装的共享构建工具，只会列出清单和删除命令，不会替你自动删除。加 `--yes` 可跳过询问直接删除工作区和 SDK，加 `--dry-run` 可预览。

## 命令行工作流

`seeed-zephyr` 负责选定开发板、示例和验证过的元数据，再把真正的设备操作交给 Zephyr 工具链。

### 构建、烧录、监视、调试

```sh
seeed-zephyr build   xiao_esp32c6
seeed-zephyr flash   xiao_esp32c6
seeed-zephyr monitor xiao_esp32c6
seeed-zephyr debug   xiao_esp32c6
```

烧录完成后直接进入串口监视：

```sh
seeed-zephyr flash xiao_esp32c6 --monitor
```

### 选择示例

当一块板有多个示例时，命令行会列出来让你挑选。直接写出示例名即可跳过选择：

```sh
seeed-zephyr build xiao_esp32c6 blinky
```

### 构建外部应用

把命令行指向任意一个 Zephyr 应用目录（含 `CMakeLists.txt` 和 `prj.conf` 的目录）：

```sh
seeed-zephyr flash xiao_esp32c6 --app ~/my-zephyr-app --monitor
```

### 查看有哪些可用资源

```sh
seeed-zephyr list boards
seeed-zephyr list examples
```

### 无需指定板子的串口监视

交互式选择端口和波特率：

```sh
seeed-zephyr monitor
```

### 维护者命令

```sh
seeed-zephyr matrix                        # 重新生成完整的板级构建矩阵
seeed-zephyr verify-hardware xiao_esp32c6  # 记录一次硬件观测结果
```

完整流程演练见[入门指南](docs/zh/getting-started.md)。

## Grove 与扩展板支持

能力目录同样收录了与 XIAO 搭配的 Grove 模块和扩展板，包含它们的接口、默认地址、供电轨，以及所需的 Zephyr 驱动和 Kconfig 选项。

**Grove 模块：** AS5600 磁旋转编码器 · GPS（Air530） · GSR 传感器 · 超声波测距

**扩展板：** Grove Shield for XIAO · XIAO 扩展板 · XIAO 圆形显示屏

完整的机器可读目录见 [`metadata/`](metadata/)。

## 从源码构建

想改示例、元数据或命令行本身？克隆仓库并直接运行 setup 脚本。这条路还能解锁维护者命令（`matrix`、`verify-hardware`）以及仓库内的 `scripts/seeed-zephyr` 启动器。

```sh
git clone https://github.com/limengdu/Seeed-Zephyr-Project.git
cd Seeed-Zephyr-Project
bash scripts/setup-macos.sh        # 或 scripts/setup-linux.sh
```

Windows（WSL2）：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup-windows.ps1
```

setup 会准备 Zephyr 工作区、安装 Python 虚拟环境与 `west`、下载 Zephyr v4.4.0 和 SDK、获取各板所需的烧录工具，并询问你是否安装 `seeed-zephyr` 命令行。加 `--board <目标>` 可只下载单块板子的依赖。

## 仓库结构

```text
Seeed-Zephyr-Project/
├── examples/boards/      # 每块 XIAO 板的最小可构建示例
├── metadata/             # 开发板、Grove 模块、扩展板目录
│   ├── boards/
│   ├── grove_modules/
│   └── expansion_boards/
├── scripts/              # 跨平台 setup + seeed-zephyr 启动器
├── tools/
│   ├── cli/              # seeed-zephyr 命令行实现
│   ├── build_matrix/     # 完整的板级示例构建验证
│   └── validate_metadata/# 元数据 schema 校验（CI 中运行）
├── docs/                 # 面向用户的指南与板级说明（英文 + 中文）
└── .github/workflows/    # CI：元数据校验
```

## 路线图

项目按三个层次推进，每一层为下一层铺路。

1. **示例、元数据与验证基础**（进行中）—— 最小板级示例、可复用的 XIAO + Grove 项目示例、能力目录、构建矩阵、CI 验证，以及选定的硬件在环测试。
2. **发现与生成命令行** —— 扩展 `seeed-zephyr`，从仓库模板脚手架出新的示例与项目，组合「板子 + Grove + 场景」模板，并生成带 README、overlay 和源码的 west / PlatformIO 项目。
3. **VS Code 产品体验** —— 可视化选择开发板、Grove 模块与扩展板；浏览示例；查看兼容性与验证状态；渲染接线图；生成项目；再把构建/烧录/监视/调试交给官方 Zephyr VS Code 扩展。

指导原则：示例和项目是产品核心；元数据、命令行、生成器与编辑器工具的存在，都是为了让这些示例更易于发现、构建、验证和扩展。

## 文档

| English | 中文 |
| --- | --- |
| [Getting Started](docs/en/getting-started.md) | [入门指南](docs/zh/getting-started.md) |
| [Board Notes](docs/en/boards/README.md) | [开发板说明](docs/zh/boards/README.md) |

各板级说明覆盖 SAMD21、nRF52840、MG24、RA4M1、RP2040、RP2350 的烧录、复位、bootloader 与串口细节。

## 参与贡献

欢迎贡献新的板级示例、Grove 模块、项目示例和验证证据。每次 push 和 pull request 都会通过 [Metadata Validation 工作流](.github/workflows/metadata.yml)自动校验元数据，因此请保证新的目录条目符合 schema，并用证据而非假设来支撑构建/硬件状态。

## 致谢

构建于 [Zephyr Project](https://www.zephyrproject.org/) 以及 [Seeed Studio XIAO](https://www.seeedstudio.com/xiao-series-page) 和 [Grove](https://wiki.seeedstudio.com/Grove_System/) 生态之上。
