# xiao_nrf54lm20b

## English

This directory contains board demos for Seeed Studio XIAO nRF54LM20B.

The baseline demo is `blinky`. It builds for the upstream Zephyr target
`xiao_nrf54lm20b/nrf54lm20b/cpuapp` (the application core), toggles the blue LED
(`led0`, GPIO1 pin 23, active low), and prints the LED state to the USB CDC ACM
console (115200 baud).

The board ships with a factory MCUboot firmware loader. The demo is linked for
that loader's application slot and signed at build time with the MCUboot
development key already present in the Zephyr workspace
(`bootloader/mcuboot/root-ed25519.pem`). Upload sends the signed image through
the USB loader using the CLI's built-in SMP uploader.

Usage:

- Connect the board through its USB-C port. The console appears as a USB serial
  port once the application is running.
- For the first upload from the factory application, hold the user button
  (P0.09), press RESET, and release the button. Holding the button while
  connecting USB also enters the loader.
- With this example running, Upload opens its application port at 9600 baud and
  then 1200 baud to reboot into the loader automatically.
- The built-in uploader uses the existing Python serial environment and a
  32-byte SHA-256 transfer checksum.
- The red and green LEDs are `led1` and `led2`.

## 中文

这个目录保存 Seeed Studio XIAO nRF54LM20B 的开发板 demo。

基线 demo 是 `blinky`。它面向上游 Zephyr target `xiao_nrf54lm20b/nrf54lm20b/cpuapp`（应用核）构建，翻转蓝色 LED（`led0`，GPIO1 的 23 号引脚，低电平点亮），并通过 USB CDC ACM 控制台打印 LED 状态（115200 波特率）。

开发板出厂带有 MCUboot 固件加载器。demo 链接到该加载器的应用分区，并在构建时使用 Zephyr 工作区中已有的 MCUboot 开发密钥（`bootloader/mcuboot/root-ed25519.pem`）签名。上传通过命令行工具内置的 SMP 上传器把签名后的镜像发给 USB 加载器。

使用说明：

- 通过板上的 USB-C 口连接电脑。应用程序运行后，控制台显示为一个 USB 串口。
- 首次从出厂应用上传时，按住用户按键（P0.09）再按 RESET，随后松开按键。按住用户按键再插上 USB 也能进入加载器。
- 本示例运行后，上传会依次以 9600、1200 波特率打开应用串口，让开发板自动重启进入加载器。
- 内置上传器使用现有 Python 串口环境，以 32 字节 SHA-256 摘要校验传输文件。
- 红色和绿色 LED 分别是 `led1` 和 `led2`。

## Board notes / 板级说明

- [English](https://github.com/limengdu/Seeed-Zephyr-Project/blob/main/docs/en/boards/xiao-nrf54lm20b.md)
- [中文](https://github.com/limengdu/Seeed-Zephyr-Project/blob/main/docs/zh/boards/xiao-nrf54lm20b.md)
