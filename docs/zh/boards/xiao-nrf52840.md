# XIAO nRF52840 Zephyr 开发指南

本页只记录 Seeed Studio XIAO nRF52840 在 Zephyr 示例开发里的板级要点。
完整安装、构建、烧录命令见 [入门指南](../getting-started.md)。

## UF2 烧录

XIAO nRF52840 出厂带 Adafruit nRF52 Bootloader，日常烧录应走 UF2：

```sh
seeed-zephyr flash xiao_nrf52840 --monitor
```

本仓库 CLI 会调用 Zephyr 的 `uf2` runner，不走默认的 `nrfutil` runner。

如果开发板已经运行本仓库示例，CLI 会先通过 USB CDC 1200 baud 请求开发板进入
UF2 下载模式，再调用 Zephyr 的 UF2 runner。

如果直接使用 Zephyr 命令，先双击 `RESET` 进入 UF2 下载模式，再运行：

```sh
west flash --runner uf2
```

## 免双击 RESET 重复烧录

目标：程序已经运行后，下次烧录可以由电脑通过 USB CDC 串口请求开发板进入 UF2 模式。

自建示例要保留这些点：

- `prj.conf`：启用 reboot、UART line control、USB CDC 串口和 console。
- `src/main.c`：监听 `UART_LINE_CTRL_BAUD_RATE`。
- 当 baud rate 变成 `1200` 时，写入 `GPREGRET` 值 `0x57`，再调用 `sys_reboot(SYS_REBOOT_COLD)`。
- 如果主循环里有长时间 `k_msleep()`，拆成短间隔并在间隔中检查 1200 baud 请求。

可参考本仓库示例：

```text
examples/boards/xiao_nrf52840/blinky/prj.conf
examples/boards/xiao_nrf52840/blinky/src/main.c
```

## 手动进入 UF2 下载模式

当当前固件还不支持自动请求 UF2，或 USB CDC 串口不可见时，使用这个恢复方式：

1. 快速双击 `RESET`。
2. 等待电脑出现 UF2 存储盘。
3. 重新运行烧录命令。

## USB CDC 串口输出

目标：`printk()` 输出可以通过 USB 串口被 monitor 看到。

XIAO nRF52840 的 Zephyr board 默认提供 USB CDC console。自建示例至少保留：

```conf
CONFIG_PRINTK=y
CONFIG_SERIAL=y
CONFIG_CONSOLE=y
CONFIG_UART_CONSOLE=y
```

如果程序启动后立刻打印但 monitor 看不到开头几行，可以给应用增加启动延迟：

```conf
CONFIG_BOOT_DELAY=5000
```

退出 monitor：

```text
Ctrl+]
```
