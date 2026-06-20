# xiao_rp2040 blinky

## English

This demo toggles the board LED through Zephyr GPIO and prints the LED state
through USB CDC serial. It is the baseline demo for Seeed Studio XIAO RP2040.

Build from the repository root:

```sh
bash scripts/build-example.sh examples/boards/xiao_rp2040/blinky
```

Build, flash, and open the monitor through the installed CLI:

```sh
seeed-zephyr flash xiao_rp2040 --monitor
```

## 中文

这个 demo 通过 Zephyr GPIO 翻转板载 LED，并通过 USB CDC 串口打印 LED 状态，
是 Seeed Studio XIAO RP2040 的基线 demo。

从仓库根目录构建:

```sh
bash scripts/build-example.sh examples/boards/xiao_rp2040/blinky
```

通过已安装 CLI 构建、烧录并打开 monitor：

```sh
seeed-zephyr flash xiao_rp2040 --monitor
```
