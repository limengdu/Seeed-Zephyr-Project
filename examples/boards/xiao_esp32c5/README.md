# xiao_esp32c5

## English

This directory contains board demos for Seeed Studio XIAO ESP32C5.

The baseline demo is `blinky`. It builds for the upstream Zephyr target
`xiao_esp32c5/esp32c5/hpcore` (the high-performance core), toggles the user LED,
and prints the LED state to the USB serial console.

Usage:

- Connect the board through its USB-C port. Upload and the serial console share
  this port (USB Serial/JTAG).
- Upload finishes with a reset command, so the board boots the new image on its
  own and the LED blinks once per second.
- Close other serial monitors on the port before uploading; the extension closes
  its earlier Upload and Monitor terminals for you.
- To enter download mode by hand, hold BOOT while plugging in USB, then press
  RESET after the upload.

## 中文

这个目录保存 Seeed Studio XIAO ESP32C5 的开发板 demo。

基线 demo 是 `blinky`。它面向上游 Zephyr target `xiao_esp32c5/esp32c5/hpcore`（高性能主核）构建，翻转用户 LED，并通过 USB 串口控制台打印 LED 状态。

使用说明：

- 通过板上的 USB-C 口连接电脑，上传和串口控制台共用这个口（USB Serial/JTAG）。
- 上传结束时会自动发送复位命令，开发板随即运行新程序，LED 每秒闪烁一次。
- 上传前关闭占用该串口的其他串口监视器；插件会自动关闭它之前打开的 Upload 和 Monitor 终端。
- 需要手动进入下载模式时，按住 BOOT 键再插上 USB，上传完成后按一下 RESET。
