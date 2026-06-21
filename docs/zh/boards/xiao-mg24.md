# XIAO MG24 Zephyr 开发指南

本页只记录 Seeed Studio XIAO MG24 在 Zephyr 示例开发里的板级要点。
完整安装、构建、烧录命令见 [入门指南](../getting-started.md)。

## Debug Mate OpenOCD 烧录

XIAO MG24 通过 Seeed Studio XIAO Debug Mate 烧录时，需要使用 Seeed 提供的
MG24 OpenOCD 包。普通 Zephyr SDK OpenOCD 可能缺少 `target/efm32s2_g23.cfg`。

下载并解压 Seeed 文档里的 `XIAO_MG24_Mac_Linux_OpenOCD-v0.12.0` 后，设置环境变量：

```sh
export SEEED_ZEPHYR_MG24_OPENOCD=/path/to/XIAO_MG24_Mac_Linux_OpenOCD-v0.12.0
```

然后运行：

```sh
seeed-zephyr flash xiao_mg24 --monitor
```

CLI 会继续调用 Zephyr 的 `west flash`，并把 OpenOCD runner 指向这个 MG24 OpenOCD 包。

参考资料：[Seeed XIAO Debug Mate - XIAO MG24](https://wiki.seeedstudio.com/xiao_debug_mate_debug/#for-seeed-studio-xiao-mg24)。

## HEX 固件

如果绕过 CLI 手动调用 OpenOCD，使用 Zephyr 生成的 `zephyr.hex`。
不要把 `zephyr.elf` 当作 MG24 Debug Mate 烧录文件。

CLI 会从 Zephyr build 目录使用正确的 `.hex` 输出，不需要手动复制文件。

## 串口 Monitor

`--monitor` 会在烧录成功后查找一个 USB 串口并打开 pyserial miniterm：

```sh
seeed-zephyr monitor xiao_mg24
```

如果电脑上同时插了多个 USB 串口设备，指定端口：

```sh
seeed-zephyr monitor xiao_mg24 --port /dev/cu.usbmodem1101
```

退出 monitor：

```text
Ctrl+]
```
