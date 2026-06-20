# 入门指南：先构建本仓库里的示例

先说结论：这个仓库现在已经有自己的 XIAO 开发板 demo，放在 `examples/boards/`。
用户应该先构建这些本仓库示例，而不是手动去 Zephyr 源码目录里找 sample。

把它想成两层：

| 位置 | 它是什么 | 平时做什么 |
| --- | --- | --- |
| `~/seeed-zephyr-base` | 本项目 | 放 XIAO/Grove 示例、metadata、脚本、文档、验证结果 |
| `~/zephyrproject` | 上游 Zephyr 工作区 | 放 Zephyr 源码、SDK、west workspace 和固件构建输出 |

一句话总结：从 `~/seeed-zephyr-base` 运行 setup；CLI 安装后，就可以在任意目录使用 `seeed-zephyr`。

## 1. 这个项目解决什么问题

Zephyr 是一个嵌入式操作系统。通俗说，它像“给微控制器用的小型系统底座”。

Zephyr 已经支持很多开发板，但它默认要求用户知道这些概念：

- board target：Zephyr 里代表某块开发板的名字，例如 `xiao_esp32c6/esp32c6/hpcore`。
- Devicetree：Zephyr 描述硬件连接的文件系统，可以理解成“硬件地图”。
- Kconfig：Zephyr 打开或关闭功能的配置系统，可以理解成“一排功能开关”。
- west：Zephyr 的命令行工具，负责下载、构建、烧录和查看日志。
- SDK：编译器工具包，把 C 代码加工成芯片能运行的固件。
- blob：芯片厂商提供的二进制文件，有些芯片构建时需要。

本仓库在这些底层概念之上，加了一层 XIAO/Grove 用户能直接使用的资料：

- `examples/boards/`：每块 XIAO 开发板的最小 demo。
- `metadata/boards/`：开发板 id、名称、vendor 和 Zephyr target。
- `scripts/`：环境安装、CLI 和示例构建脚本。
- `tools/build_matrix/`：批量构建所有开发板 demo 的验证工具。
- `docs/`：给用户看的文档。
- `AI use/`：给 AI 和维护者看的项目纲领和工作记录。

一句话总结：Zephyr 是底层引擎，本仓库给 XIAO 用户提供整理好的示例和可重复命令。

## 2. 第一次安装环境

从项目根目录运行：

```sh
cd ~/seeed-zephyr-base
bash scripts/setup-macos.sh
```

如果你已经知道要用哪块板子，可以带上 `--board`。例如 XIAO ESP32C6：

```sh
cd ~/seeed-zephyr-base
bash scripts/setup-macos.sh --board xiao_esp32c6
```

### 其他平台

非 macOS setup 入口已经写好，但还在等待真实平台验证。不要把它们当成已经验证完成的安装路径。

Linux，尚未在真实 Linux 验证：

```sh
cd ~/seeed-zephyr-base
bash scripts/setup-linux.sh
```

Windows，尚未在真实 Windows 验证，先准备 WSL2：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup-windows.ps1
```

然后在 WSL2 内运行 Linux setup：

```sh
cd ~/seeed-zephyr-base
bash scripts/setup-linux.sh
```

setup 流程会准备 `~/zephyrproject`，创建 Python venv，安装 `west`，下载 Zephyr v4.4.0，
安装 Zephyr Python 包和 SDK，并在需要时获取厂商 blobs。当你通过 `--board` 选择 Espressif
开发板时，setup 还会检查 Zephyr 自带的 `hal_espressif` 烧录和 monitor 工具是否可用。

执行到 CLI 安装步骤时，脚本会询问：

```text
Install seeed-zephyr CLI? [Y/n]
```

直接按回车就是安装。安装后，`seeed-zephyr` 命令可以在任意目录使用。如果安装目录不在
`PATH` 里，setup 会打印需要添加的 `PATH` 命令。

脚本最后会打印下一条本仓库示例命令，例如：

```sh
seeed-zephyr build xiao_esp32c6
```

一句话总结：setup 负责装工具链，也会默认安装后续操作示例用的命令。

## 3. 构建一块板子的 demo

CLI 安装后，从任意目录构建：

```sh
seeed-zephyr build xiao_esp32c6
```

XIAO ESP32C3 没有板载 LED，所以它不用 `blinky`，而是用 `hello_world`：

```sh
seeed-zephyr build xiao_esp32c3
```

`seeed-zephyr build <board_id>` 会读取开发板 metadata，找到仓库示例，然后把验证过的
target 和示例路径交给 Zephyr 的 `west build`。

如果你在 setup 里跳过了 CLI 安装，备用入口是从项目根目录运行
`scripts/seeed-zephyr <command>`。

一句话总结：安装后的命令可以离开仓库目录使用，但真正构建固件的仍然是 Zephyr。

## 4. 常用 CLI 命令

列出开发板和示例：

```sh
seeed-zephyr list boards
seeed-zephyr list examples
```

构建、烧录、查看日志和启动调试：

```sh
seeed-zephyr build xiao_esp32c6
seeed-zephyr flash xiao_esp32c6
seeed-zephyr monitor xiao_esp32c6
seeed-zephyr debug xiao_esp32c6
```

构建、烧录，然后自动打开 monitor：

```sh
seeed-zephyr flash xiao_esp32c6 --monitor
seeed-zephyr flash xiao_samd21 --monitor
seeed-zephyr flash xiao_rp2040 --monitor
```

运行完整构建矩阵：

```sh
seeed-zephyr matrix
```

记录一次真实硬件观察：

```sh
seeed-zephyr verify-hardware xiao_esp32c6
```

一句话总结：CLI 是操作本仓库示例的默认入口。

## 5. 当前开发板 demo 矩阵

这张表由 `tools/build_matrix/run.sh` 生成。

| 开发板 | board target | 仓库示例 | v4.4.0 状态 | 说明 |
| --- | --- | --- | --- | --- |
| XIAO SAMD21 | `seeeduino_xiao` | `examples/boards/xiao_samd21/blinky` | PASS | 硬件已验证 |
| XIAO nRF52840 | `xiao_ble` | `examples/boards/xiao_nrf52840/blinky` | PASS | 可构建 |
| XIAO ESP32C3 | `xiao_esp32c3` | `examples/boards/xiao_esp32c3/hello_world` | PASS | 无板载 LED |
| XIAO ESP32C5 | `xiao_esp32c5` | `examples/boards/xiao_esp32c5/hello_world` | UNSUPPORTED | Zephyr v4.4.0 没有 XIAO target |
| XIAO ESP32C6 | `xiao_esp32c6/esp32c6/hpcore` | `examples/boards/xiao_esp32c6/blinky` | PASS | 可构建 |
| XIAO ESP32S3 | `xiao_esp32s3/esp32s3/procpu` | `examples/boards/xiao_esp32s3/blinky` | PASS | 可构建 |
| XIAO MG24 | `xiao_mg24` | `examples/boards/xiao_mg24/blinky` | PASS | 可构建 |
| XIAO nRF54L15 | `xiao_nrf54l15/nrf54l15/cpuapp` | `examples/boards/xiao_nrf54l15/blinky` | PASS | 可构建 |
| XIAO RA4M1 | `xiao_ra4m1` | `examples/boards/xiao_ra4m1/blinky` | PASS | 可构建 |
| XIAO RP2040 | `xiao_rp2040` | `examples/boards/xiao_rp2040/blinky` | PASS | 硬件已验证；每次烧录需要 UF2 模式 |
| XIAO RP2350 | `xiao_rp2350/rp2350a/hazard3` | `examples/boards/xiao_rp2350/blinky` | PASS | 可构建 |

`UNSUPPORTED` 的意思不是脚本写错了，而是当前固定使用的 Zephyr v4.4.0 里没有这个
XIAO board target。XIAO ESP32C5 已经有仓库 demo 记录，但要等选定 Zephyr 基线提供
真实 `xiao_esp32c5` target 后才能构建。

一句话总结：当前 10 个 target 能构建本仓库 demo，XIAO ESP32C5 已记录但在当前基线下不可构建。

## 6. 烧录到开发板

构建成功后，通过 CLI 烧录：

```sh
seeed-zephyr flash xiao_esp32c6
```

`flash` 每次都会先 build 再 flash。如果要在烧录成功后自动打开 monitor，可以运行：

```sh
seeed-zephyr flash xiao_esp32c6 --monitor
```

ESP32 系列有时需要手动进入 bootloader。通俗说，就是让板子进入“准备接收新程序”的状态。

ESP32 系列查看串口日志可以运行：

```sh
seeed-zephyr monitor xiao_esp32c6
```

非 Espressif 开发板会使用 Zephyr venv 中的 pyserial miniterm 打开串口：

```sh
seeed-zephyr monitor xiao_samd21
```

如果省略 `--port`，CLI 会尝试自动检测一个 USB 串口设备。

关于 XIAO SAMD21 连续烧录和 BOSSA 自动重启行为，见
[XIAO SAMD21 开发板说明](boards/xiao-samd21.md)。

关于 XIAO RP2040 UF2 烧录和 USB CDC monitor 行为，见
[XIAO RP2040 开发板说明](boards/xiao-rp2040.md)。

如果已经连接合适的硬件调试器，可以启动 Zephyr 调试会话：

```sh
seeed-zephyr debug xiao_esp32c6
```

一句话总结：CLI 负责选择本仓库示例，真正的 `west build`、`west flash`、`west debug`、模块工具和 Zephyr venv 串口工具仍由 Zephyr 环境执行。

## 7. 维护者常用命令

校验 metadata：

```sh
cd ~/seeed-zephyr-base
/Users/mengdu/zephyrproject/.venv/bin/python tools/validate_metadata/validate.py
```

重新构建全部开发板 demo：

```sh
seeed-zephyr matrix
```

一句话总结：维护者用 metadata 校验和构建矩阵，让示例目录保持可信。

## 8. 常见错误

### `west: command not found`

运行 setup，或激活 Zephyr venv：

```sh
source ~/zephyrproject/.venv/bin/activate
```

一句话总结：找不到 `west`，通常是还没激活 Zephyr venv。

### `No board named ...`

检查当前 Zephyr 基线里有没有这个 board target：

```sh
cd ~/zephyrproject
source .venv/bin/activate
west boards | grep -i xiao
```

一句话总结：找不到 board 时，先确认名字，再确认当前 Zephyr 版本是否支持。

### `blinky` 找不到 `led0`

没有板载 LED 的板子要用非 LED demo：

```sh
seeed-zephyr build xiao_esp32c3
```

一句话总结：不是每块 XIAO 都适合用 LED blink 做最小验证。

### ESP32 烧录时找不到 `esptool`

重新运行 setup，让 Zephyr venv 和 CLI 环境刷新：

```sh
cd ~/seeed-zephyr-base
bash scripts/setup-macos.sh --board xiao_esp32c6
```

一句话总结：ESP32 烧录和 monitor 使用 Zephyr 的 `hal_espressif` 工具，CLI 会把 Zephyr venv 暴露给这些工具。

### `No matching UF2 partitions found`

把 RP2040 或 RP2350 开发板放进 UF2 模式，然后重新运行烧录命令：

```sh
seeed-zephyr flash xiao_rp2040 --monitor
```

进入方式是：按住 BOOTSEL 再插入 USB，或者按住 BOOTSEL 再按 RESET。运行 `west flash` 的环境必须能看到
UF2 存储卷。

一句话总结：UF2 开发板必须先露出 bootloader 存储盘，Zephyr 才能复制固件。
