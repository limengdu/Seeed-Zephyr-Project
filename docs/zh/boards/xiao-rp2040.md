# XIAO RP2040 Zephyr 开发指南

面向 Seeed Studio XIAO RP2040 的最小开发、烧录和串口查看流程。

## 快速开始

最小示例：

```sh
examples/boards/xiao_rp2040/blinky
```

构建、烧录并打开串口：

```sh
seeed-zephyr flash xiao_rp2040 --monitor
```

看到 `LED state: ON/OFF` 循环输出，就说明构建、烧录、串口都正常。

## 日常开发流程

1. 修改示例代码：`examples/boards/xiao_rp2040/blinky/src/main.c`
2. 重新运行：

```sh
seeed-zephyr flash xiao_rp2040 --monitor
```

退出串口监视器：

```text
Ctrl+]
```

## 什么时候需要 BOOTSEL

正常重复烧录不需要每次按 `BOOTSEL`。

只有这些情况才需要手动进入 UF2 下载模式：

- 首次烧录无法自动进入下载模式；
- 当前程序没有 USB CDC 1200 baud 自动下载逻辑；
- 看到 `No matching UF2 partitions found`；
- 串口没有出现，CLI 无法触发自动下载。

手动进入 UF2：

1. 按住 `BOOTSEL`；
2. 插入 USB，或按一下 `RESET`；
3. 看到 `RPI-RP2` 存储盘后重新运行烧录命令。

## 自建示例要点

如果你新建 XIAO RP2040 示例，并希望保留免按键重复烧录，需要保留：

- USB CDC 串口输出；
- USB CDC 1200 baud 进入 UF2 的处理逻辑；
- RP2 boot mode retention snippet。

本仓库 CLI 会自动加 snippet。直接用 `west build` 时需要手动加：

```sh
west build -p always -b xiao_rp2040 -S rp2-boot-mode-retention <your-app>
```

参考实现：

```sh
examples/boards/xiao_rp2040/blinky/src/main.c
```

## 常见问题

### 多个串口设备

手动指定端口：

```sh
seeed-zephyr flash xiao_rp2040 --monitor --port /dev/cu.usbmodem1101
```

### monitor 没输出

检查 USB 线是否支持数据、是否选对串口、示例是否启用 USB CDC 串口。

### 每次都要 BOOTSEL

先烧录本仓库 `xiao_rp2040/blinky` 示例确认自动重复烧录可用，再把同样的 USB CDC 1200 baud 处理逻辑带到你的自定义示例里。
