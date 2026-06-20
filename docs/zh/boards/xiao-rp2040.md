# XIAO RP2040 开发板说明

这页记录 Seeed Studio XIAO RP2040 在 Zephyr 下已经验证过的行为。

一句话总结：XIAO RP2040 使用 UF2 U 盘模式烧录，所以每次烧录前，都要先让 UF2 卷出现在电脑上。

## 已验证的仓库示例

仓库示例：

```sh
examples/boards/xiao_rp2040/blinky
```

构建、烧录，并打开串口监视器：

```sh
seeed-zephyr flash xiao_rp2040 --monitor
```

烧录完成后，如果电脑上只出现一个 USB 串口，CLI 可以自动检测端口。如果同时插着多个 USB 串口设备，
就显式传入端口：

```sh
seeed-zephyr flash xiao_rp2040 --monitor --port /dev/cu.usbmodem1101
```

一句话总结：先用默认命令；只有自动检测不知道选哪个串口时，才手动加 `--port`。

## UF2 烧录行为

XIAO RP2040 使用 UF2 bootloader。通俗说，bootloader 会把开发板临时变成一个 USB 存储盘，
就像一个很小的 U 盘。Zephyr 的 UF2 runner 会把生成好的 `zephyr.uf2` 文件复制到这个盘里。

进入 UF2 模式的方式是：按住 BOOTSEL 再插入 USB，或者按住 BOOTSEL 再按 RESET。macOS 上常见
卷路径是 `/Volumes/RPI-RP2`。Linux、Windows 或 WSL2 USB 转发环境里的名字和路径可能不同。
关键不是路径长什么样，而是运行 `west flash` 的环境必须能看到这个 UF2 存储卷。

如果开发板没有进入 UF2 模式，Zephyr 会报：

```text
No matching UF2 partitions found
```

本仓库 CLI 会在这类烧录失败后追加 BOOTSEL 提示。

一句话总结：RP2040 烧录本质上是把固件复制到 bootloader U 盘，不是串口上传。

## 预期连续烧录行为

已经验证到的行为是：

- 开发板处于 UF2 模式、UF2 卷已经挂载时，`seeed-zephyr flash xiao_rp2040 --monitor` 可以成功。
- 烧录完成后，开发板会重启进入应用程序，UF2 卷会消失，然后应用程序暴露 USB CDC 串口给 monitor 使用。
- 如果第二次不重新进入 UF2 模式，直接再次烧录，会失败并出现 `No matching UF2 partitions found`
  和 CLI 的 BOOTSEL 提示。

一句话总结：和已经验证过的 XIAO SAMD21 不同，当前 RP2040 流程应按“每次烧录都需要先进入 UF2 模式”来使用。

## 串口监视器行为

本仓库的 `xiao_rp2040/blinky` 示例启用了 USB CDC ACM console。这样
`seeed-zephyr flash xiao_rp2040 --monitor` 在烧录成功后，可以打开 pyserial miniterm，
看到持续输出的 LED 状态。

退出 monitor 的快捷键是：

```text
Ctrl+]
```

如果 monitor 没有打开，先等开发板烧录后重新枚举，确认 USB 数据线支持数据传输；如果电脑上同时有多个
USB 串口设备，就用 `--port` 明确指定端口。

一句话总结：烧录走 UF2 U 盘，日志输出走固件启动后暴露出来的 USB CDC 串口。

## 验证证据

本仓库已经为 `xiao_rp2040` 记录了真实硬件证据：

- 未进入 UF2 模式时烧录失败，并出现预期的 BOOTSEL/UF2 提示。
- `seeed-zephyr flash xiao_rp2040 --monitor` 完成构建，把 `zephyr.uf2` 复制到
  `/Volumes/RPI-RP2`，并打开串口监视器。
- 串口输出里看到了持续出现的 `LED state: OFF` 和 `LED state: ON`。
- 连续第二次不重新进入 UF2 模式直接烧录，会出现预期的 `No matching UF2 partitions found`
  和 BOOTSEL 提示。

详细硬件记录在
[`AI use/HARDWARE_VERIFICATION.md`](../../../AI%20use/HARDWARE_VERIFICATION.md)。

一句话总结：这个示例已经过真实硬件验证，但重复烧录仍然需要 RP2040 的 UF2 bootloader 卷。
