# xiao_stm32c5 blinky

## English

This demo toggles the board LED through Zephyr GPIO. It is the baseline demo for
Seeed Studio XIAO STM32C5 and produces a TinyUF2 image.

The board overlay enables the USB 48 MHz HSE clock and PA11/PA12 pins for the
Zephyr v4.5.0 baseline. The console uses USB id `2886:00C5` at 115200 baud.
A 1200-baud serial request restarts the application into the factory TinyUF2
bootloader, so consecutive uploads run automatically. For manual entry, press
RESET twice within about half a second, then upload to `XIAOC5BOOT` or
`XIAOSTM32C5`.

After updating to release 0.5.4 or later, create a fresh project from this
example to include its board overlay, configuration, and source.

Build from the repository root:

```sh
bash scripts/build-example.sh examples/boards/xiao_stm32c5/blinky
```

## 中文

这个 demo 通过 Zephyr GPIO 翻转板载 LED，是 Seeed Studio XIAO STM32C5 的基线 demo，并生成 TinyUF2 镜像。

板级补丁为 Zephyr v4.5.0 基线启用 USB 的 48 MHz HSE 时钟和 PA11/PA12 引脚。控制台使用 USB 标识 `2886:00C5`，波特率为 115200。收到 1200 波特率串口请求后，应用程序会复位进入出厂 TinyUF2 引导程序，因此可以连续自动上传。手动进入时，在大约半秒内按两次 RESET，再上传到 `XIAOC5BOOT` 或 `XIAOSTM32C5` 存储盘。

更新到 0.5.4 或更新版本后，从本示例重新创建工程，即可包含配套的板级补丁、配置和源代码。

从仓库根目录构建:

```sh
bash scripts/build-example.sh examples/boards/xiao_stm32c5/blinky
```
