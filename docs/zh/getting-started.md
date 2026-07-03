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

## 2. 安装 CLI

四种安装方式，选适合你的。

### 方式 A：pip（全平台通用）

```sh
pip install seeed-zephyr
```

或者用 [pipx](https://pipx.pypa.io/) 隔离安装：

```sh
pipx install seeed-zephyr
```

通过 pip 安装 CLI 后，还需要 Zephyr 工具链。见下方
[第 2b 节](#2b-zephyr-环境安装)。

### 方式 B：一键安装（macOS / Linux）

同时安装 CLI **和** Zephyr 环境，一步到位：

```sh
curl -fsSL https://raw.githubusercontent.com/limengdu/Seeed-Zephyr-Project/main/install.sh | bash
```

完成后直接跳到[第 3 节](#3-构建一块板子的-demo)。

### 方式 C：Homebrew（macOS / Linux）

```sh
brew tap limengdu/seeed
brew install limengdu/seeed/seeed-zephyr
```

通过 Homebrew 安装 CLI 后，还需要 Zephyr 工具链。见下方
[第 2b 节](#2b-zephyr-环境安装)。

### 方式 D：从源码安装（贡献者流程）

克隆仓库后运行对应系统的 setup 脚本。

```sh
cd ~/seeed-zephyr-base
bash scripts/setup-macos.sh
```

如果你已经知道要用哪块板子，可以带上 `--board`：

```sh
cd ~/seeed-zephyr-base
bash scripts/setup-macos.sh --board xiao_esp32c6
```

#### 其他平台

Linux：

```sh
cd ~/seeed-zephyr-base
bash scripts/setup-linux.sh
```

Windows（WSL2）：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup-windows.ps1
```

然后在 WSL2 内运行 Linux setup：

```sh
cd ~/seeed-zephyr-base
bash scripts/setup-linux.sh
```

执行到 CLI 安装步骤时，脚本会询问：

```text
Install seeed-zephyr CLI? [Y/n]
```

直接按回车就是安装。从源码安装时 setup 脚本也会一并准备 Zephyr 环境，
可以跳过第 2b 节。

## 2b. Zephyr 环境安装

如果你通过 pip 或 Homebrew（方式 A 或 C）安装了 CLI，还需要 Zephyr 工具链。
一键安装（方式 B）和从源码安装（方式 D）会自动处理这一步。

`~/zephyrproject` 下的 Zephyr 工作区包含 Python venv、`west`、Zephyr v4.4.0、
Zephyr 包、SDK 和板级 blobs。克隆仓库并运行对应系统的 setup 脚本来安装：

```sh
git clone https://github.com/limengdu/Seeed-Zephyr-Project.git ~/.seeed-zephyr-base

# macOS
bash ~/.seeed-zephyr-base/scripts/setup-macos.sh

# Linux
bash ~/.seeed-zephyr-base/scripts/setup-linux.sh
```

setup 流程会准备 Zephyr 工作区，创建 Python venv，安装 `west`，下载 Zephyr v4.4.0，
安装 Zephyr Python 包和 SDK，并在需要时获取厂商 blobs。通过 `--board` 选择 Espressif
开发板时，setup 还会检查 Zephyr 自带的 `hal_espressif` 烧录和 monitor 工具是否可用。
其他开发板也会处理对应的烧录工具，例如 SAMD21 的 `bossac`、MG24 的 PyOCD CMSIS pack、
RA4M1 的 `dfu-util`。

一句话总结：先装 CLI，再装 Zephyr 工具链（如果安装方式没有自动处理的话）。

## 3. 构建一块板子的 demo

CLI 安装后，从任意目录构建：

```sh
seeed-zephyr build xiao_esp32c6
```

XIAO ESP32-C3 没有板载 LED，所以它不用 `blinky`，而是用 `hello_world`：

```sh
seeed-zephyr build xiao_esp32c3
```

`seeed-zephyr build <board_id>` 会读取开发板 metadata，找到仓库示例，然后把验证过的
target 和示例路径交给 Zephyr 的 `west build`。

如果你从源码安装时跳过了 CLI 安装，备用入口是从项目根目录运行
`scripts/seeed-zephyr <command>`。

一句话总结：安装后的命令可以离开仓库目录使用，但真正构建固件的仍然是 Zephyr。

### 在任意板上构建 Grove 示例

Grove 模块示例位于 `examples/grove/`，板级无关：一份源码通过上游 `seeed_xiao_connector`
抽象在所有 XIAO 板上构建。先写板子，再写 `grove/<模块>/<demo>` 引用：

```sh
seeed-zephyr build xiao_esp32c6  grove/grove_scd41_co2_temperature_humidity_sensor/basic_read
seeed-zephyr build xiao_nrf52840 grove/grove_scd41_co2_temperature_humidity_sensor/basic_read
```

同一份源码在两块板上都能构建，无需修改。查看供编辑器工具使用的每脚状态：

```sh
seeed-zephyr show pins xiao_esp32c6 grove/grove_scd41_co2_temperature_humidity_sensor/basic_read
```

### 在编辑器里创建项目

在 Seeed XIAO Zephyr Assistant 里，**Create Project** 会先问你从什么创建：

- **Grove 模块示例** —— 选一个模块（如 Grove Ultrasonic）、一个 demo,再选一块板。
- **板级示例** —— 选一块板,再选它的某个 demo。
- **空白项目** —— 选一块板,生成一个最小 Zephyr 应用。

也可以从 **Catalog** 开始:展开某个 Grove 模块看到它的示例,用行内的 **Create Project** 按钮,和板子展开示例的方式一样。命令行上,`seeed-zephyr create --blank --board <板子> --output <目录>` 会生成同样的空白项目。

### 在编辑器里配置 Grove GPIO 引脚

Grove Ultrasonic 这类可选引脚示例，可以在 Seeed XIAO Zephyr Assistant 里用图形界面配置。通过插件创建项目时，引脚配置器会在项目写入前打开。已有的生成项目打开为工作区后，在 **Projects** 里选择 **Configure Pins**。

保存后，插件会把角色到引脚的映射写进 `boards/<target>.overlay`，并更新 `snapshot.json`。I2C 传感器这类固定总线模块会高亮显示接线位置，作为只读参考。

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

更新 CLI、示例和 metadata：

```sh
seeed-zephyr update
seeed-zephyr update --version 0.3.0
seeed-zephyr info
```

旧版安装先按原安装渠道引导升级一次：

```sh
brew update && brew upgrade seeed-zephyr
python3 -m pip install --upgrade seeed-zephyr
pipx upgrade seeed-zephyr
curl -fsSL https://raw.githubusercontent.com/limengdu/Seeed-Zephyr-Project/main/install.sh | bash
```

一句话总结：CLI 是操作本仓库示例的默认入口。

## 5. 当前开发板 demo 矩阵

这张表由 `tools/build_matrix/run.sh` 生成。

| 开发板 | board target | 仓库示例 | v4.4.0 状态 | 说明 |
| --- | --- | --- | --- | --- |
| XIAO SAMD21 | `seeeduino_xiao` | `examples/boards/xiao_samd21/blinky` | PASS | 硬件已验证 |
| XIAO nRF52840 | `xiao_ble` | `examples/boards/xiao_nrf52840/blinky` | PASS | 硬件已验证；重复烧录会自动请求 UF2 |
| XIAO ESP32-C3 | `xiao_esp32c3` | `examples/boards/xiao_esp32c3/hello_world` | PASS | 硬件已验证；无板载 LED |
| XIAO ESP32-C5 | `xiao_esp32c5` | `examples/boards/xiao_esp32c5/hello_world` | UNSUPPORTED | Zephyr v4.4.0 没有 XIAO target |
| XIAO ESP32-C6 | `xiao_esp32c6/esp32c6/hpcore` | `examples/boards/xiao_esp32c6/blinky` | PASS | 硬件已验证 |
| XIAO ESP32-S3 | `xiao_esp32s3/esp32s3/procpu` | `examples/boards/xiao_esp32s3/blinky` | PASS | 硬件已验证 |
| XIAO MG24 | `xiao_mg24` | `examples/boards/xiao_mg24/blinky` | PASS | 硬件已验证；默认使用 Zephyr PyOCD runner |
| XIAO nRF54L15 | `xiao_nrf54l15/nrf54l15/cpuapp` | `examples/boards/xiao_nrf54l15/blinky` | PASS | 硬件已验证 |
| XIAO RA4M1 | `xiao_ra4m1` | `examples/boards/xiao_ra4m1/blinky` | PASS | 硬件已验证；使用 USB DFU bootloader |
| XIAO RP2040 | `xiao_rp2040` | `examples/boards/xiao_rp2040/blinky` | PASS | 硬件已验证；重复烧录会自动请求 UF2 |
| XIAO RP2350 | `xiao_rp2350/rp2350a/m33` | `examples/boards/xiao_rp2350/blinky` | PASS | 硬件已验证；M33 target |

`UNSUPPORTED` 的意思不是脚本写错了，而是当前固定使用的 Zephyr v4.4.0 里没有这个
XIAO board target。XIAO ESP32-C5 已经有仓库 demo 记录，但要等选定 Zephyr 基线提供
真实 `xiao_esp32c5` target 后才能构建。

一句话总结：当前 10 个 target 能构建本仓库 demo，XIAO ESP32-C5 已记录但在当前基线下不可构建。

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

非 Espressif 开发板会使用 Zephyr venv 中的可重连串口监视器打开串口：

```sh
seeed-zephyr monitor xiao_samd21
```

设备从 USB 掉线时（例如复位或重新插拔），监视器不会退出，而是保持等待并自动重连。按 `Ctrl+]` 退出。

如果省略 `--port`，CLI 会尝试自动检测一个 USB 串口设备。

关于 XIAO SAMD21 连续烧录和 BOSSA 自动重启行为，见
[XIAO SAMD21 开发板说明](boards/xiao-samd21.md)。

关于 XIAO RP2040 UF2 烧录和 USB CDC monitor 行为，见
[XIAO RP2040 开发板说明](boards/xiao-rp2040.md)。

关于 XIAO nRF52840 UF2 烧录和 1200 baud 自动进 bootloader 行为，见
[XIAO nRF52840 开发板说明](boards/xiao-nrf52840.md)。

关于 XIAO MG24 PyOCD 烧录和 CMSIS pack 要求，见
[XIAO MG24 开发板说明](boards/xiao-mg24.md)。

关于 XIAO RA4M1 USB DFU 烧录和应用起始地址，见
[XIAO RA4M1 开发板说明](boards/xiao-ra4m1.md)。

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

### UF2 开发板找不到存储盘

对 RP2040、RP2350 或 nRF52840 开发板，先确认 UF2 存储卷已经可见，然后重新运行烧录命令：

```sh
seeed-zephyr flash xiao_nrf52840 --monitor
```

如果 XIAO RP2040、XIAO RP2350 或 XIAO nRF52840 已经运行支持自动进入 UF2 的本仓库示例，
CLI 通常会通过 USB CDC 1200 baud 自动请求进入 UF2 模式。

如果当前程序不支持这个请求，或者看不到 USB CDC 串口：

- XIAO RP2040 / XIAO RP2350：按住 BOOTSEL 再插入 USB，或者按住 BOOTSEL 再按 RESET。
- XIAO nRF52840：快速双击 `RESET`，等待 UF2 存储盘出现。

本仓库 CLI 会使用 Zephyr 的 `uf2` runner，不需要为普通 nRF52840 UF2 烧录安装 `nrfutil`。

一句话总结：UF2 开发板仍然是复制固件到 bootloader 存储盘；运行本仓库示例后，CLI 会优先用 1200 baud 自动请求进入这个模式。
