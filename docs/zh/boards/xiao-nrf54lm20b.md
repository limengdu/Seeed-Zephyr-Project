# XIAO nRF54LM20B

## 出厂固件布局

板上的 USB-C 直接连接 nRF54LM20B。出厂 MCUboot 启动链使用以下内部闪存分区：

| 区域 | 起始地址 | 大小 |
| --- | --- | --- |
| MCUboot | `0x000000` | 24 KiB |
| 应用分区 slot 0 | `0x006000` | 1784 KiB |
| 固件加载器 slot 1 | `0x1C4000` | 116 KiB |
| 存储区 | `0x1E1000` | 124 KiB |

应用面向 `xiao_nrf54lm20b/nrf54lm20b/cpuapp` 构建，启用
`CONFIG_MCUBOOT_BOOTLOADER_MODE_FIRMWARE_UPDATER=y`、pure Ed25519 签名，并使用
Zephyr 工作区的 MCUboot 开发密钥 `bootloader/mcuboot/root-ed25519.pem`。
镜像头占 `0x800` 字节。上传文件为 `build/zephyr/zephyr.signed.confirmed.bin`，
出厂加载器保留在原分区。

## 进入 USB 加载器

应用程序的 USB 标识是 `2886:8013`；出厂加载器是 `2886:0013`，设备名为
`CDC ACM serial backend`。

从出厂 Thread Co-Processor 应用首次上传时，按住用户按键（Button 0，P0.09），
再按 RESET，随后松开用户按键。按住 Button 0 再插入 USB 也能进入加载器。
电脑识别到加载器后，重新执行 Upload。

仓库 blinky 示例支持后续上传自动进入加载器。命令行工具依次以 9600、1200
波特率打开应用串口并拉低 DTR。示例每 50 毫秒检查一次 USB 串口设置，检测到
1200 波特率后，通过 `zephyr,boot-mode` 记录 `BOOT_MODE_TYPE_BOOTLOADER`，
随后重启，由 MCUboot 启动出厂加载器。示例的 `prj.conf` 包含所需的串口控制、
重启和启动模式保留配置。

## 镜像传输

命令行工具使用现有 Python 串口环境，通过加载器的 SMP 镜像上传协议发送签名文件。
传输校验使用整个上传文件的 32 字节 SHA-256 摘要；签名文件内部继续使用 pure
Ed25519 签名和 SHA-512 镜像摘要。

Nordic `nrfutil mcu-manager` 0.12.3 会把镜像的 64 字节 SHA-512 摘要放进上传请求。
出厂加载器对这个传输字段的长度上限为 32 字节，因此返回 `MGMT_ERR_EINVAL`；
使用协议版本 2 可看到更具体的镜像组错误 24（`INVALID_HASH`）。内置上传器使用
加载器支持的传输摘要，并按开发板确认的字节位置继续发送。

## 串口和 LED

应用控制台为 115200 波特率的 USB CDC ACM 串口。blinky 上传成功后，设备名为
`XIAO nRF54LM20B`，串口先打印 Zephyr 启动信息，再交替打印 `LED state: OFF`
和 `LED state: ON`。蓝色 LED 为 `led0`（GPIO1 的 23 号引脚，低电平点亮），
红色、绿色分别为 `led1`、`led2`。

使用 0.5.7 或更新版本插件新建示例项目，可包含 USB 标识和自动进入加载器的处理逻辑。
