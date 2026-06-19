# 术语表

本术语表用通俗语言解释重要术语。

## Zephyr

Zephyr 是一个用于嵌入式设备的开源实时操作系统。

通俗解释: 它是一个共享软件基础，可以运行在许多不同的微控制器上。

一句话总结: Zephyr 是许多小芯片的通用操作层。

## RTOS

RTOS 的意思是实时操作系统。

通俗解释: 它是一个小型操作系统，专为需要可预测时序的设备设计，例如传感器、无线设备和工业控制器。

一句话总结: RTOS 帮助小设备在正确时间运行任务。

## XIAO

XIAO 是 Seeed 的紧凑型开发板系列。

通俗解释: 它是一块小板，带有微控制器，并引出用于传感器、通信和扩展的引脚。

一句话总结: XIAO 是运行用户固件的小型主板。

## Grove

Grove 是 Seeed 的模块化传感器和执行器生态系统。

通俗解释: Grove 让用户可以用标准化线缆连接传感器和模块，而不是手工焊接。

一句话总结: Grove 把硬件模块变成即插即用的积木。

## Expansion Board

扩展板是一块附加板，可以为 XIAO 提供更方便的端口或功能。

通俗解释: 它就像 XIAO 的插线板，让连接 Grove 模块、显示屏、按钮或电池更容易。

一句话总结: 扩展板让 XIAO 更容易连接其他硬件。

## Board Target

Board target 是 Zephyr 用来为特定开发板构建固件的名称。

通俗解释: 它告诉 Zephyr 这个项目打算在哪块开发板上运行。

一句话总结: board target 是 Zephyr 对所选开发板的内部名称。

## Devicetree

Devicetree 是 Zephyr 使用的硬件描述系统。

通俗解释: 它是一张机器可读的硬件地图，告诉软件 LED、按钮、总线和传感器连接在哪里。

一句话总结: Devicetree 是 Zephyr 可以读取的接线地图。

## Overlay

Overlay 是一个额外的 Devicetree 文件，用来添加或更改硬件信息。

通俗解释: 如果用户把 Grove 传感器插到开发板上，overlay 会告诉 Zephyr 关于这个新增传感器的信息。

一句话总结: overlay 是针对特定项目的一小张额外接线便签。

## Shield

Shield 是 Zephyr 内置的附加板描述方式，例如插到主板上的扩展板。

通俗解释: shield 是一个可复用文件夹，携带 overlay 文件和默认设置，所以 Zephyr 知道附加板如何把引脚路由到主板。在本项目中，每块 Seeed 扩展板都实现为一个 shield，引脚路由保存在那里，而不是复制到元数据中。

一句话总结: shield 是 Zephyr 对扩展板的可复用描述，并拥有引脚路由。

## LTS

LTS 的意思是长期支持版本。

通俗解释: 它是项目会用稳定性和安全修复维护多年的 Zephyr 版本，并推荐给构建真实产品的人。当前 LTS 是 Zephyr 3.7，下一个计划为 Zephyr 4.6。本项目跟踪最新稳定版本，而不是 LTS。

一句话总结: LTS 是面向产品的长期维护 Zephyr 版本。

## Kconfig

Kconfig 是 Zephyr 的配置系统。

通俗解释: 它控制哪些功能打开或关闭，例如传感器、日志、Bluetooth、Wi-Fi 或 drivers。

一句话总结: Kconfig 是 Zephyr 项目的功能开关板。

## prj.conf

`prj.conf` 是 Zephyr 使用的项目配置文件。

通俗解释: 它保存一个项目的功能开关。

一句话总结: `prj.conf` 说明这个项目需要哪些 Zephyr 功能。

## west

west 是 Zephyr 的命令行工具。

通俗解释: 它帮助下载 Zephyr 模块、构建项目、烧录固件和运行调试命令。

一句话总结: west 是 Zephyr 项目的标准命令工具。

## CMake

CMake 是一个构建配置工具。

通俗解释: 它告诉电脑如何把源代码变成固件。

一句话总结: CMake 准备构建说明。

## Ninja

Ninja 是一个构建执行工具。

通俗解释: CMake 准备好构建说明后，Ninja 会快速执行它们。

一句话总结: Ninja 在 CMake 准备好之后执行实际构建工作。

## PlatformIO

PlatformIO 是一个嵌入式开发平台，可在 VS Code 等编辑器中工作。

通俗解释: 它用用户友好的方式组织项目、依赖、构建命令、上传命令和串口监视。

一句话总结: PlatformIO 是一个对嵌入式开发友好的项目系统。

## Metadata

Metadata 是关于某个事物的结构化信息。

通俗解释: 开发板 metadata 描述一块开发板；Grove metadata 描述一个模块；模板 metadata 描述一个项目需要什么。

一句话总结: metadata 是用软件能理解的方式写下的产品信息。

## CLI

CLI 的意思是命令行界面。

通俗解释: 它是用户通过在终端输入命令来运行的工具。

一句话总结: CLI 让用户和其他工具可以运行可重复的命令。

## CI

CI 的意思是持续集成。

通俗解释: 它是一套自动检查系统，会在发生变更时构建或测试代码。

一句话总结: CI 是检查变更是否破坏了东西的机器人。

## Hardware-in-loop

Hardware-in-loop 的意思是在真实硬件上自动测试软件。

通俗解释: 测试系统不是只编译固件，而是把它烧录到真实开发板上并检查结果。

一句话总结: hardware-in-loop 证明代码能在真实设备上运行。

## VS Code Webview

VS Code Webview 是 VS Code 扩展内部的一个小型网页面板。

通俗解释: 它让插件可以显示自定义界面、表单、图表和控件。

一句话总结: Webview 让 VS Code 插件拥有自己的可视化界面。

## Wiring Diagram

接线图展示硬件部件如何连接。

通俗解释: 它告诉用户哪个 Grove 端口、引脚、电源线和信号线应连接到哪个模块。

一句话总结: 接线图是用户的可视化连接指南。

## Compatibility Matrix

兼容性矩阵展示哪些组合可以工作。

通俗解释: 它可能显示某块 XIAO 开发板在 Zephyr 下是否支持某个 Grove 模块，以及该支持是已测试还是实验性的。

一句话总结: 兼容性矩阵是一张说明什么可用、什么不可用的地图。

## Template

模板是预先准备好的项目模式。

通俗解释: 生成器不需要从零写每个文件，而是填充一个已知可用的项目结构。

一句话总结: 模板是可复用的入门项目。

## Vendor SDK

Vendor SDK 是芯片制造商提供的官方软件开发工具包。

通俗解释: Espressif、Nordic、Silicon Labs、Renesas 和其他芯片供应商会为自己的芯片提供软件包。

一句话总结: vendor SDK 是芯片制造商自己的开发工具包。

## Zephyr-first

Zephyr-first 意味着当 Zephyr 适用时，它是默认推荐路径。

通俗解释: 它不意味着 Zephyr 是唯一支持的路径。

一句话总结: Zephyr-first 意味着优先选择 Zephyr，但在其他路径更好时保留它们。
