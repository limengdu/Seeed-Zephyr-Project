# xiao_nrf54lm20a

## English

This directory contains board demos for Seeed Studio XIAO nRF54LM20A.

The baseline demo is `blinky`. It builds for the upstream Zephyr target
`xiao_nrf54lm20a/nrf54lm20a/cpuapp` (the application core), toggles the blue LED
(`led0`, GPIO1 pin 23, active low), and prints the LED state to the USB serial
console provided by the on-board SAMD11 debugger (`uart20`, 115200 baud).

Usage:

- Connect the board through its USB-C port. The on-board SAMD11 CMSIS-DAP
  debugger handles flashing, and its USB serial port carries the console.
- Upload uses Zephyr's default runner for this board.
- The red and green LEDs are `led1` and `led2`.

## 中文

这个目录保存 Seeed Studio XIAO nRF54LM20A 的开发板 demo。

基线 demo 是 `blinky`。它面向上游 Zephyr target `xiao_nrf54lm20a/nrf54lm20a/cpuapp`（应用核）构建，翻转蓝色 LED（`led0`，GPIO1 的 23 号引脚，低电平点亮），并通过板载 SAMD11 调试器提供的 USB 串口控制台打印 LED 状态（`uart20`，115200 波特率）。

使用说明：

- 通过板上的 USB-C 口连接电脑。板载 SAMD11 CMSIS-DAP 调试器负责烧录，它的 USB 串口承载控制台。
- 上传使用该板在 Zephyr 中的默认烧录器。
- 红色和绿色 LED 分别是 `led1` 和 `led2`。
