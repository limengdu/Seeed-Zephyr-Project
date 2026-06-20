# 入门指南

Zephyr 设置最容易理解为三个部分协同工作:

- 由 `west` 获取和更新的 Zephyr source tree
- 将源代码转换为固件的编译器和 Zephyr SDK
- 驱动获取、构建、烧录和监视流程的 `west` 命令行工具

本指南的目标是为本项目的 XIAO 开发板和 shields 构建固件。一次成功构建是第一份本地证据，证明开发板和 shield 元数据可以指向真实的 Zephyr targets。

## 1. 安装前置依赖

在 macOS Apple Silicon 上，先安装 Homebrew，把它加载到 shell 中，然后安装 Zephyr 需要的软件包。

```sh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
(echo; echo 'eval "$(/opt/homebrew/bin/brew shellenv)"') >> ~/.zprofile
source ~/.zprofile
brew install cmake ninja gperf python3 python-tk ccache qemu dtc libmagic wget openocd
(echo; echo 'export PATH="'$(brew --prefix)'/opt/python/libexec/bin:$PATH"') >> ~/.zprofile
source ~/.zprofile
```

一句话总结: 在获取或构建任何固件前，安装 Zephyr 需要的 macOS 工具。

## 2. 创建 Python 虚拟环境并安装 West

Python 虚拟环境会让 Zephyr 的 Python 包与系统其他部分隔离。每个新终端在运行 Zephyr 命令前，都必须重新激活这个环境。

```sh
python3 -m venv ~/zephyrproject/.venv
source ~/zephyrproject/.venv/bin/activate
pip install west
```

打开新终端后，在构建前重新激活同一个虚拟环境。

一句话总结: 创建隔离的 Python 环境并安装 `west`，然后在每个新终端中重新激活它。

## 3. 获取 Zephyr 源码

本项目的基线是最新稳定 Zephyr 版本，即 4.4。显式固定它，以便构建可复现。

```sh
west init ~/zephyrproject --mr v4.4.0
cd ~/zephyrproject
west update
```

本项目的大多数开发板都在最新稳定版本中可用。少数最新开发板可能只存在于开发分支 `main`。如果在稳定检出版本上运行 `west boards | grep -i xiao` 时没有列出你需要的开发板，那么该开发板正在等待下一个稳定版本。只为了临时验证这类开发板时，可以运行不带 `--mr` 的 `west init ~/zephyrproject` 来改为获取 `main`。

一句话总结: 固定最新稳定版本 `v4.4.0` 以获得可复现构建，只对尚未进入稳定版本的开发板回退到 `main`。

## 4. 导出 CMake，安装 Python 依赖，并安装 SDK

导出 Zephyr 可以让 CMake 找到 Zephyr 包。Python 依赖命令会安装 Zephyr 脚本使用的软件包。SDK 安装会下载并安装用于编译固件的工具链，体积有数 GB。

```sh
west zephyr-export
west packages pip --install
cd ~/zephyrproject/zephyr
west sdk install
```

一句话总结: 把 Zephyr 连接到 CMake，安装 Zephyr 的 Python 包，并安装编译器 SDK。

## 5. 获取开发板专属 Binary Blobs

只有部分 XIAO 芯片系列需要 Zephyr binary blobs。macOS setup script 会读取 `metadata/boards/<board_id>.yaml` 里的 `vendor:` 值，由此推导正确的 HAL module，并在 `west blobs list <module>` 没有输出 blob 条目时跳过获取。

```sh
cd ~/seeed-zephyr-base
bash scripts/setup-macos.sh --board xiao_esp32c6
```

如果手动设置，先把开发板 vendor 映射到 Zephyr HAL module，再检查该 module 是否有 blobs。下面的例子使用 `xiao_esp32c6` 对应的 module；实际使用时请替换成你的开发板 vendor 对应的 module。

```sh
cd ~/zephyrproject
MODULE=hal_espressif
west blobs list "$MODULE"
west blobs fetch "$MODULE"
```

如果 `west blobs list "$MODULE"` 没有打印 blob 条目，就跳过这块开发板的 fetch。

一句话总结: 只在所选 XIAO 开发板的 HAL module 确实报告 blob 条目时，才获取芯片专属 blobs。

## 6. 构建本项目的 XIAO 开发板

首先，列出 Zephyr checkout 已知的权威 XIAO 开发板名称:

```sh
west boards | grep -i xiao
```

然后为有代表性的开发板构建一个小型基线固件。大多数开发板可以使用
`samples/basic/blinky`；没有板载 LED 的开发板应该使用不依赖 `led0` 的样例，
例如 `samples/hello_world`。

```sh
cd ~/zephyrproject/zephyr
west build -p always -b xiao_esp32c6/esp32c6/hpcore samples/basic/blinky
west build -p always -b xiao_rp2040 samples/basic/blinky
west build -p always -b xiao_ble samples/basic/blinky
west build -p always -b xiao_esp32c3 samples/hello_world
```

有些开发板是多变体或多核的。使用裸名称，例如 `xiao_esp32c6`，会报错并打印有效的全限定名称，例如 `xiao_esp32c6/esp32c6/hpcore`。请使用 Zephyr 打印出的完整名称。

下表记录了 2026-06-20 基于 Zephyr v4.4.0 的基线构建矩阵。PASS 表示所选基线样例在当前环境中编译通过。UNSUPPORTED 表示当前 stable checkout 没有提供这块 XIAO 开发板的专属 target。

权威开发板 targets:

| 开发板显示名称 | Zephyr 构建 target | 基线样例 | v4.4.0 结果 | 备注 |
| --- | --- | --- | --- | --- |
| XIAO SAMD21 | `seeeduino_xiao` | `samples/basic/blinky` | PASS | 构建成功。 |
| XIAO nRF52840 | `xiao_ble` | `samples/basic/blinky` | PASS | 构建成功。 |
| XIAO ESP32C3 | `xiao_esp32c3` | `samples/hello_world` | PASS | XIAO ESP32C3 没有板载 LED，所以 `blinky` 不能作为这块板子的有效基线样例。 |
| XIAO ESP32C5 | `xiao_esp32c5` | `samples/basic/blinky` | UNSUPPORTED | Zephyr v4.4.0 没有提供这个 XIAO target。Zephyr `main` 有 `esp32c5_devkitc`，但它不是 XIAO ESP32C5 这个板级 target。 |
| XIAO ESP32C6 | `xiao_esp32c6/esp32c6/hpcore` | `samples/basic/blinky` | PASS | 构建成功。 |
| XIAO ESP32S3 | `xiao_esp32s3/esp32s3/procpu` | `samples/basic/blinky` | PASS | 构建成功。 |
| XIAO MG24 | `xiao_mg24` | `samples/basic/blinky` | PASS | 构建成功。 |
| XIAO nRF54L15 | `xiao_nrf54l15/nrf54l15/cpuapp` | `samples/basic/blinky` | PASS | 构建成功。 |
| XIAO RA4M1 | `xiao_ra4m1` | `samples/basic/blinky` | PASS | 构建成功。 |
| XIAO RP2040 | `xiao_rp2040` | `samples/basic/blinky` | PASS | 构建成功。 |
| XIAO RP2350 | `xiao_rp2350/rp2350a/hazard3` | `samples/basic/blinky` | PASS | 构建成功。 |

一句话总结: 用准确的 Zephyr target 名称构建一个小型上游 sample，来验证每块 XIAO 开发板。

## 7. 构建本项目的扩展板

Zephyr 使用 shields 描述附加板。通过传入带上游 shield 名称的 `--shield` 来构建 shield samples:

```sh
west build -p always -b xiao_esp32c6/esp32c6/hpcore --shield seeed_xiao_expansion_board samples/drivers/display
west build -p always -b xiao_esp32s3/esp32s3/procpu --shield seeed_xiao_round_display samples/subsys/display/lvgl
```

XIAO 的 Grove Shield，SKU 103020312，没有上游 Zephyr shield。它是一个被动转接板，因此 Grove 模块连接到 XIAO 自身的 I2C 引脚，不使用 `--shield` 标志。

一句话总结: 只对拥有上游 shield 定义的扩展板使用 Zephyr shield 名称。

## 8. 烧录和监视

成功构建后，烧录生成的固件:

```sh
west flash
```

ESP32 开发板可能需要手动进入 bootloader，例如双击 RESET。ESP32 开发板可以用 `west espressif monitor` 进行监视。

一句话总结: 使用 `west flash` 给开发板写入程序，并在验证 ESP32 开发板时使用 Espressif monitor 命令。

## 9. 验证并报告证据

这次验证的目的是为 build status 和 validated Zephyr version 等 derived metadata fields 收集真实证据。这些字段应基于观察结果，而不是假设。

记录以下结果:

- 哪些开发板需要 fully-qualified target
- 哪些开发板构建成功
- 哪些开发板失败，包括错误输出的第一段和最后一段有用行
- AS5600 Kconfig symbol 是否确实为 `CONFIG_AS5600`
- 两个 shield samples 是否构建成功

推荐证据格式:

```text
Zephyr checkout: main or pinned version
Host: macOS Apple Silicon
Board target: xiao_esp32c6
Sample: samples/basic/blinky or samples/hello_world
Result: passed, failed, or unsupported
Error head: first useful error lines
Error tail: last useful error lines
Notes: manual bootloader, fully-qualified target, or shield behavior
```

一句话总结: 报告填充 metadata status fields 所需的准确构建证据，以保持其真实。
