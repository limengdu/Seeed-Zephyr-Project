# xiao_rp2040 blinky

## English

This demo toggles the board LED through Zephyr GPIO and prints the LED state
through USB CDC serial. It is the baseline demo for Seeed Studio XIAO RP2040.
It also handles the 1200-baud USB CDC request used by the CLI to reboot into
UF2 mode for repeated flashing.

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
它也会处理 CLI 使用的 USB CDC 1200 baud 请求，用来在重复烧录时自动重启进入 UF2 模式。

从仓库根目录构建:

```sh
bash scripts/build-example.sh examples/boards/xiao_rp2040/blinky
```

通过已安装 CLI 构建、烧录并打开 monitor：

```sh
seeed-zephyr flash xiao_rp2040 --monitor
```
