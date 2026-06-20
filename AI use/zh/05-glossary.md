# 术语表

本术语表用通俗语言解释项目术语。

## Zephyr

Zephyr 是一个用于嵌入式设备的开源实时操作系统。

通俗解释: 它是一个能运行在许多不同微控制器上的共享软件基础。

一句话总结: Zephyr 是本仓库建立在其上的操作层。

## XIAO

XIAO 是 Seeed 的紧凑型开发板系列。

通俗解释: 它是运行用户固件的小型主板。

一句话总结: XIAO 是本仓库的核心开发板。

## Grove

Grove 是 Seeed 的模块化传感器和执行器生态。

通俗解释: Grove 模块用标准线缆连接，而不是手工焊接。

一句话总结: Grove 是本仓库教学和验证的模块系统。

## Example

Example 是本仓库中的小型、聚焦的 Zephyr 应用。

通俗解释: 它用尽量少的额外代码证明一种开发板能力、一个 Grove 模块行为或一个扩展板功能。

一句话总结: 示例是最小的学习和验证单元。

## Project

Project 是组合开发板、Grove 模块、扩展板和真实场景的较完整应用。

通俗解释: 它展示多个示例如何变成有用结果。

一句话总结: 项目是用户可以学习和改造的完整参考。

## Capability

Capability 是开发板或模块能做的事情，例如 I2C、UART、ADC、PWM、BLE、Wi-Fi、display、storage 或 low power。

通俗解释: 能力是用户寻找所需功能的入口。

一句话总结: 能力连接硬件特性和示例。

## Board Target

Board target 是 Zephyr 用来为特定开发板构建固件的名称。

通俗解释: 它告诉 Zephyr 项目要运行在哪块开发板上。

一句话总结: board target 是 Zephyr 的开发板内部名称。

## Devicetree

Devicetree 是 Zephyr 的机器可读硬件地图。

通俗解释: 它告诉软件设备、总线、引脚和模块连接在哪里。

一句话总结: Devicetree 是 Zephyr 读取的接线事实。

## Overlay

Overlay 是额外的 Devicetree 文件，用来添加或修改项目专属硬件信息。

一句话总结: overlay 是项目专属的硬件便签。

## Shield

Shield 是 Zephyr 对附加板的可复用描述。

通俗解释: 在本项目中，扩展板如果拥有引脚路由事实，就应尽量成为 Zephyr shield。

一句话总结: shield 是 Zephyr 原生描述扩展板的方式。

## Metadata

Metadata 是关于开发板、模块、示例、项目和验证状态的结构化产品信息。

通俗解释: 它帮助工具和用户发现有什么，以及什么已知可用。

一句话总结: metadata 让目录可搜索、可测试。

## Validation Evidence

Validation evidence 是状态背后的证据记录。

通俗解释: 它包括构建命令、Zephyr 版本、board target、硬件、结果、日期和观察输出。

一句话总结: 验证证据说明用户为什么能相信支持声明。

## Build-Only

Build-only 表示示例或项目能编译，但还没有在真实硬件上证明。

一句话总结: build-only 有价值，但不等于 hardware-tested。

## Hardware-Tested

Hardware-tested 表示固件已经构建、烧录，并在真实硬件上观察过。

一句话总结: hardware-tested 是普通验证里最强的状态。

## Community Contribution

Community contribution 是核心维护者之外贡献的示例、项目、metadata 改进或验证报告。

通俗解释: 只要结构清晰且可验证，社区贡献就应被欢迎。

一句话总结: 社区贡献让目录增长，同时不能降低信任。

## CLI

CLI 是命令行界面。

通俗解释: 它让用户和工具运行可重复命令。

一句话总结: CLI 操作仓库目录。

## CI

CI 是持续集成。

通俗解释: 它自动检查改动后是否仍能构建和通过验证。

一句话总结: CI 是示例和 metadata 的自动审查者。

## AI Project Charter

AI project charter 是 `AI use/` 下的指导文件。

通俗解释: 它告诉 AI 这个项目是什么、资产如何排序、工作如何记录。

一句话总结: AI 纲领给未来 AI 提供项目说明。

## AI Work Log

AI work log 是 `AI use/WORKLOG.md`。

通俗解释: 它记录重要 AI 工作，但不是私人聊天记录。

一句话总结: 工作日志是未来 AI 的交接轨迹。

## Zephyr-First

Zephyr-first 表示当 Zephyr 适用时，它是默认路径。

通俗解释: 它不表示 Zephyr 是唯一支持路径。

一句话总结: Zephyr-first 是优先 Zephyr，同时保持诚实。
