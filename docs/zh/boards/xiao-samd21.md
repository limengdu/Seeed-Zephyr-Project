# XIAO SAMD21 Zephyr 开发指南

本页只记录 Seeed Studio XIAO SAMD21 在 Zephyr 示例开发里的板级要点。
完整安装、构建、烧录命令见 [入门指南](../getting-started.md)。

## BOSSA 烧录

XIAO SAMD21 使用兼容 BOSSA 的 bootloader。烧录时，Zephyr 的 `bossac`
runner 会把固件写入开发板。

常用命令：

```sh
seeed-zephyr flash xiao_samd21 --monitor
```

如果系统提示缺少 `bossac`，先安装这块板子需要的烧录工具，再重新运行烧录命令。

## 免双击 RESET 重复烧录

目标：程序已经运行后，下次烧录可以由电脑通过 USB CDC 串口请求开发板重启进入
bootloader。

开发自己的 XIAO SAMD21 示例时，需要处理这些文件：

- `prj.conf`：启用旧版 USB device stack、UART line control、USB CDC 串口和 console。
- `app.overlay`：声明 `cdc_acm_uart0`，并设置 `label = "CDC_ACM_0"`。
- `src/main.c`：启动时调用 `usb_enable(NULL)`，让 USB CDC 串口出现。

关键配置：

```conf
CONFIG_UART_LINE_CTRL=y
CONFIG_USB_DEVICE_STACK=y
CONFIG_USB_DEVICE_INITIALIZE_AT_BOOT=n
CONFIG_USB_DEVICE_STACK_NEXT=n
CONFIG_SERIAL=y
CONFIG_CONSOLE=y
CONFIG_UART_CONSOLE=y
```

关键 `app.overlay` 结构：

```dts
/ {
	chosen {
		zephyr,console = &cdc_acm_uart0;
	};
};

&zephyr_udc0 {
	cdc_acm_uart0: cdc_acm_uart0 {
		compatible = "zephyr,cdc-acm-uart";
		label = "CDC_ACM_0";
	};
};
```

参考实现：`examples/boards/xiao_samd21/blinky`。

## USB CDC 串口输出

目标：`printk()` 输出可以通过 USB 串口被 monitor 看到。

需要处理这些文件：

- `prj.conf`：启用 `CONFIG_PRINTK`、`CONFIG_SERIAL`、`CONFIG_CONSOLE`、
  `CONFIG_UART_CONSOLE` 和 USB device stack。
- `app.overlay`：把 `zephyr,console` 指向 `cdc_acm_uart0`。
- `src/main.c`：在输出日志前调用 `usb_enable(NULL)`。

查看串口：

```sh
seeed-zephyr monitor xiao_samd21
```

退出 monitor：

```text
Ctrl+]
```

## 手动进入 Bootloader 模式

这是自动烧录不可用时的恢复方式：

1. 双击 `RESET`。
2. 等待 bootloader 串口出现。
3. 重新运行烧录命令。
