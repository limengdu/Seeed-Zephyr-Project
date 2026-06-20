# XIAO RP2040 Zephyr 开发指南

本页只记录 Seeed Studio XIAO RP2040 在 Zephyr 示例开发里的板级要点。
完整安装、构建、烧录命令见 [入门指南](../getting-started.md)。

## UF2 烧录

XIAO RP2040 使用 UF2 下载模式。开发时通常不需要手动拷贝 UF2 文件，直接运行：

```sh
seeed-zephyr flash xiao_rp2040 --monitor
```

如果直接使用 Zephyr 命令，需要构建时加入 RP2 boot mode retention snippet：

```sh
west build -p always -b xiao_rp2040 -S rp2-boot-mode-retention <app>
west flash
```

本仓库 CLI 会自动加入这个 snippet。

## 免按 BOOTSEL 重复烧录

目标：程序已经运行后，下次烧录可以由电脑通过 USB CDC 串口请求开发板进入 UF2 模式。

开发自己的 XIAO RP2040 示例时，需要处理这些文件：

- `prj.conf`：启用 reboot、UART line control、USB CDC 串口和 console。
- `app.overlay`：声明 `cdc_acm_uart0`，并把 `zephyr,console` 指向它。
- `src/main.c`：读取 `UART_LINE_CTRL_BAUD_RATE`；当主机把 USB CDC 打开为 `1200`
  baud 时，设置 `BOOT_MODE_TYPE_BOOTLOADER` 并调用 `sys_reboot()`。
- 构建命令：使用 `-S rp2-boot-mode-retention`。

关键配置：

```conf
CONFIG_REBOOT=y
CONFIG_UART_LINE_CTRL=y
CONFIG_SERIAL=y
CONFIG_CONSOLE=y
CONFIG_UART_CONSOLE=y
CONFIG_USB_DEVICE_STACK_NEXT=y
CONFIG_CDC_ACM_SERIAL_INITIALIZE_AT_BOOT=y
```

关键代码形态：

```c
ret = uart_line_ctrl_get(cdc_acm, UART_LINE_CTRL_BAUD_RATE, &baudrate);
if (ret == 0 && baudrate == 1200) {
	bootmode_set(BOOT_MODE_TYPE_BOOTLOADER);
	k_sleep(K_MSEC(50));
	sys_reboot(SYS_REBOOT_COLD);
}
```

参考实现：`examples/boards/xiao_rp2040/blinky/src/main.c`。

## USB CDC 串口输出

目标：`printk()` 输出可以通过 USB 串口被 monitor 看到。

需要处理这些文件：

- `prj.conf`：启用 `CONFIG_PRINTK`、`CONFIG_SERIAL`、`CONFIG_CONSOLE`、
  `CONFIG_UART_CONSOLE` 和 USB CDC。
- `app.overlay`：把 `zephyr,console` 指向 `cdc_acm_uart0`。
- `src/main.c`：使用 `printk()` 输出运行日志。

`app.overlay` 的关键结构：

```dts
/ {
	chosen {
		zephyr,console = &cdc_acm_uart0;
	};
};

&zephyr_udc0 {
	cdc_acm_uart0: cdc_acm_uart0 {
		compatible = "zephyr,cdc-acm-uart";
	};
};
```

查看串口：

```sh
seeed-zephyr monitor xiao_rp2040
```

退出 monitor：

```text
Ctrl+]
```

## 手动进入 UF2 下载模式

这是自动烧录不可用时的恢复方式：

1. 按住 `BOOTSEL`。
2. 插入 USB，或按一下 `RESET`。
3. 看到 `RPI-RP2` 存储盘后重新运行烧录命令。
