# XIAO RA4M1 Zephyr 开发指南

本页只记录 Seeed Studio XIAO RA4M1 在 Zephyr 示例开发里的板级要点。
完整安装、构建、烧录命令见 [入门指南](../getting-started.md)。

## USB DFU 烧录

本仓库使用 XIAO RA4M1 板载 USB DFU bootloader 烧录固件：

```sh
seeed-zephyr flash xiao_ra4m1 --monitor
```

setup 选择 `xiao_ra4m1`，或不选择开发板执行全量 setup 时，会安装 `dfu-util`。
CLI 会把 Zephyr 构建产物转换成适合 DFU bootloader 的紧凑 bin，然后调用 `dfu-util`
上传。

如果板子当前正在运行带 DFU runtime 的固件，CLI 可以直接从运行态切到 DFU 并上传。
如果板子当前运行的固件没有 DFU runtime，烧录前需要先手动进入 DFU bootloader。

## 应用起始地址

XIAO RA4M1 的板载 DFU bootloader 占用 flash 前 16 KB。Zephyr 示例必须从 `0x4000`
开始运行：

```conf
CONFIG_FLASH_LOAD_OFFSET=0x4000
```

新建 RA4M1 示例时，也要保留这个配置。

## 进入 DFU Bootloader

如果烧录时电脑没有看到 DFU 设备，手动进入 bootloader：

1. 连接 XIAO RA4M1 的 USB 口。
2. 按住右侧 Boot。
3. 点按左侧 Reset。
4. Reset 松开后继续按住 Boot 约 1 到 2 秒。
5. 重新运行烧录命令。

## 串口 Monitor

本仓库基础示例把 Zephyr console 放到 USB CDC 串口。烧录后打开串口：

```sh
seeed-zephyr monitor xiao_ra4m1
```

如果电脑上同时插了多个 USB 串口设备，指定端口：

```sh
seeed-zephyr monitor xiao_ra4m1 --port /dev/cu.usbmodem1101
```

退出 monitor：

```text
Ctrl+]
```

## 调试

XIAO RA4M1 的 Zephyr debug 默认使用 J-Link。调试时需要把外部调试器连接到底部 SWD 焊盘。
普通烧录不需要 J-Link。

参考资料：[Zephyr XIAO RA4M1 文档](https://docs.zephyrproject.org/latest/boards/seeed/xiao_ra4m1/doc/index.html)。
