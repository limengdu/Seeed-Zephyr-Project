# XIAO STM32C5 Zephyr 开发指南

本页只记录 Seeed Studio XIAO STM32C5 在 Zephyr v4.5.0 基线上的板级要点。
完整安装、构建、烧录命令见 [入门指南](../getting-started.md)。

## TinyUF2 镜像

出厂 TinyUF2 引导程序占用 flash 开头的 32 KiB。应用程序从 `0x08008000` 开始，
构建产物是 `zephyr.uf2`，family id 为 `0x00C5C5C5`。

```conf
CONFIG_BUILD_OUTPUT_UF2=y
CONFIG_BUILD_OUTPUT_UF2_FAMILY_ID="0x00C5C5C5"
```

上传把这个文件复制到引导盘：

```sh
seeed-zephyr flash xiao_stm32c5 --monitor
```

这块板子的出厂卷标是 `XIAOC5BOOT`。上游板级说明也使用 `XIAOSTM32C5`。
上传接受这两个卷标，也接受 `INFO_UF2.TXT` 里写明这块板子的卷
（`Model: Seeed XIAO C5`，`Board-ID: STM32C5A3-XIAO-C5`）。

## USB 时钟和引脚

v4.5.0 的板级定义启用了 USB 设备，但 48 MHz 时钟选择仍是关闭的，USB 引脚
也没有指定。启动时会清掉引导程序留下的时钟配置，所以 UF2 拷贝完成后，
应用程序不会出现在 USB 上。

blinky 的板级补丁打开已有的 `clk48` 节点，选用板上的 48 MHz HSE，并把
PA11（USB DM）和 PA12（USB DP）交给 USB：

```dts
&clk48 {
	clocks = <&rcc STM32_SRC_HSE CK48_SEL(3)>;
	status = "okay";
};

&usb {
	pinctrl-0 = <&usb_dm_pa11 &usb_dp_pa12>;
	pinctrl-names = "default";
};
```

在这个基线上自建应用时，把同一份补丁放在
`boards/xiao_stm32c5_stm32c5a3xx.overlay`。引脚名称来自 Zephyr 模块自带的
STM32 设备树。

参考：`examples/boards/xiao_stm32c5/blinky/boards/xiao_stm32c5_stm32c5a3xx.overlay`。

## 应用程序的 USB 标识

控制台是 USB CDC ACM，波特率 115200。上传按 USB 标识 `2886:00C5` 找到正在运行的
应用程序。

```conf
CONFIG_UART_LINE_CTRL=y
CONFIG_CDC_ACM_SERIAL_VID=0x2886
CONFIG_CDC_ACM_SERIAL_PID=0x00C5
CONFIG_CDC_ACM_SERIAL_MANUFACTURER_STRING="Seeed Studio"
CONFIG_CDC_ACM_SERIAL_PRODUCT_STRING="XIAO STM32C5"
```

## 连续上传

这个应用程序运行时，上传会以 1200 波特率打开 CDC 串口。应用程序每 50 毫秒读一次
`UART_LINE_CTRL_BAUD_RATE`。读到 1200 时，它把 `0xf01669ef` 写入 SRAM 的最后一个字，
然后复位进入出厂引导程序。

引导程序本身只是一个 U 盘，没有串口，所以 1200 波特率请求由正在运行的应用程序处理。
第一次给还没跑这个程序的板子上传时，用下面的手动方式。这个镜像跑起来之后，
下一次上传会自己发送 1200 波特率请求。

参考：`examples/boards/xiao_stm32c5/blinky/src/main.c`。

## 手动进入引导程序

第一次上传，或应用程序串口看不到时，用这条路径：

1. 在大约半秒内按两次 RESET。
2. 等待出现 `XIAOC5BOOT` 或 `XIAOSTM32C5` 存储盘。
3. 再次运行烧录命令。已经挂载的存储盘会被直接使用。

## BOOT 触点

BOOT 触点（PH2）在复位时被采样。上电和复位时松开它。

## 工程文件

从 0.5.4 或更新版本创建的工程带有板级补丁、USB 标识和 1200 波特率复位处理。
更新到该版本后，重新创建一个 `blinky` 工程。
