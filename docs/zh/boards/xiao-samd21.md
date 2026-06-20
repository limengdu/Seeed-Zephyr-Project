# XIAO SAMD21 开发板说明

这页记录 Seeed Studio XIAO SAMD21 在 Zephyr 下已经验证过的行为。

一句话总结：只要板子里已经烧录了本仓库验证过的 `blinky` 固件，后续重复烧录通常不需要手动进入 bootloader。

## 已验证的仓库示例

仓库示例：

```sh
examples/boards/xiao_samd21/blinky
```

构建、烧录，并打开串口监视器：

```sh
seeed-zephyr flash xiao_samd21 --monitor
```

如果电脑上只出现一个 USB 串口，CLI 可以自动检测端口。如果同时插着多个 USB 串口设备，
就显式传入端口：

```sh
seeed-zephyr flash xiao_samd21 --monitor --port /dev/cu.usbmodem1101
```

一句话总结：先用默认命令；只有自动检测不知道选哪个串口时，才手动加 `--port`。

## 为什么正常情况下不需要手动 reset

XIAO SAMD21 使用兼容 BOSSA 的 bootloader。通俗说，bootloader 就像“收快递的人”，
它负责先接收新固件，然后再让主程序运行。

SAMD21 开发板通常支持 1200 baud touch reset。大白话说，就是电脑先用 1200 这个特殊串口速度
碰一下开发板的 USB 串口。正在运行的固件识别到这个动作后，会自动重启进入 bootloader。
接下来 Zephyr 的 BOSSA runner 会调用 `bossac`，把新固件写进去。

本仓库的 `xiao_samd21/blinky` 示例启用了 USB CDC ACM 串口输出，并且把 CDC ACM 设备命名成
Zephyr 的 SAMD21 BOSSA reset 钩子能找到的名字。所以烧录过这版固件以后，可以连续自动烧录。

一句话总结：正在运行的固件必须暴露正确的 USB 串口，Zephyr 才能让板子自动重启进 bootloader。

## 预期烧录行为

烧录过本仓库验证固件以后：

- 第二次、第三次以及后续继续运行 `seeed-zephyr flash xiao_samd21 --monitor`，通常不需要双击 reset。
- 拔掉 USB 再插回来以后，只要还是这个验证固件正常启动，并且 USB 串口重新出现，通常也不需要手动进 bootloader。
- 如果板子之前烧录的是不带正确 USB CDC ACM 行为的固件，第一次可能仍然需要手动进一次 bootloader，用来装入这版验证固件。

一句话总结：正确固件已经在板子上运行后，后续上传应该接近 Arduino 那种自动上传体验。

## 哪些情况仍可能需要手动进 bootloader

以下情况仍可能需要手动进入 bootloader：

- 当前固件没有启用 USB CDC ACM 串口；
- 当前固件在 USB 串口准备好之前就崩溃；
- 其他固件覆盖了本仓库验证示例；
- USB 串口因为数据线、Hub、操作系统问题或其他程序占用而不可见；
- 同时连接了多个串口设备，并且选错了端口。

XIAO SAMD21 手动进入 bootloader 的方式是双击 reset 按钮，然后重新运行烧录命令。

一句话总结：手动进 bootloader 是恢复手段，不是本仓库验证示例的正常日常流程。

## 验证证据

本仓库已经为 `xiao_samd21` 记录了真实硬件证据：

- `seeed-zephyr flash xiao_samd21 --monitor` 完成了构建、烧录、校验，并打开串口监视器。
- 串口输出里看到了 Zephyr 启动信息和持续出现的 LED 状态。
- 连续第二次运行 `seeed-zephyr flash xiao_samd21 --monitor`，没有手动 reset，也通过了。

详细硬件记录在
[`AI use/HARDWARE_VERIFICATION.md`](../../../AI%20use/HARDWARE_VERIFICATION.md)。

一句话总结：这里写的不是只靠构建推测出来的，而是来自真实硬件验证。
