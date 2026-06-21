# 开发板说明

## English

This directory contains board-specific Zephyr development notes for XIAO boards.

Each board page should record only information that depends on that board:

- pitfalls found during real board development;
- board-specific flashing, reset, bootloader, and serial behavior;
- board-specific pin, peripheral, and subsystem development guides;
- board-specific files or configuration required by examples.

Do not repeat the complete setup flow, all CLI commands, repository roadmap,
or AI work logs here. Put complete process tutorials in `getting-started.md`.

## 中文

这个目录保存 XIAO 开发板的 Zephyr 板级开发说明。

每个开发板页面只记录和这块板子强相关的信息：

- 实际开发中遇到的板级坑点；
- 这块板子特有的烧录、复位、bootloader 和串口行为；
- 这块板子特有的引脚、外设、子功能开发方法；
- 示例需要使用的板级文件或配置。

不要在这里重复完整 setup 流程、所有 CLI 命令、仓库路线图或 AI 工作日志。
完整流程教程放在 `getting-started.md`。

## 文档

- [XIAO SAMD21](xiao-samd21.md)
- [XIAO nRF52840](xiao-nrf52840.md)
- [XIAO MG24](xiao-mg24.md)
- [XIAO RP2040](xiao-rp2040.md)
- [XIAO RP2350](xiao-rp2350.md)
