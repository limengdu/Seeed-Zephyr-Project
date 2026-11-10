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
- Upload requests TinyUF2 mode through the application USB serial port at 1200
  baud, then copies the UF2 image to the `XIAOC5BOOT` or `XIAOSTM32C5` volume.
  The application uses USB id `2886:00C5` and returns to its serial console
  after the upload.
- For manual bootloader entry, press RESET twice within about half a second.
  Upload uses the mounted TinyUF2 volume directly.
- Create a fresh `blinky` project from release 0.5.4 or later to include the
  USB clock/pin overlay and automatic bootloader entry support.
- The BOOT pad (PH2) is sampled while the board resets. Leave it released
  during power-on and reset.

## 中文

这个目录保存 Seeed Studio XIAO STM32C5 的开发板 demo。

基线 demo 是 `blinky`。它面向上游 Zephyr target `xiao_stm32c5/stm32c5a3xx` 构建，翻转用户 LED（`led0`，PB12，低电平点亮），并通过 USB CDC ACM 控制台打印 LED 状态（115200 波特率）。

开发板出厂带有 TinyUF2 引导程序，占用 flash 开头的 32 KiB，因此应用程序从 `0x08008000` 开始。构建会生成 UF2 镜像（family id `0x00C5C5C5`）。

使用说明：

- 通过板上的 USB-C 口连接电脑。应用程序运行后，控制台显示为一个 USB 串口。
- 上传先通过应用程序的 USB 串口发送 1200 波特率请求，进入 TinyUF2 模式，再把 UF2 镜像复制到 `XIAOC5BOOT` 或 `XIAOSTM32C5` 存储盘。应用程序使用 USB 标识 `2886:00C5`，上传后恢复串口控制台。
- 手动进入引导程序时，在大约半秒内按两次 RESET。上传会直接使用已经挂载的 TinyUF2 存储盘。
- 使用 0.5.4 或更新版本重新创建 `blinky` 工程，即可带上 USB 时钟、引脚补丁和自动进入引导程序的支持。
- BOOT 触点（PH2）在复位时被采样。上电和复位时松开它。
