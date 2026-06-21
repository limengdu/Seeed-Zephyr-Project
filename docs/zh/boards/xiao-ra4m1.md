# XIAO RA4M1 Zephyr 开发指南

本页只记录 Seeed Studio XIAO RA4M1 在 Zephyr 示例开发里的板级要点。
完整安装、构建、烧录命令见 [入门指南](../getting-started.md)。

## RFP 烧录

XIAO RA4M1 的 Zephyr 默认烧录路径是 `rfp` runner，也就是通过 Renesas Flash Programmer
CLI 使用板载 RA USB bootloader 写入固件。

```sh
seeed-zephyr flash xiao_ra4m1 --monitor
```

如果通过本仓库 setup 选择 `xiao_ra4m1`，或不选择开发板执行全量 setup，脚本会准备
`rfp-cli`。

## 进入 USB Bootloader

烧录前让板子进入 bootloader：

1. 连接 XIAO RA4M1 的 USB 口。
2. 按住右侧 Boot。
3. 点按左侧 Reset。
4. Reset 松开后继续按住 Boot 约 1 到 2 秒。
5. 重新运行烧录命令。

## 串口 Monitor

烧录后打开串口：

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
