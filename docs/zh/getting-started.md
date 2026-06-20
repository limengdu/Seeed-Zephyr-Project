# 入门指南：你现在在做什么

先说结论：这个仓库不是 Zephyr 本体。这个仓库是在给 Seeed XIAO、Grove 模块和扩展板做一层“使用 Zephyr 的说明书、资料库和验证工具”。

把它想成两层：

| 位置 | 它是什么 | 平时做什么 |
| --- | --- | --- |
| `~/seeed-zephyr-base` | 本项目 | 放 XIAO/Grove metadata、脚本、文档、验证结果 |
| `~/zephyrproject` | 上游 Zephyr 工作区 | 放 Zephyr 源码、SDK、west workspace，并实际编译固件 |

Zephyr 是一个嵌入式操作系统。通俗说，它像“给微控制器用的小型系统底座”。本项目不是改这个底座，而是帮 XIAO 用户知道该怎么把这个底座用起来。

一句话总结：`seeed-zephyr-base` 是说明书和验证层，`~/zephyrproject` 才是实际编译 Zephyr 固件的地方。

## 1. 这个项目要解决什么问题

Zephyr 已经支持很多开发板，但它默认要求用户知道这些概念：

- board target：Zephyr 里用来代表某块开发板的名字，例如 `xiao_esp32c6/esp32c6/hpcore`。
- sample：Zephyr 自带的小示例程序，例如 `samples/basic/blinky`。
- SDK：编译器工具包，把 C 代码变成芯片能运行的固件。
- west：Zephyr 的命令行工具，负责下载源码、构建、烧录和查看串口。
- blob：芯片厂商提供的二进制文件，有些 ESP32 系列构建时需要。
- shield：Zephyr 对扩展板的叫法，例如 XIAO Expansion Board。

这些词刚开始会很绕。你可以先把它们理解成：

- board target 是“地址”。
- sample 是“试运行的小程序”。
- SDK 是“加工机器”。
- west 是“总控遥控器”。
- blob 是“厂商给的零件”。
- shield 是“插在主板上的扩展板说明”。

本项目的目标是把这些信息整理成机器可读的 metadata 和人能看懂的文档，再用脚本定期验证它们是不是真的能构建。

一句话总结：这个项目是在把 Zephyr 的复杂信息整理成 XIAO 用户能直接使用的资料和工具。

## 2. 你通常有两种身份

第一种身份是“我要用一块板子跑起来”。这时你只关心：

1. 安装 Zephyr 环境。
2. 找到正确的 board target。
3. build 一个 sample。
4. flash 到开发板。

第二种身份是“我要维护这个仓库”。这时你还要关心：

1. `metadata/` 里的 YAML 是否写对。
2. 每块 XIAO 板子是否能真实构建。
3. 文档是否和真实验证结果一致。
4. 哪些板子是通过、失败、还是当前稳定版暂不支持。

一句话总结：普通使用者只需要跑单块板子，维护者才需要跑完整矩阵和更新验证记录。

## 3. 第一次安装环境

如果你只是想把本机准备好，进入本项目目录运行：

```sh
cd ~/seeed-zephyr-base
bash scripts/setup-macos.sh
```

如果你已经知道要用哪块板子，推荐带上 `--board`。例如 XIAO ESP32C6：

```sh
cd ~/seeed-zephyr-base
bash scripts/setup-macos.sh --board xiao_esp32c6
```

这个脚本会做这些事：

| 步骤 | 做什么 | 写到哪里 |
| --- | --- | --- |
| 1 | 安装 Zephyr 需要的 Homebrew 工具 | 系统 Homebrew |
| 2 | 创建 Python venv 并安装 `west` | `~/zephyrproject/.venv` |
| 3 | 下载 Zephyr v4.4.0 源码 | `~/zephyrproject/zephyr` |
| 4 | 安装 Zephyr Python 包和 SDK | `~/zephyrproject` 和 `~/zephyr-sdk-*` |
| 5 | 如果指定了板子，按 vendor 拉取 blobs | `~/zephyrproject` |

脚本最后会打印下一条建议 build 命令。对于 XIAO ESP32C3，它会推荐 `samples/hello_world`，因为这块板子没有板载 LED，不能用 `blinky` 当基线样例。

一句话总结：`setup-macos.sh` 是“装环境脚本”，应该在 `~/seeed-zephyr-base` 里运行，但它会准备 `~/zephyrproject`。

## 4. 构建一块 XIAO 板子

安装完成后，真正构建固件要进入 Zephyr 源码目录：

```sh
cd ~/zephyrproject/zephyr
source ~/zephyrproject/.venv/bin/activate
```

然后运行：

```sh
west build -p always -b <board_target> <sample_path>
```

例如 XIAO ESP32C6：

```sh
west build -p always -b xiao_esp32c6/esp32c6/hpcore samples/basic/blinky
```

例如 XIAO ESP32C3：

```sh
west build -p always -b xiao_esp32c3 samples/hello_world
```

为什么 C3 不用 `blinky`？因为 `blinky` 需要一个叫 `led0` 的板载 LED。XIAO ESP32C3 没有板载 LED，所以它用 `hello_world` 这种不依赖 LED 的小程序来证明“这个板子和工具链可以编译”。

一句话总结：构建命令在 `~/zephyrproject/zephyr` 里跑，C3 用 `hello_world`，有 LED 的板子通常用 `blinky`。

## 5. 当前已验证的板子命令

这张表来自 `tools/build_matrix/results.md`。它不是猜出来的，是实际跑过构建矩阵得到的结果。

| 开发板 | board target | baseline sample | v4.4.0 状态 | 说明 |
| --- | --- | --- | --- | --- |
| XIAO SAMD21 | `seeeduino_xiao` | `samples/basic/blinky` | PASS | 可构建 |
| XIAO nRF52840 | `xiao_ble` | `samples/basic/blinky` | PASS | 可构建 |
| XIAO ESP32C3 | `xiao_esp32c3` | `samples/hello_world` | PASS | 没有板载 LED，不用 `blinky` |
| XIAO ESP32C5 | `xiao_esp32c5` | `samples/basic/blinky` | UNSUPPORTED | Zephyr v4.4.0 没有这个 XIAO target |
| XIAO ESP32C6 | `xiao_esp32c6/esp32c6/hpcore` | `samples/basic/blinky` | PASS | 可构建 |
| XIAO ESP32S3 | `xiao_esp32s3/esp32s3/procpu` | `samples/basic/blinky` | PASS | 可构建 |
| XIAO MG24 | `xiao_mg24` | `samples/basic/blinky` | PASS | 可构建 |
| XIAO nRF54L15 | `xiao_nrf54l15/nrf54l15/cpuapp` | `samples/basic/blinky` | PASS | 可构建 |
| XIAO RA4M1 | `xiao_ra4m1` | `samples/basic/blinky` | PASS | 可构建 |
| XIAO RP2040 | `xiao_rp2040` | `samples/basic/blinky` | PASS | 可构建 |
| XIAO RP2350 | `xiao_rp2350/rp2350a/hazard3` | `samples/basic/blinky` | PASS | 可构建 |

`UNSUPPORTED` 不是“代码写错了”。它的意思是：当前固定使用的 Zephyr v4.4.0 里，还没有这个 XIAO board target。上游 Zephyr `main` 里有 `esp32c5_devkitc`，但那是 ESP32-C5 DevKitC，不是 XIAO ESP32C5。

一句话总结：现在是 10 个可验证 target 通过，XIAO ESP32C5 在 v4.4.0 下暂时没有可验证 target。

## 6. 烧录到开发板

构建成功后，继续在 `~/zephyrproject/zephyr` 里运行：

```sh
west flash
```

ESP32 系列有时需要手动进入 bootloader。通俗说，就是让板子进入“准备接收新程序”的状态。常见做法是双击 RESET，或者按住 BOOT 再点 RESET，具体取决于板子。

ESP32 系列查看串口日志可以运行：

```sh
west espressif monitor
```

一句话总结：`west build` 负责生成固件，`west flash` 负责把固件写进板子。

## 7. 这个仓库里的脚本分别干什么

| 脚本 | 在哪里运行 | 给谁用 | 做什么 | 输出看哪里 |
| --- | --- | --- | --- | --- |
| `scripts/setup-macos.sh` | `~/seeed-zephyr-base` | 第一次装环境的人 | 安装工具、下载 Zephyr、安装 SDK、拉 blobs | 终端最后的 next step |
| `tools/validate_metadata/validate.py` | `~/seeed-zephyr-base` | 维护者 | 检查 `metadata/` 的 YAML 格式和必填字段 | 终端里的 PASS/FAIL |
| `tools/build_matrix/run.sh` | `~/seeed-zephyr-base` | 维护者 | 批量构建所有板子的 baseline sample | `tools/build_matrix/results.md` |

常用命令：

```sh
cd ~/seeed-zephyr-base
/Users/mengdu/zephyrproject/.venv/bin/python tools/validate_metadata/validate.py
```

```sh
cd ~/seeed-zephyr-base
BUILD_MATRIX_GENERATED_ON=2026-06-20 bash tools/build_matrix/run.sh
```

一句话总结：普通用户主要用 setup 脚本；维护者才需要跑 metadata 校验和 build matrix。

## 8. 重要文件地图

| 路径 | 作用 |
| --- | --- |
| `metadata/boards/*.yaml` | 每块 XIAO 板子的资料，例如 vendor、Zephyr target、芯片名 |
| `metadata/grove_modules/*.yaml` | Grove 模块资料 |
| `metadata/expansion_boards/*.yaml` | 扩展板资料 |
| `tools/build_matrix/board-overrides.tsv` | 少数板子的特殊构建规则，例如 C3 用 `hello_world` |
| `tools/build_matrix/results.md` | 最近一次完整构建矩阵结果 |
| `AI use/en/validation-log.md` | 详细验证日志，记录为什么某个状态可信 |
| `docs/zh/getting-started.md` | 中文入门说明 |
| `docs/en/getting-started.md` | 英文入门说明 |

一句话总结：`metadata` 是资料库，`tools` 是验证工具，`docs` 是给人看的说明。

## 9. 常见错误怎么判断

### `west: command not found`

通常是没有激活 Python venv。运行：

```sh
source ~/zephyrproject/.venv/bin/activate
```

一句话总结：看不到 `west`，先激活 venv。

### `no west workspace found`

通常是在错误目录运行了 Zephyr 命令，或者还没有初始化 `~/zephyrproject`。先确认：

```sh
ls ~/zephyrproject/.west
```

如果没有这个目录，回到本项目运行 setup 脚本。

一句话总结：Zephyr 命令需要在 west workspace 里面跑。

### `No board named ...`

这通常有两种可能：

1. board target 拼错了。
2. 当前 Zephyr 版本还没有这块板子的 target。

先查：

```sh
cd ~/zephyrproject/zephyr
west boards | grep -i xiao
```

一句话总结：找不到 board 时，先确认名字，再确认当前 Zephyr 版本是否支持。

### `blinky` 找不到 `led0`

这说明这个 sample 需要板载 LED，但当前板子没有可用的 `led0`。XIAO ESP32C3 就是这种情况。改用：

```sh
west build -p always -b xiao_esp32c3 samples/hello_world
```

一句话总结：不是所有板子都适合用 blink 验证。

### ESP32 构建缺 blob

ESP32 系列可能需要厂商 blobs。回到本项目运行：

```sh
cd ~/seeed-zephyr-base
bash scripts/setup-macos.sh --board xiao_esp32c6
```

一句话总结：ESP32 缺厂商零件时，让 setup 脚本按板子补齐。

## 10. 下一步应该做什么

如果你现在的目标是“先跑通一块板子”，建议从 XIAO ESP32C6 开始：

```sh
cd ~/seeed-zephyr-base
bash scripts/setup-macos.sh --board xiao_esp32c6
cd ~/zephyrproject/zephyr
source ~/zephyrproject/.venv/bin/activate
west build -p always -b xiao_esp32c6/esp32c6/hpcore samples/basic/blinky
west flash
```

如果你的目标是“维护这个项目”，建议每次改 metadata 后跑：

```sh
cd ~/seeed-zephyr-base
/Users/mengdu/zephyrproject/.venv/bin/python tools/validate_metadata/validate.py
BUILD_MATRIX_GENERATED_ON=2026-06-20 bash tools/build_matrix/run.sh
```

一句话总结：先单板跑通，再用矩阵验证整个资料库。
