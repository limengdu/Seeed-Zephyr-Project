# xiao_nrf52840 blinky

## English

This demo toggles the board LED through Zephyr GPIO and prints the LED state
over the board USB CDC console. It is the baseline demo for Seeed Studio XIAO
nRF52840.

It also handles USB CDC 1200 baud bootloader requests so later CLI flashes can
enter the UF2 bootloader without double-tapping `RESET`.

Build from the repository root:

```sh
bash scripts/build-example.sh examples/boards/xiao_nrf52840/blinky
```

## 中文

这个 demo 通过 Zephyr GPIO 翻转板载 LED，并通过开发板 USB CDC console 输出 LED 状态。
它是 Seeed Studio XIAO nRF52840 的基线 demo。

它也会处理 USB CDC 1200 baud bootloader 请求，让后续 CLI 烧录可以不再双击 `RESET`
就进入 UF2 bootloader。

从仓库根目录构建:

```sh
bash scripts/build-example.sh examples/boards/xiao_nrf52840/blinky
```
