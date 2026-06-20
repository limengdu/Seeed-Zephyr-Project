# XIAO RP2040 开发板说明

这页记录 Seeed Studio XIAO RP2040 在 Zephyr 下已经验证过的行为。

一句话总结：XIAO RP2040 仍然使用 UF2 U 盘模式烧录，但装入本仓库固件后，CLI 可以自动让板子进入 UF2 模式。

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

装入本仓库的 `xiao_rp2040/blinky` 固件后，CLI 会用 1200 baud 打开开发板的 USB CDC 串口。
正在运行的固件会把这个动作当成进入 bootloader 的请求，然后自动重启到 UF2 模式，最后由 Zephyr 的
UF2 runner 复制新固件。

如果板子当前运行的是旧固件，不支持这个 1200 baud 请求，就需要手动进入 UF2 模式：按住 BOOTSEL
再插入 USB，或者按住 BOOTSEL 再按 RESET。macOS 上常见卷路径是 `/Volumes/RPI-RP2`。
Linux、Windows 或 WSL2 USB 转发环境里的名字和路径可能不同。关键不是路径长什么样，
而是运行 `west flash` 的环境必须能看到这个 UF2 存储卷。

如果开发板没有进入 UF2 模式，Zephyr 会报：

```text
No matching UF2 partitions found
```

本仓库 CLI 会先尝试 1200 baud 自动请求。如果找不到正在运行的 USB CDC 串口，或者请求后仍然看不到
UF2 卷，就会追加 BOOTSEL 恢复提示。

一句话总结：RP2040 烧录本质仍然是复制 UF2 文件；串口只负责通知正在运行的仓库固件进入 UF2 模式。

## 预期连续烧录行为

已经验证到的行为是：

- 如果板子当前是旧固件，第一次安装本仓库固件可能需要手动按 BOOTSEL，让 UF2 卷先出现。
- 烧录完成后，开发板会重启进入应用程序，UF2 卷会消失，然后应用程序暴露 USB CDC 串口给 monitor 使用。
- 连续第二次、第三次、第四次运行 `seeed-zephyr flash xiao_rp2040 --monitor` 都已经验证通过，
  中间不需要再次手动进入 UF2 模式。
- 正常拔插 USB 后，只要开发板启动的是本仓库固件，并且重新暴露出一个 USB CDC 串口，后续烧录也应继续走
  自动请求流程。如果串口没有出现，手动 BOOTSEL 仍然是恢复方式。

一句话总结：手动 BOOTSEL 是首次安装旧固件或异常恢复用的，不是本仓库固件正常连续烧录的日常步骤。

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
- 连续第二次、第三次、第四次运行 `seeed-zephyr flash xiao_rp2040 --monitor` 都通过 USB CDC 串口
  1200 baud 请求自动进入 UF2 模式，不需要手动 BOOTSEL。

详细硬件记录在
[`AI use/HARDWARE_VERIFICATION.md`](../../../AI%20use/HARDWARE_VERIFICATION.md)。

一句话总结：这个示例已经过真实硬件验证；装入本仓库固件后，重复烧录不再需要手动 BOOTSEL。
