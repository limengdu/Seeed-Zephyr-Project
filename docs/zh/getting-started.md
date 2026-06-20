# 入门指南：先构建本仓库里的示例

先说结论：这个仓库现在已经有自己的 XIAO 开发板 demo，放在 `examples/boards/`。
用户应该先构建这些本仓库示例，而不是手动去 Zephyr 源码目录里找 sample。

把它想成两层：

| 位置 | 它是什么 | 平时做什么 |
| --- | --- | --- |
| `~/seeed-zephyr-base` | 本项目 | 放 XIAO/Grove 示例、metadata、脚本、文档、验证结果 |
| `~/zephyrproject` | 上游 Zephyr 工作区 | 放 Zephyr 源码、SDK、west workspace 和固件构建输出 |

一句话总结：平时从 `~/seeed-zephyr-base` 运行本项目脚本；脚本会调用 `~/zephyrproject` 里的 Zephyr。

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
- `scripts/`：环境安装和单个示例构建脚本。
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

这个脚本会准备 `~/zephyrproject`，创建 Python venv，安装 `west`，下载 Zephyr v4.4.0，
安装 Zephyr Python 包和 SDK，并在需要时获取厂商 blobs。

脚本最后会打印下一条本仓库示例命令，例如：

```sh
cd ~/seeed-zephyr-base
bash scripts/build-example.sh examples/boards/xiao_esp32c6/blinky
```

一句话总结：setup 负责装工具链，装完后把你带回本仓库示例。

## 3. 构建一块板子的 demo

从项目根目录构建：

```sh
cd ~/seeed-zephyr-base
bash scripts/build-example.sh examples/boards/xiao_esp32c6/blinky
```

XIAO ESP32C3 没有板载 LED，所以它不用 `blinky`，而是用 `hello_world`：

```sh
cd ~/seeed-zephyr-base
bash scripts/build-example.sh examples/boards/xiao_esp32c3/hello_world
```

`build-example.sh` 会读取 `example.yaml`，找到 Zephyr target，激活
`~/zephyrproject/.venv`，按需获取 blobs，然后调用 `west build` 构建这个仓库里的示例。

一句话总结：构建命令从本仓库开始，Zephyr 的复杂参数由脚本处理。

## 4. 当前开发板 demo 矩阵

这张表由 `tools/build_matrix/run.sh` 生成。

| 开发板 | board target | 仓库示例 | v4.4.0 状态 | 说明 |
| --- | --- | --- | --- | --- |
| XIAO SAMD21 | `seeeduino_xiao` | `examples/boards/xiao_samd21/blinky` | PASS | 可构建 |
| XIAO nRF52840 | `xiao_ble` | `examples/boards/xiao_nrf52840/blinky` | PASS | 可构建 |
| XIAO ESP32C3 | `xiao_esp32c3` | `examples/boards/xiao_esp32c3/hello_world` | PASS | 无板载 LED |
| XIAO ESP32C5 | `xiao_esp32c5` | `examples/boards/xiao_esp32c5/hello_world` | UNSUPPORTED | Zephyr v4.4.0 没有 XIAO target |
| XIAO ESP32C6 | `xiao_esp32c6/esp32c6/hpcore` | `examples/boards/xiao_esp32c6/blinky` | PASS | 可构建 |
| XIAO ESP32S3 | `xiao_esp32s3/esp32s3/procpu` | `examples/boards/xiao_esp32s3/blinky` | PASS | 可构建 |
| XIAO MG24 | `xiao_mg24` | `examples/boards/xiao_mg24/blinky` | PASS | 可构建 |
| XIAO nRF54L15 | `xiao_nrf54l15/nrf54l15/cpuapp` | `examples/boards/xiao_nrf54l15/blinky` | PASS | 可构建 |
| XIAO RA4M1 | `xiao_ra4m1` | `examples/boards/xiao_ra4m1/blinky` | PASS | 可构建 |
| XIAO RP2040 | `xiao_rp2040` | `examples/boards/xiao_rp2040/blinky` | PASS | 可构建 |
| XIAO RP2350 | `xiao_rp2350/rp2350a/hazard3` | `examples/boards/xiao_rp2350/blinky` | PASS | 可构建 |

`UNSUPPORTED` 的意思不是脚本写错了，而是当前固定使用的 Zephyr v4.4.0 里没有这个
XIAO board target。XIAO ESP32C5 已经有仓库 demo 记录，但要等选定 Zephyr 基线提供
真实 `xiao_esp32c5` target 后才能构建。

一句话总结：当前 10 个 target 能构建本仓库 demo，XIAO ESP32C5 已记录但在当前基线下不可构建。

## 5. 烧录到开发板

构建成功后，用 Zephyr 标准命令烧录：

```sh
cd ~/zephyrproject
source .venv/bin/activate
west flash
```

ESP32 系列有时需要手动进入 bootloader。通俗说，就是让板子进入“准备接收新程序”的状态。

ESP32 系列查看串口日志可以运行：

```sh
west espressif monitor
```

一句话总结：构建从本仓库开始，烧录仍使用 Zephyr 官方 `west flash`。

## 6. 维护者常用命令

校验 metadata：

```sh
cd ~/seeed-zephyr-base
/Users/mengdu/zephyrproject/.venv/bin/python tools/validate_metadata/validate.py
```

重新构建全部开发板 demo：

```sh
cd ~/seeed-zephyr-base
BUILD_MATRIX_GENERATED_ON=2026-06-20 bash tools/build_matrix/run.sh
```

一句话总结：维护者用 metadata 校验和构建矩阵，让示例目录保持可信。

## 7. 常见错误

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
bash scripts/build-example.sh examples/boards/xiao_esp32c3/hello_world
```

一句话总结：不是每块 XIAO 都适合用 LED blink 做最小验证。
