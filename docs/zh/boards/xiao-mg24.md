# XIAO MG24 Zephyr 开发指南

本页只记录 Seeed Studio XIAO MG24 在 Zephyr 示例开发里的板级要点。
完整安装、构建、烧录命令见 [入门指南](../getting-started.md)。

## PyOCD 烧录

XIAO MG24 默认使用 Zephyr 官方配置的 `pyocd` runner：

```sh
seeed-zephyr flash xiao_mg24 --monitor
```

第一次使用前，需要安装 MG24 的 CMSIS pack：

```sh
pyocd pack install EFR32MG24B220F1536IM48
```

如果通过本仓库 setup 选择 `xiao_mg24`，或不选择开发板执行全量 setup，这一步会自动处理。

## Debug Mate 串口和调试器

XIAO MG24 板载 SAMD11 CMSIS-DAP 调试器，Zephyr 可以通过它进行烧录和调试。
电脑能看到 CMSIS-DAP 设备后，`pyocd` runner 会使用这个调试器连接 MG24。

查看串口：

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

## OpenOCD 备用路径

Zephyr 官方文档也说明 MG24 可使用 OpenOCD，但 OpenOCD 版本必须包含 MG24 flash 支持。
如果使用普通 OpenOCD 遇到 `target/efm32s2_g23.cfg` 或 flash 支持问题，优先回到本仓库默认的
`pyocd` 路径。

参考资料：[Zephyr XIAO MG24 文档](https://docs.zephyrproject.org/latest/boards/seeed/xiao_mg24/doc/index.html)。
