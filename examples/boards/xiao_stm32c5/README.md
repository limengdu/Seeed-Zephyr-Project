# xiao_stm32c5

## English

This directory contains board demos for Seeed Studio XIAO STM32C5.

The baseline demo is `blinky`. It builds for the upstream Zephyr target
`xiao_stm32c5/stm32c5a3xx`, toggles the user LED (`led0`, PB12, active low),
and prints the LED state to the USB CDC ACM console (115200 baud).

The board ships with a TinyUF2 bootloader that occupies the first 32 KiB of
flash, so the application starts at `0x08008000`. The build produces a UF2
image (family id `0x00C5C5C5`).

Usage:

- Connect the board through its USB-C port. The console appears as a USB serial
  port once the application is running.
- Upload copies the UF2 image to the `XIAOC5BOOT` mass storage volume (USB id
  `2886:00C5`).
- Enter the bootloader by hand with a double tap of RESET: press RESET twice
  within about half a second, then rerun the upload.
- The BOOT pad (PH2) is sampled while the board resets. Leave it released
  during power-on and reset.

## 中文

这个目录保存 Seeed Studio XIAO STM32C5 的开发板 demo。

基线 demo 是 `blinky`。它面向上游 Zephyr target `xiao_stm32c5/stm32c5a3xx` 构建，翻转用户 LED（`led0`，PB12，低电平点亮），并通过 USB CDC ACM 控制台打印 LED 状态（115200 波特率）。

开发板出厂带有 TinyUF2 引导程序，占用 flash 开头的 32 KiB，因此应用程序从 `0x08008000` 开始。构建会生成 UF2 镜像（family id `0x00C5C5C5`）。

使用说明：

- 通过板上的 USB-C 口连接电脑。应用程序运行后，控制台显示为一个 USB 串口。
- 上传把 UF2 镜像复制到 `XIAOC5BOOT` 存储盘（USB 标识 `2886:00C5`）。
- 手动进入引导程序的方法是双击 RESET：在大约半秒内按两次 RESET，然后重新上传。
- BOOT 触点（PH2）在复位时被采样。上电和复位时松开它。
