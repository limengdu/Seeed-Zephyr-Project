# XIAO SAMD21 DAC Ramp

## English

This demo outputs a repeating 10-bit sawtooth ramp through the XIAO SAMD21 DAC
on D0/A0. It reports selected DAC values while a USB serial monitor is
connected and uses a scheduler-aware delay in every output step.

Build from the repository root:

```sh
bash scripts/build-example.sh examples/boards/xiao_samd21/dac
```

## 中文

这个 demo 通过 XIAO SAMD21 的 D0/A0 输出循环递增的 10-bit 锯齿波。USB 串口监视器连接后，
程序会输出选定的 DAC 数值，并在每次输出后使用可调度延时。

从仓库根目录构建:

```sh
bash scripts/build-example.sh examples/boards/xiao_samd21/dac
```
