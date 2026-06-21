# XIAO RA4M1 Zephyr 开发指南

本页只记录 XIAO RA4M1 的板级开发要点。完整命令流程见 [入门指南](../getting-started.md)。

## USB DFU 烧录

常用命令：

```sh
seeed-zephyr flash xiao_ra4m1 --monitor
```

setup 选择 `xiao_ra4m1`，或执行全量 setup 时，会安装 `dfu-util`。
CLI 会生成适合板载 USB DFU bootloader 的 bin 文件，并通过 `dfu-util` 上传。

首次安装本仓库固件时，如果当前固件不能自动进入 DFU，需要手动进入 DFU bootloader：

1. 按住 Boot。
2. 点按 Reset。
3. Reset 松开后继续按住 Boot 约 1 到 2 秒。
4. 重新运行烧录命令。

## 应用起始地址

RA4M1 板载 DFU bootloader 占用 flash 前 16 KB。Zephyr 示例必须保留：

```conf
CONFIG_FLASH_LOAD_OFFSET=0x4000
```

## 后续免按 Boot 烧录

自建 RA4M1 示例如果希望第二次、第三次烧录不再手动进 DFU，需要同时支持：

```conf
CONFIG_REBOOT=y
CONFIG_UART_LINE_CTRL=y
CONFIG_USB_DEVICE_STACK_NEXT=y
CONFIG_CDC_ACM_SERIAL_INITIALIZE_AT_BOOT=y
```

程序里要检测 USB CDC 串口的 `1200` baud 请求，然后：

1. 向 `R_SYSTEM->VBTBKR[0]` 写入 `0x07738135`。
2. 关闭 `R_USB_FS0->SYSCFG_b.DPRPU`。
3. 调用 `sys_reboot(SYS_REBOOT_COLD)`。

本仓库基础示例已经包含这套入口，可作为自建示例参考。

## ROM Boot 恢复烧录

当板载 DFU bootloader 丢失时，可以通过 Renesas ROM bootloader 恢复烧录。

1. 按住 Boot，点按 Reset，松开 Boot，进入 ROM Boot 模式（电脑枚举 `RA USB Boot` 或 `045B:0261`）。
2. 运行烧录命令：

```sh
seeed-zephyr flash xiao_ra4m1 --monitor
```

CLI 自动检测到 ROM Boot 设备后，按 DFU 偏移构建应用固件，并把 DFU bootloader 与应用固件合并后，通过
ROM bootloader 串口协议（9600 baud，256 字节分块）写入 flash。烧录完成后按 Reset 启动新固件。

ROM Boot 恢复烧录同时写回 DFU bootloader，恢复完成后板子回到出厂状态，后续烧录走正常 DFU 流程。

## 串口 Monitor

打开串口：

```sh
seeed-zephyr monitor xiao_ra4m1
```

退出 monitor：

```text
Ctrl+]
```

## 调试

Zephyr debug 默认使用 J-Link，需要外部调试器连接底部 SWD 焊盘。普通烧录不需要 J-Link。

参考资料：[Zephyr XIAO RA4M1 文档](https://docs.zephyrproject.org/latest/boards/seeed/xiao_ra4m1/doc/index.html)。
