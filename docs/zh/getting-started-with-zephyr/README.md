---
description: 面向 Zephyr 零基础学习者，通过为 Seeed Studio XIAO SAMD21 创建 DAC 示例，逐步理解 Zephyr 项目结构、配置系统、设备树和驱动 API。
title: Zephyr 入门：创建 XIAO SAMD21 DAC 示例
keywords:
  - Zephyr
  - XIAO SAMD21
  - DAC
  - Kconfig
  - Devicetree
image: https://files.seeedstudio.com/wiki/seeed_logo/logo_2023.png
slug: /getting-started-with-zephyr-xiao-samd21-dac
last_update:
  date: 07/10/2026
  author: Citric
---

# Zephyr 入门：创建 XIAO SAMD21 DAC 示例

这是一份边学习、边更新的 Zephyr 入门课程。课程目标不是提供一份只需复制的最终代码，而是通过亲手创建 `examples/boards/xiao_samd21/dac`，理解每条命令、每个项目文件以及每行关键配置的作用。

当前课程已经完成：创建示例骨架、理解并修改 `CMakeLists.txt`、编写 `example.yaml`，以及在仓库检查工具中登记 `dac` 示例类型。

一句话总结：我们通过完成一个真实的 DAC 示例，逐步学习 Zephyr 的项目组织和运行方式。

## 1. 从 Arduino 概念过渡到 Zephyr

Arduino 把很多硬件配置隐藏在简单函数后面。Zephyr 将程序拆成多个职责明确的部分：C 代码描述程序行为，Kconfig 选择软件功能，Devicetree 描述硬件连接，CMake 决定编译哪些源文件。

<div class="table-center">
	<table align="center">
		<tr>
			<th>Arduino</th>
			<th>Zephyr 中对应的方式</th>
		</tr>
		<tr>
			<td><code>analogWriteResolution(10)</code></td>
			<td>配置 DAC 通道分辨率为 10 位</td>
		</tr>
		<tr>
			<td><code>analogWrite(A0, value)</code></td>
			<td>调用 <code>dac_write_value()</code></td>
		</tr>
		<tr>
			<td><code>analogReadResolution(12)</code></td>
			<td>在 ADC 通道设备树配置中声明 12 位分辨率</td>
		</tr>
		<tr>
			<td><code>analogRead(A1)</code></td>
			<td>调用 <code>adc_read_dt()</code></td>
		</tr>
		<tr>
			<td><code>Serial.println()</code></td>
			<td>通过 USB CDC 控制台调用 <code>printk()</code></td>
		</tr>
		<tr>
			<td><code>delay(1)</code></td>
			<td>调用 <code>k_msleep(1)</code></td>
		</tr>
		<tr>
			<td><code>sin(x)</code></td>
			<td>使用 C 数学库的 <code>sinf()</code></td>
		</tr>
	</table>
</div>

原 Arduino 示例虽然声明了 `frequency = 440`，但没有在计算中使用它。按照 `x += 0.02` 和每次约 1 ms 的延时，一个周期大约需要 314 个采样点，实际频率约为 `1 / 0.314 = 3.18 Hz`。

真正按照目标频率产生正弦波时，我们将使用：

```text
phase_increment = 2 * pi * frequency / sample_rate
```

一句话总结：Zephyr 需要显式描述软件功能和硬件资源，正弦波频率也需要根据采样率计算。

## 2. 创建 DAC 示例骨架

### 2.1 进入仓库根目录

```bash
cd /Users/mengdu/Desktop/Seeed-Zephyr-Project
```

- `cd` 是 `change directory` 的缩写，用来切换终端当前目录。
- 后面的绝对路径是 Seeed Zephyr 仓库的位置。
- 后续相对路径都以这个仓库根目录为起点。

### 2.2 复制已验证的基础示例

```bash
cp -R examples/boards/xiao_samd21/blinky examples/boards/xiao_samd21/dac
```

- `cp` 表示复制文件或目录。
- `-R` 表示递归复制目录中的全部子目录和文件。
- 第一个路径是来源：已经能够构建和运行的 `blinky` 示例。
- 第二个路径是目标：准备开发的 `dac` 示例。

从现有示例开始，可以复用已经验证过的 Zephyr 项目结构和 XIAO SAMD21 USB CDC 控制台配置。

复制后，目录包含：

```text
examples/boards/xiao_samd21/dac/
├── CMakeLists.txt
├── README.md
├── app.overlay
├── example.yaml
├── prj.conf
└── src/
    ├── README.md
    └── main.c
```

一句话总结：复制 `blinky` 是为了从一个已知可用的 Zephyr 骨架开始，再逐项替换为 DAC 功能。

## 3. 认识项目中的文件

- `CMakeLists.txt`：告诉构建系统需要编译哪些源代码。
- `prj.conf`：通过 Kconfig 选项开启应用需要的软件功能和驱动。
- `app.overlay`：在开发板基础设备树之上补充当前应用使用的硬件连接。
- `src/main.c`：应用程序入口和运行逻辑。
- `example.yaml`：本仓库的示例登记信息，供插件、构建脚本和检查工具读取。
- `README.md`：面向示例使用者的说明。
- `src/README.md`：源代码目录说明。

其中，`example.yaml` 是 Seeed 仓库自己的管理文件；CMake、Kconfig、Devicetree 和 C 源代码属于 Zephyr 项目的核心组成。

一句话总结：每个文件只负责一类问题，组合起来形成完整的 Zephyr 应用。

## 4. 理解 `CMakeLists.txt`

当前 DAC 示例使用以下内容：

```cmake
cmake_minimum_required(VERSION 3.20.0)

find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(xiao_samd21_dac)

target_sources(app PRIVATE src/main.c)
```

### 4.1 `cmake_minimum_required`

```cmake
cmake_minimum_required(VERSION 3.20.0)
```

- `CMake` 是负责组织编译过程的构建系统。
- `cmake_minimum_required()` 声明项目要求的最低 CMake 版本。
- `VERSION 3.20.0` 表示至少需要 CMake 3.20.0。

这行检查的是 CMake 版本，不是 Zephyr 版本。

### 4.2 `find_package`

```cmake
find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
```

- `find_package(Zephyr ...)` 查找并加载 Zephyr 的 CMake 构建能力。
- `REQUIRED` 表示 Zephyr 是构建当前项目的必要依赖。
- `HINTS` 提供查找位置提示。
- `$ENV{ZEPHYR_BASE}` 读取名为 `ZEPHYR_BASE` 的环境变量，它指向 Zephyr 源码目录。

加载完成后，项目才能使用 Zephyr 内核、设备驱动、Kconfig、Devicetree 和板级配置。

### 4.3 `project`

```cmake
project(xiao_samd21_dac)
```

- `project()` 为当前 CMake 项目命名。
- `xiao_samd21_dac` 表示这是 XIAO SAMD21 的 DAC 应用。

项目名称用于 CMake 内部和构建日志。开发板由构建命令的 `-b seeeduino_xiao` 参数选择。

### 4.4 `target_sources`

```cmake
target_sources(app PRIVATE src/main.c)
```

- `target_sources()` 为编译目标添加源文件。
- `app` 是 Zephyr 已经创建好的应用程序目标。
- `PRIVATE` 表示该源文件属于当前应用。
- `src/main.c` 是需要编译的 C 源文件。

### 4.5 检查文件内容

```bash
sed -n '1,20p' examples/boards/xiao_samd21/dac/CMakeLists.txt
```

- `sed` 是文本处理工具。
- `-n` 关闭默认的全部输出。
- `'1,20p'` 表示打印第 1 到第 20 行。
- 这个命令只读取文件，不改变内容。

一句话总结：`CMakeLists.txt` 把当前目录接入 Zephyr 构建系统，并把 `src/main.c` 加入应用。

## 5. 理解 `example.yaml`

当前内容为：

```yaml
id: xiao_samd21_dac
board_id: xiao_samd21
demo: dac
zephyr_target: seeeduino_xiao
validation_status: experimental
expected_behavior: Generates a 440 Hz, 10-bit sine wave on D0 and reports the loopback voltage sampled from D1.
```

YAML 使用 `名称: 值` 记录配置。冒号后保留一个空格；当前文件没有嵌套层级，因此每一行都从最左侧开始。

### 5.1 `id`

```yaml
id: xiao_samd21_dac
```

`id` 是示例在仓库中的唯一身份，由开发板名称 `xiao_samd21` 和功能名称 `dac` 组成。

### 5.2 `board_id`

```yaml
board_id: xiao_samd21
```

`board_id` 连接到 `metadata/boards/xiao_samd21.yaml`，表示该示例属于 Seeed Studio XIAO SAMD21。

### 5.3 `demo`

```yaml
demo: dac
```

`demo` 是示例功能的短名称，并与目录名称 `examples/boards/xiao_samd21/dac` 保持一致。

### 5.4 `zephyr_target`

```yaml
zephyr_target: seeeduino_xiao
```

`xiao_samd21` 是本仓库的产品标识，`seeeduino_xiao` 是上游 Zephyr 构建系统使用的开发板目标。原生构建命令会使用 `west build -b seeeduino_xiao`。

### 5.5 `validation_status`

```yaml
validation_status: experimental
```

`experimental` 表示示例处于开发和验证阶段。完成构建及真实硬件验证后，再依据验证证据更新状态。

### 5.6 `expected_behavior`

```yaml
expected_behavior: Generates a 440 Hz, 10-bit sine wave on D0 and reports the loopback voltage sampled from D1.
```

该字段描述最终验收结果：D0 输出 10 位、440 Hz 正弦波，D1 读取回环电压，并通过控制台报告结果。它是验收说明，不会直接控制程序频率。

一句话总结：`example.yaml` 让仓库和插件知道这个示例属于哪块板、叫什么、处于什么验证阶段以及成功时应看到什么。

## 6. 登记 `dac` 示例类型

仓库检查工具在 `tools/validate_metadata/validate.py` 中维护允许使用的板级示例名称：

```python
VALID_EXAMPLE_DEMOS = {"blinky", "dac", "hello_world"}
```

- `VALID_EXAMPLE_DEMOS` 表示合法示例名称集合。
- `=` 把右侧数据保存到左侧变量。
- `{}` 在 Python 中表示集合，集合保存不重复的成员。
- `"blinky"`、`"dac"` 和 `"hello_world"` 是三个合法示例名称。

检查工具读取 `example.yaml` 中的 `demo: dac` 后，会确认 `dac` 存在于该集合中。

### 6.1 运行元数据检查

```bash
/Users/mengdu/zephyrproject/.venv/bin/python tools/validate_metadata/validate.py
```

- `/Users/mengdu/zephyrproject/.venv/bin/python` 是 Zephyr 虚拟环境中的 Python 解释器。
- `tools/validate_metadata/validate.py` 是要运行的仓库元数据检查程序。
- 检查程序会读取开发板、模块、扩展板以及示例 YAML 文件。
- 该命令检查登记数据和文件结构，不编译固件。

成功输出中应包含：

```text
PASS examples/boards/xiao_samd21/dac/example.yaml
SUMMARY: ... passed, 0 failed, ... total
```

一句话总结：登记并验证 `dac` 后，仓库工具和插件就能把它识别为正式的示例类型。

## 7. 配置 `prj.conf`

`prj.conf` 是 Zephyr 应用自己的功能开关文件。可以把它理解成一张“购物清单”：程序要用 DAC、ADC、USB 串口这些能力，就要先在这张清单里写出来，Zephyr 构建时才会把对应驱动和子系统编进固件。

这里第一次遇到一个重要概念：Kconfig。Kconfig 是 Zephyr 用来开关功能的配置系统。`CONFIG_XXX=y` 的意思是“打开这个功能”，`CONFIG_XXX=n` 的意思是“关闭这个功能”。

一句话总结：`prj.conf` 不写业务代码，它告诉 Zephyr 这个程序需要哪些系统能力。

### 7.1 本示例需要的能力

这个 DAC 示例从 Arduino 版本迁移过来后，核心动作有三个：

- 输出模拟电压，对应 Arduino 里的 `analogWrite(A0, dacVoltage)`。
- 读取模拟电压，对应 Arduino 里的 `analogRead(A1)`。
- 通过 USB 串口打印电压，对应 Arduino 里的 `Serial.println(voltage)`。

所以 `prj.conf` 里要打开 DAC、ADC 和串口控制台相关能力。

一句话总结：Arduino 的三个动作，在 Zephyr 里会拆成 DAC、ADC、USB 串口控制台三组配置。

### 7.2 先按功能分组理解

`prj.conf` 里会出现很多 `CONFIG_` 开头的名字。刚开始不需要死记硬背，可以先把它们分成 4 组。

第一组是模拟输入输出：

```conf
CONFIG_DAC=y
CONFIG_ADC=y
```

`CONFIG_DAC=y` 打开“数字转电压”的能力。程序给出一个数字，DAC 把它变成引脚上的模拟电压。

`CONFIG_ADC=y` 打开“电压转数字”的能力。板子读取一个电压，ADC 把它变成程序能处理的数字。

一句话总结：DAC 负责写电压，ADC 负责读电压。

第二组是打印能力：

```conf
CONFIG_PRINTK=y
CONFIG_STDOUT_CONSOLE=y
```

`CONFIG_PRINTK=y` 打开 Zephyr 的基础打印函数 `printk()`。它的作用可以先理解成 Zephyr 里的 `Serial.print()`。

`CONFIG_STDOUT_CONSOLE=y` 把程序默认的文字输出接到控制台上。简单说，就是让打印出来的文字有地方出去。

一句话总结：这两行让程序能把电压值打印出来。

第三组是串口控制台：

```conf
CONFIG_SERIAL=y
CONFIG_CONSOLE=y
CONFIG_UART_CONSOLE=y
CONFIG_UART_LINE_CTRL=y
```

`CONFIG_SERIAL=y` 打开串口驱动。串口可以理解成电脑和开发板之间传文字的一条通道。

`CONFIG_CONSOLE=y` 打开 Zephyr 的控制台系统。控制台是 Zephyr 统一管理文字输出的地方。

`CONFIG_UART_CONSOLE=y` 告诉 Zephyr 控制台走 UART。这里的 UART 不一定是板子上单独的硬件串口，因为 USB CDC 虚拟串口也会被 Zephyr 当成一种 UART 设备来用。

`CONFIG_UART_LINE_CTRL=y` 打开串口线路控制。USB 串口常用它来判断电脑端有没有打开串口监视器，比如 DTR 状态。

一句话总结：这几行把“打印文字”接到“USB 虚拟串口”这条路上。

第四组是 USB 设备能力：

```conf
CONFIG_USB_DEVICE_STACK=y
CONFIG_DEPRECATION_TEST=y
CONFIG_USB_DEVICE_PRODUCT="Seeed XIAO SAMD21 DAC"
CONFIG_USB_DEVICE_PID=0x0004
CONFIG_USB_DEVICE_INITIALIZE_AT_BOOT=n
CONFIG_USB_DEVICE_STACK_NEXT=n
```

`CONFIG_USB_DEVICE_STACK=y` 打开 USB 设备协议栈。协议栈就是一整套通信规则，Zephyr 靠它让开发板被电脑识别成 USB 设备。

`CONFIG_DEPRECATION_TEST=y` 允许这个示例继续使用 Zephyr 的 legacy USB 设备栈相关接口。这里沿用仓库现有 XIAO SAMD21 示例的 USB 配置方式。

`CONFIG_USB_DEVICE_PRODUCT="Seeed XIAO SAMD21 DAC"` 设置电脑看到的 USB 设备名称。这里从 `blinky` 改成 `DAC`，是为了让设备名和当前示例一致。

`CONFIG_USB_DEVICE_PID=0x0004` 设置 USB Product ID。电脑识别 USB 设备时会用到这个值。这里先沿用已有配置。

`CONFIG_USB_DEVICE_INITIALIZE_AT_BOOT=n` 表示 USB 不在系统一启动时自动初始化。后面写 `main.c` 时，程序可以在合适位置主动启用 USB。

`CONFIG_USB_DEVICE_STACK_NEXT=n` 关闭 Zephyr 新一代 USB 设备栈，继续使用当前示例采用的 legacy USB 配置方式。

一句话总结：这几行让 XIAO SAMD21 可以通过 USB 变成电脑上的串口设备。

### 7.3 推荐的 `prj.conf` 内容

把 `examples/boards/xiao_samd21/dac/prj.conf` 调整为下面这样：

```conf
CONFIG_DAC=y
CONFIG_ADC=y
CONFIG_PRINTK=y
CONFIG_SERIAL=y
CONFIG_CONSOLE=y
CONFIG_UART_CONSOLE=y
CONFIG_STDOUT_CONSOLE=y
CONFIG_UART_LINE_CTRL=y
CONFIG_USB_DEVICE_STACK=y
CONFIG_DEPRECATION_TEST=y
CONFIG_USB_DEVICE_PRODUCT="Seeed XIAO SAMD21 DAC"
CONFIG_USB_DEVICE_PID=0x0004
CONFIG_USB_DEVICE_INITIALIZE_AT_BOOT=n
CONFIG_USB_DEVICE_STACK_NEXT=n
```

这一节先只改配置，不写 `main.c`。配置文件改完以后，后面的 C 代码才能顺利调用 DAC、ADC 和串口输出相关 API。

如果你的文件里还保留了从 `blinky` 示例复制来的这一行：

```conf
CONFIG_GPIO=y
```

它表示打开 GPIO 驱动。GPIO 是 General Purpose Input/Output，中文可以理解成“通用数字输入输出引脚”。DAC 示例主流程暂时不依赖 GPIO；保留这一行不会影响本节，后面整理最小配置时可以再处理。

一句话总结：先把能力开关打开，再写真正控制硬件的 C 代码。

### 7.4 每一行的作用

```conf
CONFIG_DAC=y
```

打开 DAC 子系统。DAC 是 Digital-to-Analog Converter，中文叫“数字转模拟转换器”。它的作用是把程序里的数字，比如 `0` 到 `1023`，转换成板子引脚上的模拟电压。

```conf
CONFIG_ADC=y
```

打开 ADC 子系统。ADC 是 Analog-to-Digital Converter，中文叫“模拟转数字转换器”。它的作用正好和 DAC 相反：把引脚上的模拟电压读回来，变成程序里的数字。

```conf
CONFIG_PRINTK=y
```

打开 `printk()` 输出能力。`printk()` 可以先理解成 Zephyr 里的基础打印函数，作用类似 Arduino 里的 `Serial.print()`。

```conf
CONFIG_SERIAL=y
```

打开串口驱动。串口可以理解成电脑和开发板之间的一条文字通道，开发板把日志和电压值通过这条通道发给电脑。

```conf
CONFIG_CONSOLE=y
```

打开控制台系统。控制台是 Zephyr 里接收和输出文字信息的统一出口。

```conf
CONFIG_UART_CONSOLE=y
```

把 UART 作为控制台后端。UART 是常见串口通信硬件；在这个例子里，Zephyr 会把 USB CDC 虚拟串口也表现成一个 UART 设备。

```conf
CONFIG_STDOUT_CONSOLE=y
```

把标准输出连接到控制台。标准输出可以理解成程序默认“往外打印文字”的出口。

```conf
CONFIG_UART_LINE_CTRL=y
```

打开 UART 线路控制能力。USB CDC 串口通常需要读取 DTR 等状态，确认电脑端串口已经打开。

```conf
CONFIG_USB_DEVICE_STACK=y
```

打开 USB 设备协议栈。协议栈可以理解成一整套通信规则，Zephyr 通过它把开发板识别成 USB 设备。

```conf
CONFIG_DEPRECATION_TEST=y
```

允许当前示例继续使用 Zephyr legacy USB 设备栈相关接口。本仓库现有 XIAO SAMD21 示例沿用了这套 USB 配置。

```conf
CONFIG_USB_DEVICE_PRODUCT="Seeed XIAO SAMD21 DAC"
```

设置电脑看到的 USB 设备名称。这里把从 `blinky` 复制来的名称改成 `DAC`，这样串口设备信息更符合当前示例。

```conf
CONFIG_USB_DEVICE_PID=0x0004
```

设置 USB Product ID。这里沿用当前示例已有值，保持和现有 USB 配置一致。

```conf
CONFIG_USB_DEVICE_INITIALIZE_AT_BOOT=n
```

设置 USB 设备栈不在系统启动时自动初始化。后续程序代码可以在合适的位置主动启用 USB。

```conf
CONFIG_USB_DEVICE_STACK_NEXT=n
```

选择使用当前示例的 legacy USB 设备栈配置。`STACK_NEXT` 是 Zephyr 新一代 USB 设备栈开关，这里保持关闭。

一句话总结：`prj.conf` 每一行都在告诉 Zephyr“我要哪一块系统能力”，不是在直接操作引脚。

### 7.5 修改后先检查文件内容

修改完成后，在仓库根目录运行：

```bash
sed -n '1,80p' examples/boards/xiao_samd21/dac/prj.conf
```

这个命令的作用是打印 `prj.conf` 的第 1 到第 80 行：

- `sed` 是一个文本查看和处理工具。
- `-n` 表示先不要自动打印所有内容。
- `'1,80p'` 表示只打印第 1 到第 80 行。
- `examples/boards/xiao_samd21/dac/prj.conf` 是要查看的文件。

预期能看到 `CONFIG_DAC=y`、`CONFIG_ADC=y`，以及 USB 产品名 `Seeed XIAO SAMD21 DAC`。

一句话总结：这一步只是确认文件写对了，还不编译固件。

## 8. 理解 `app.overlay`

`app.overlay` 是应用自己的设备树覆盖文件。设备树是 Devicetree，简单说就是 Zephyr 用来描述硬件的一张“地图”：板子上有哪些外设、外设叫什么、引脚怎么连，都可以放在这张地图里。

`overlay` 的意思是“覆盖”或“补充”。应用里的 `app.overlay` 不会替换整块板子的设备树，而是在板级设备树的基础上补几行应用需要的硬件描述。

一句话总结：`prj.conf` 负责开功能，`app.overlay` 负责告诉 Zephyr 这些功能对应到哪一个硬件设备。

### 8.0 先建立脑内模型

可以先把 Zephyr 的硬件信息分成三层：

第一层是 SoC 设备树。SoC 是 System on Chip，中文可以理解成“芯片本体”。SAMD21 芯片本身有什么外设，比如 USB、ADC、DAC、SERCOM，会先在 SoC 设备树里描述。

第二层是开发板设备树。XIAO SAMD21 这块板子把芯片的哪些外设接出来、哪些引脚用于 LED、USB、DAC，会在板级设备树里描述。

第三层是应用 overlay。某个具体示例如果想改变默认选择，或者给某个外设补一个子设备，就在自己的 `app.overlay` 里写。

本示例的 `app.overlay` 做的是第三层的事：它不重新描述整块 XIAO SAMD21，只补充“USB 控制器下面有一个 CDC ACM 虚拟串口，并把控制台指向它”。

一句话总结：设备树像硬件地图，`app.overlay` 是在地图上贴一张和当前示例有关的小纸条。

### 8.1 当前文件内容

当前 `examples/boards/xiao_samd21/dac/app.overlay` 内容如下：

```dts
/*
 * SPDX-License-Identifier: Apache-2.0
 */

/ {
	chosen {
		zephyr,console = &cdc_acm_uart0;
	};
};

&zephyr_udc0 {
	cdc_acm_uart0: cdc_acm_uart0 {
		compatible = "zephyr,cdc-acm-uart";
		label = "CDC_ACM_0";
	};
};
```

这个文件已经满足当前阶段的需求：它把 Zephyr 控制台输出接到 USB CDC ACM 虚拟串口上。CDC ACM 可以先理解成“电脑上看到的 USB 虚拟串口”。

一句话总结：这个 `app.overlay` 的目的就是让 `printk()` 这类输出能从 USB 串口出来。

### 8.2 每一行的作用

```dts
/*
 * SPDX-License-Identifier: Apache-2.0
 */
```

这是许可证声明，说明这个文件使用 Apache-2.0 许可证。它不影响程序运行，但对开源项目很重要。

```dts
/ {
```

`/` 表示设备树的根节点。根节点可以理解成硬件地图的最外层目录。

```dts
	chosen {
```

`chosen` 是设备树里的特殊区域，用来告诉 Zephyr 某些“默认选择”。比如默认控制台、默认 shell 串口、默认 flash、默认内存等。

```dts
		zephyr,console = &cdc_acm_uart0;
```

这一行告诉 Zephyr：控制台输出使用 `cdc_acm_uart0` 这个设备。`&cdc_acm_uart0` 里的 `&` 表示引用一个已经命名的设备节点，可以理解成“去找这个名字对应的硬件设备”。

```dts
	};
};
```

这两行关闭 `chosen` 节点和根节点。设备树用 `{}` 表示一段节点内容，写完以后要用 `};` 结束。

```dts
&zephyr_udc0 {
```

这一行引用板级设备树里已经存在的 USB 设备控制器。`UDC` 是 USB Device Controller，也就是“让开发板作为 USB 设备连接到电脑”的控制器。

在 XIAO SAMD21 的板级设备树里，`zephyr_udc0` 已经指向 `usb0`，并且状态是 `okay`。所以应用里可以直接在它下面添加 USB CDC ACM 子设备。

```dts
	cdc_acm_uart0: cdc_acm_uart0 {
```

这一行创建一个新的设备节点。冒号左边的 `cdc_acm_uart0` 是标签，后面可以通过 `&cdc_acm_uart0` 引用它；冒号右边的 `cdc_acm_uart0` 是节点名。

```dts
		compatible = "zephyr,cdc-acm-uart";
```

`compatible` 告诉 Zephyr 这个节点应该匹配哪一种驱动。这里的 `zephyr,cdc-acm-uart` 表示把 USB CDC ACM 设备表现成一个 UART 串口设备。

```dts
		label = "CDC_ACM_0";
```

`label` 是这个设备的可读名称。后面的代码调试或日志里可能会看到这个名字。

```dts
	};
};
```

这两行关闭 `cdc_acm_uart0` 节点和 `zephyr_udc0` 节点。

一句话总结：这段设备树做了一件事：在 USB 控制器下面创建一个虚拟串口，并把 Zephyr 控制台指向它。

### 8.3 这段 DTS 语法怎么读

设备树文件通常使用 DTS 语法。DTS 可以先理解成一种专门描述硬件的配置语言。

```dts
node_name {
	property = value;
};
```

这是最常见的结构：

- `node_name` 是节点名，可以理解成硬件地图里的一个条目。
- `{ ... }` 里面放这个节点的属性或子节点。
- `property = value;` 是属性，表示这个节点的一条信息。
- 每条属性后面的 `;` 表示这一句结束。
- 最后的 `};` 表示这个节点结束。

在当前文件里还会看到这种写法：

```dts
cdc_acm_uart0: cdc_acm_uart0 {
```

冒号左边的 `cdc_acm_uart0` 是标签。标签的作用是让别的地方可以用 `&cdc_acm_uart0` 找到这个节点。

冒号右边的 `cdc_acm_uart0` 是节点名。节点名描述这个节点本身是什么。

还会看到这种写法：

```dts
&zephyr_udc0 {
```

`&zephyr_udc0` 表示“引用已经存在的 `zephyr_udc0` 节点，然后往它里面补内容”。这里补进去的内容就是 `cdc_acm_uart0` 这个 USB 虚拟串口。

一句话总结：DTS 的关键读法是看节点、属性、标签和引用，先不要把它当 C 代码来读。

### 8.4 Zephyr 最后怎么使用这段配置

这段配置最终会形成一条很清楚的路径：

```text
printk()
-> Zephyr console
-> zephyr,console
-> cdc_acm_uart0
-> zephyr,cdc-acm-uart driver
-> zephyr_udc0 USB device controller
-> USB cable
-> computer serial monitor
```

逐步拆开看：

- 代码里调用 `printk()` 打印文字。
- Zephyr 把这类文字交给 console，也就是控制台系统。
- `zephyr,console = &cdc_acm_uart0;` 告诉控制台使用 `cdc_acm_uart0`。
- `compatible = "zephyr,cdc-acm-uart";` 让 Zephyr 给这个节点匹配 USB CDC ACM UART 驱动。
- `&zephyr_udc0` 表示这个虚拟串口挂在 USB 设备控制器下面。
- 最后电脑通过 USB 线看到一个串口设备。

一句话总结：这段 overlay 把“程序打印文字”一路接到了“电脑上的 USB 串口”。

### 8.5 为什么这里不用新增 DAC 节点，以及为什么 ADC 还要继续检查

XIAO SAMD21 的板级设备树已经启用了 DAC：

```dts
&dac0 {
	status = "okay";

	pinctrl-0 = <&dac_default>;
	pinctrl-names = "default";
};
```

板级连接文件里也已经提供了别名：

```dts
xiao_dac: &dac0 {};
xiao_adc: &adc {};
```

这里要分清两件事。

`xiao_dac: &dac0 {};` 表示板子给 `dac0` 取了一个适合 XIAO 系列使用的名字。由于 `seeeduino_xiao.dts` 里已经把 `&dac0` 设置成 `status = "okay";`，所以 DAC 这部分已经能被 Zephyr 当成可用硬件。

`xiao_adc: &adc {};` 表示板子也给 `adc` 取了一个名字。但是“有名字”不等于“已经启用”。真正的 ADC 控制器节点来自 SoC 设备树：

```text
/Users/mengdu/zephyrproject/zephyr/dts/arm/atmel/samd2x.dtsi
```

里面的 ADC 节点是：

```dts
adc: adc@42004000 {
	compatible = "atmel,sam0-adc";
	reg = <0x42004000 0x2b>;
	status = "disabled";

	#io-channel-cells = <1>;

	prescaler = <4>;
};
```

所以 ADC 的判断要继续往下走：节点存在，名字也有，但默认状态是 `disabled`。后面真正写 ADC 示例时，我们需要在应用 overlay 里把它启用，并说明要读哪一个 ADC 输入通道。

一句话总结：DAC 已经在板级设备树里启用；ADC 只有名字和基础节点，还要通过 overlay 启用并选择输入通道。

### 8.6 检查 `app.overlay`

在仓库根目录运行：

```bash
sed -n '1,80p' examples/boards/xiao_samd21/dac/app.overlay
```

这个命令会打印 `app.overlay` 的第 1 到第 80 行。预期能看到：

- `zephyr,console = &cdc_acm_uart0;`
- `&zephyr_udc0 {`
- `compatible = "zephyr,cdc-acm-uart";`

如果这三部分都存在，说明 USB 虚拟串口控制台的设备树描述已经在应用里准备好了。

一句话总结：这一节不需要改 `app.overlay`，只要确认 USB 串口控制台配置存在即可。

### 8.7 这些配置从哪里来

Zephyr 配置不能靠猜。遇到一个外设时，可以按下面这个顺序查来源。

第一步，看当前应用要做什么。

Arduino 示例里有三件事：

- `analogWrite(A0, dacVoltage)`：需要 DAC。
- `analogRead(A1)`：需要 ADC。
- `Serial.println(voltage)`：需要串口输出。

所以我们先知道方向：这个 Zephyr 示例至少需要 DAC、ADC 和一个能打印文字的控制台。

一句话总结：先从功能需求出发，判断大方向需要哪些硬件能力。

第二步，看板级设备树里有没有这些硬件。

XIAO SAMD21 的板级设备树在 Zephyr 源码里：

```text
/Users/mengdu/zephyrproject/zephyr/boards/seeed/seeeduino_xiao/seeeduino_xiao.dts
```

可以用这个命令查看：

```bash
sed -n '1,120p' /Users/mengdu/zephyrproject/zephyr/boards/seeed/seeeduino_xiao/seeeduino_xiao.dts
```

里面可以看到：

```dts
zephyr_udc0: &usb0 {
	status = "okay";

	pinctrl-0 = <&usb_dc_default>;
	pinctrl-names = "default";
};

&dac0 {
	status = "okay";

	pinctrl-0 = <&dac_default>;
	pinctrl-names = "default";
};
```

这说明两件事：

- `zephyr_udc0` 这个名字来自板级设备树，不是应用自己编的。
- `dac0` 已经是 `okay`，说明板级设备树已经启用了 DAC。

一句话总结：先查板级 `.dts`，确认硬件节点是否已经存在并启用。

第三步，看 XIAO 连接器别名。

XIAO 的连接器定义在：

```text
/Users/mengdu/zephyrproject/zephyr/boards/seeed/seeeduino_xiao/seeed_xiao_connector.dtsi
```

可以用这个命令查看：

```bash
sed -n '1,80p' /Users/mengdu/zephyrproject/zephyr/boards/seeed/seeeduino_xiao/seeed_xiao_connector.dtsi
```

里面可以看到：

```dts
gpio-map = <0 0 &porta 2 0>,		/* D0 */
	   <1 0 &porta 4 0>,		/* D1 */

xiao_dac: &dac0 {};
xiao_adc: &adc {};
```

这说明：

- XIAO 的 `D0` 对应芯片的 `PA2`。
- XIAO 的 `D1` 对应芯片的 `PA4`。
- `xiao_dac` 是 `dac0` 的别名。
- `xiao_adc` 是 `adc` 的别名。

一句话总结：connector 文件告诉你板子丝印上的 D0、D1 最后对应到芯片和 Zephyr 里的哪个设备。

第四步，看官方示例或 snippet，确认 overlay 写法。

USB CDC ACM 控制台的官方片段在：

```text
/Users/mengdu/zephyrproject/zephyr/snippets/cdc-acm-console/
```

可以查看它的 overlay：

```bash
sed -n '1,80p' /Users/mengdu/zephyrproject/zephyr/snippets/cdc-acm-console/cdc-acm-console.overlay
```

它的结构是：

```dts
/ {
	chosen {
		zephyr,console = &snippet_cdc_acm_console_uart;
		zephyr,shell-uart = &snippet_cdc_acm_console_uart;
	};
};

&zephyr_udc0 {
	snippet_cdc_acm_console_uart: snippet_cdc_acm_console_uart {
		compatible = "zephyr,cdc-acm-uart";
	};
};
```

这就是我们当前 `app.overlay` 写法的来源。当前示例只需要 console，所以只设置了 `zephyr,console`。

一句话总结：不确定 overlay 怎么写时，优先找 Zephyr 官方 sample 或 snippet 的写法。

第五步，看 binding，确认 `compatible` 是合法的。

`compatible = "zephyr,cdc-acm-uart";` 的定义在：

```text
/Users/mengdu/zephyrproject/zephyr/dts/bindings/serial/zephyr,cdc-acm-uart.yaml
```

里面有：

```yaml
description: USB CDC ACM UART
compatible: "zephyr,cdc-acm-uart"
include: uart-controller.yaml
on-bus: usb
```

这说明 `zephyr,cdc-acm-uart` 是 Zephyr 正式定义的设备类型，而且它挂在 USB 总线上。

一句话总结：`compatible` 要去 `dts/bindings/` 里查，那里定义了“这个节点到底是什么设备”。

第六步，看 Kconfig，确认要打开哪些 `CONFIG_`。

DAC 的总开关来自：

```text
/Users/mengdu/zephyrproject/zephyr/drivers/dac/Kconfig
```

里面有：

```kconfig
menuconfig DAC
	bool "Digital-to-Analog Converter (DAC) drivers"
```

所以应用里要写：

```conf
CONFIG_DAC=y
```

SAMD21 属于 SAM0 系列，具体 DAC 驱动来自：

```text
/Users/mengdu/zephyrproject/zephyr/drivers/dac/Kconfig.sam0
```

里面有：

```kconfig
config DAC_SAM0
	default y
	depends on DT_HAS_ATMEL_SAM0_DAC_ENABLED
```

这句话的意思是：当设备树里存在并启用了 `atmel,sam0-dac` 这种 DAC 节点时，SAM0 DAC 驱动会默认启用。

ADC 也类似，来源在：

```text
/Users/mengdu/zephyrproject/zephyr/drivers/adc/Kconfig.sam0
```

里面有：

```kconfig
config ADC_SAM0
	default y
	depends on DT_HAS_ATMEL_SAM0_ADC_ENABLED
```

一句话总结：`CONFIG_DAC=y` 和 `CONFIG_ADC=y` 来自 Zephyr 的 Kconfig；具体 SAM0 驱动是否启用，还要看设备树里是否有对应硬件节点。

### 8.8 判断一个外设要不要写 overlay 的方法

以后遇到新外设，可以按这个判断：

第一，看板级设备树里有没有这个设备。

- 如果已经有，而且 `status = "okay";`，应用通常不需要重新声明这个硬件。
- 如果有但 `status = "disabled";`，应用 overlay 可能需要把它改成 `okay`，并补 pinctrl 等信息。
- 如果没有这个设备节点，要先确认这块芯片和板子是否真的支持这个外设。

第二，看应用是否要改默认选择。

比如 XIAO SAMD21 板级默认控制台是 `sercom4`，但这个 DAC 示例要把打印走 USB 虚拟串口，所以 `app.overlay` 需要写：

```dts
zephyr,console = &cdc_acm_uart0;
```

第三，看是否要增加子设备。

USB 控制器 `zephyr_udc0` 已经存在，但 CDC ACM 虚拟串口这个子设备是当前应用要用的，所以在 `app.overlay` 里补：

```dts
&zephyr_udc0 {
	cdc_acm_uart0: cdc_acm_uart0 {
		compatible = "zephyr,cdc-acm-uart";
	};
};
```

一句话总结：设备树不是靠想象写的，先查板级是否已有，再查官方示例怎么补，最后用 binding 和 Kconfig 验证写法是否合法。

### 8.9 先学会“怎么找到该看的文件”

Zephyr 的源码目录很大，初学时最容易卡在一个问题：别人说“打开这个文件”，但自己不知道这个文件为什么在那里。解决方法不是背路径，而是先掌握 Zephyr 查硬件信息的固定入口。

可以把 Zephyr 的硬件描述想成一套档案柜：`board target` 是档案编号，板级 `.dts` 是第一张档案，`.dtsi` 是它引用的附页，binding 是字段说明书，Kconfig 是功能开关清单。

一句话总结：学习设备树的第一步不是记住某个文件名，而是知道 Zephyr 是按什么顺序把硬件信息找出来的。

第一步，先确认当前示例使用的 `board target`。

`board target` 可以理解成“构建时选择的开发板型号”。你平时运行 Zephyr 构建命令时，`-b` 后面的名字就是它，例如：

```bash
west build -b seeeduino_xiao examples/boards/xiao_samd21/dac
```

这里的 `seeeduino_xiao` 就是 board target。Zephyr 会根据这个名字去找对应开发板的设备树。

如果你只知道板子大概叫 XIAO，可以先查 Zephyr 认识哪些相关开发板：

```bash
west boards | rg -i "xiao|seeeduino"
```

如果当前环境暂时不想跑 `west boards`，也可以直接在 Zephyr 源码里查开发板登记文件：

```bash
rg -n "^identifier: seeeduino_xiao$" /Users/mengdu/zephyrproject/zephyr/boards -g "*.yaml"
```

这个命令的意思是：在 Zephyr 的 `boards` 目录下，找哪一个 `.yaml` 文件声明了 `identifier: seeeduino_xiao`。

找到的文件是：

```text
/Users/mengdu/zephyrproject/zephyr/boards/seeed/seeeduino_xiao/seeeduino_xiao.yaml
```

这说明 `seeeduino_xiao` 这个 board target 对应的开发板目录就是：

```text
/Users/mengdu/zephyrproject/zephyr/boards/seeed/seeeduino_xiao/
```

一句话总结：先找 board target，因为 Zephyr 是从 board target 开始决定“这次构建用哪块板子的硬件地图”。

第二步，从开发板目录打开板级 `.dts`。

进入刚才找到的目录后，你通常会看到这些文件：

```text
seeeduino_xiao.dts
seeeduino_xiao.yaml
seeeduino_xiao-pinctrl.dtsi
seeed_xiao_connector.dtsi
```

这里最重要的是 `seeeduino_xiao.dts`。`.dts` 是 Devicetree Source，通俗讲就是“这块开发板的主硬件地图”。Zephyr 选中 `seeeduino_xiao` 这个 board target 后，会从这个 `.dts` 开始合并设备树。

查看它的开头：

```bash
sed -n '1,30p' /Users/mengdu/zephyrproject/zephyr/boards/seeed/seeeduino_xiao/seeeduino_xiao.dts
```

你会看到类似内容：

```dts
/dts-v1/;
#include <atmel/samd21.dtsi>
#include <atmel/samx2xx18.dtsi>
#include "seeeduino_xiao-pinctrl.dtsi"
#include "seeed_xiao_connector.dtsi"
```

这里有两种 `#include`：

- `"seeed_xiao_connector.dtsi"` 这种带双引号的文件，一般就在当前开发板目录附近。
- `<atmel/samd21.dtsi>` 这种带尖括号的文件，一般来自 Zephyr 的通用 DTS include 路径，也就是芯片或芯片系列的公共描述。

所以你不是凭空知道要看 connector 文件，而是因为板级 `.dts` 明确 include 了它。你也不是凭空知道要看 `samd21.dtsi`，也是因为板级 `.dts` 明确 include 了它。

一句话总结：板级 `.dts` 是入口；它 include 了什么，你就顺着什么继续看。

第三步，先看“板子把哪些引脚接出来”。

现在我们要找 Arduino 的 `A1`。这属于“板子引脚名称到芯片脚位”的问题，所以先看 connector 文件，而不是先看 ADC 驱动。

原因很简单：`A1` 是板子丝印或 Arduino 命名，不是芯片内部名字。Zephyr 需要知道它最后连到芯片的哪一个脚。

打开 connector 文件：

```bash
sed -n '1,80p' /Users/mengdu/zephyrproject/zephyr/boards/seeed/seeeduino_xiao/seeed_xiao_connector.dtsi
```

里面有：

```dts
gpio-map = <0 0 &porta 2 0>,		/* D0 */
	   <1 0 &porta 4 0>,		/* D1 */
```

这段可以这样读：

- 注释里的 `D1` 是 XIAO 板子上的数字引脚名。
- `&porta` 是 SAMD21 的 GPIO A 端口控制器。
- `4` 表示 A 端口的第 4 号脚，也就是 `PA4`。

对于 XIAO SAMD21，`A1` 和 `D1` 是同一个板子引脚的两种使用场景：做数字 IO 时叫 `D1`，做模拟输入时叫 `A1`。所以这一步得到：`A1/D1 -> PA4`。

一句话总结：要找 `A1` 这种板子引脚，先看板级 connector 或官方 pinout，因为它负责把板子名字翻译成芯片脚位。

第四步，再看“这个芯片脚能不能做 ADC”。

知道 `A1` 是 `PA4` 之后，还不能直接写 `<&adc 4>`。我们还要确认 `PA4` 在 SAMD21 芯片里有没有 ADC 功能，以及对应 ADC 的几号输入。

这一步为什么看 pinctrl？因为 pinctrl 是 Pin Control，通俗讲就是“引脚功能选择表”。同一个芯片脚可能有很多功能，比如 GPIO、串口、I2C、ADC。pinctrl 文件会告诉 Zephyr 某个脚可以切到哪种功能。

先看 XIAO 的 pinctrl 文件：

```bash
sed -n '1,20p' /Users/mengdu/zephyrproject/zephyr/boards/seeed/seeeduino_xiao/seeeduino_xiao-pinctrl.dtsi
```

它 include 了这个头文件：

```dts
#include <dt-bindings/pinctrl/samd21-da1gXabcd-pinctrl.h>
```

然后顺着这个 include 去查 `PA4` 的 ADC 功能：

```bash
rg -n "PA4.*ADC|PA4B_ADC_AIN4" /Users/mengdu/zephyrproject/modules/hal/atmel/include/dt-bindings/pinctrl/samd21-da1gXabcd-pinctrl.h
```

可以找到：

```c
/* pa4b_adc_ain4 */
#define PA4B_ADC_AIN4 \
	SAM_PINMUX(a, 4, b, periph)
```

这段的意思是：`PA4` 可以通过 B 组复用功能连接到 ADC，并且它对应的是 `AIN4`，也就是 ADC 输入 4。

一句话总结：`A1 -> PA4 -> ADC AIN4` 这条链，是从 connector 和 pinctrl 两类文件一步步查出来的。

第五步，再看“Zephyr 里 ADC 控制器节点叫什么”。

现在我们已经知道外部引脚是 ADC 输入 4，但还不知道 overlay 里应该写 `&adc`、`&adc0`，还是别的名字。这个名字来自 SoC 设备树。

为什么看 SoC 设备树？因为 ADC 控制器是 SAMD21 芯片内部的硬件，不是 XIAO 板子额外接上去的外设。芯片内部有什么 ADC、地址是多少、默认开不开，通常写在 SoC `.dtsi` 里。

从板级 `.dts` 的 include 可以看到它引用了：

```dts
#include <atmel/samd21.dtsi>
```

打开它：

```bash
sed -n '1,30p' /Users/mengdu/zephyrproject/zephyr/dts/arm/atmel/samd21.dtsi
```

你会看到：

```dts
#include <atmel/samd2x.dtsi>
```

这说明 `samd21.dtsi` 还继续引用了 SAMD2x 系列的公共描述。继续打开公共文件：

```bash
sed -n '200,215p' /Users/mengdu/zephyrproject/zephyr/dts/arm/atmel/samd2x.dtsi
```

里面有真正的 ADC 节点：

```dts
adc: adc@42004000 {
	compatible = "atmel,sam0-adc";
	reg = <0x42004000 0x2b>;
	status = "disabled";
	#io-channel-cells = <1>;
	prescaler = <4>;
};
```

这里的 `adc:` 是节点标签。设备树里用 `&adc` 引用的就是这个标签。所以 overlay 里写 `&adc { ... };` 的来源就是这里。

一句话总结：控制器名字不是猜的；先从板级 `.dts` 顺着 include 走到 SoC `.dtsi`，再看节点标签。

第六步，用 `compatible` 找 binding。

现在我们知道 ADC 节点的 `compatible` 是：

```dts
compatible = "atmel,sam0-adc";
```

`compatible` 可以理解成“设备型号标签”。Zephyr 会用它找到对应的 binding 和驱动。

binding 是 Devicetree Binding，通俗讲就是“设备树字段说明书”。它告诉你这个设备节点能写哪些属性、哪些属性必填、属性值是什么类型。

用 `compatible` 去查 binding：

```bash
rg -n 'compatible: "atmel,sam0-adc"' /Users/mengdu/zephyrproject/zephyr/dts/bindings
```

会找到：

```text
/Users/mengdu/zephyrproject/zephyr/dts/bindings/adc/atmel,sam0-adc.yaml
```

打开它：

```bash
sed -n '1,80p' /Users/mengdu/zephyrproject/zephyr/dts/bindings/adc/atmel,sam0-adc.yaml
```

里面有：

```yaml
compatible: "atmel,sam0-adc"

include:
  - name: adc-controller.yaml
  - name: pinctrl-device.yaml
  - name: atmel,assigned-clocks.yaml

io-channel-cells:
  - input
```

这里的 `io-channel-cells: input` 说明 `<&adc 4>` 里的 `4` 表示 ADC 输入编号。通用 ADC 通道的字段说明在它 include 的 `adc-controller.yaml` 里。

一句话总结：先从节点里的 `compatible` 找 binding，再从 binding 判断 overlay 里哪些字段是 Zephyr 认可的。

第七步，找同类官方示例，但只学习结构。

有了 binding 之后，还可以找官方 sample 或 test，看看 Zephyr 项目通常怎么组织这类 overlay。

可以搜索同类 ADC 用法：

```bash
rg -n "io-channels = <&adc|channel@" /Users/mengdu/zephyrproject/zephyr/tests/drivers/adc /Users/mengdu/zephyrproject/zephyr/samples
```

对于 SAMD21，可以看到：

```text
/Users/mengdu/zephyrproject/zephyr/tests/drivers/adc/adc_api/boards/samd21_xpro.overlay
```

这个文件不是因为它和 XIAO 是同一块板子，而是因为它使用同一类 SAMD21 / SAM0 ADC 驱动。我们从它学习 overlay 结构，但具体输入通道仍然用 XIAO 自己的 `A1 -> PA4 -> AIN4` 证据链来确定。

一句话总结：官方示例用来学习写法结构；具体引脚和通道仍然回到自己的板子文件和芯片 pinctrl 文件确认。

第八步，看 Kconfig，理解为什么 `CONFIG_ADC=y` 还不够。

Kconfig 是 Zephyr 的功能开关系统。`prj.conf` 里写的 `CONFIG_ADC=y` 是告诉 Zephyr“我要 ADC 子系统”。但是具体到 SAMD21 的 ADC 驱动，还要看设备树里有没有启用的 `atmel,sam0-adc` 节点。

查 ADC Kconfig：

```bash
rg -n "menuconfig ADC|config ADC_SAM0" /Users/mengdu/zephyrproject/zephyr/drivers/adc
```

可以看到 SAM0 ADC 驱动有：

```kconfig
config ADC_SAM0
	default y
	depends on DT_HAS_ATMEL_SAM0_ADC_ENABLED
```

这句话的意思是：设备树里存在并启用了 `compatible = "atmel,sam0-adc"` 的节点时，`ADC_SAM0` 才会自动打开。也就是说，`prj.conf` 和 `app.overlay` 是配合工作的。

一句话总结：`CONFIG_ADC=y` 打开 ADC 子系统；`&adc { status = "okay"; };` 让具体硬件驱动有机会生效。

如果下次换成别的外设，也按同一个顺序走：

1. 从 `west build -b ...` 或 board `.yaml` 确认 board target。
2. 从 board target 找到开发板目录。
3. 打开板级 `.dts`，看它 include 了哪些 `.dtsi`。
4. 如果问题是板子引脚，先看 connector / pinctrl / 官方 pinout。
5. 如果问题是芯片内部控制器，顺着 SoC `.dtsi` 找节点标签和 `status`。
6. 用节点里的 `compatible` 去 `dts/bindings/` 找字段说明书。
7. 用同类 sample / test 学习结构。
8. 写 overlay 后，用 `build/zephyr/zephyr.dts` 和 `build/zephyr/.config` 反查最终结果。

一句话总结：换外设时，方法不变；变的只是搜索关键词，比如 ADC 换成 I2C、SPI、UART、PWM 或 DAC。

### 8.10 如果现在要自己写 ADC 设备树，完整思路是什么

前面已经学会了怎么找文件。现在把这条查找路径应用到 `analogRead(A1)` 上，得到完整证据链。

第一步，把 Arduino 的 `A1` 翻译成 XIAO 板子的实际引脚。

XIAO SAMD21 的 connector 文件里有：

```dts
gpio-map = <0 0 &porta 2 0>,		/* D0 */
	   <1 0 &porta 4 0>,		/* D1 */
```

对于 XIAO SAMD21，Arduino 示例里的 `A1` 对应板子上的 `D1/A1` 这个脚。connector 文件告诉我们：`D1` 连接到芯片的 `PA4`。

一句话总结：第一步不是写代码，而是先把板子丝印上的 `A1` 找到芯片脚位 `PA4`。

第二步，确认 `PA4` 能不能当 ADC 输入。

XIAO 板级 pinctrl 文件包含了这个头文件：

```dts
#include <dt-bindings/pinctrl/samd21-da1gXabcd-pinctrl.h>
```

这个头文件来自：

```text
/Users/mengdu/zephyrproject/modules/hal/atmel/include/dt-bindings/pinctrl/samd21-da1gXabcd-pinctrl.h
```

里面可以看到：

```c
/* pa4b_adc_ain4 */
#define PA4B_ADC_AIN4 \
	SAM_PINMUX(a, 4, b, periph)
```

这句话可以拆开看：

- `PA4`：芯片的 A 端口第 4 号脚。
- `ADC`：这个脚可以连接到 ADC 外设。
- `AIN4`：这个脚对应 ADC 的模拟输入 4。
- `B`：这个功能走的是芯片的 B 组复用功能。

所以，`A1 -> D1 -> PA4 -> ADC AIN4` 这条链就成立了。

一句话总结：ADC 通道号不是自己编的，是从芯片 pinctrl 定义或芯片手册里查出来的。

第三步，确认 Zephyr 里 ADC 控制器节点叫什么、默认状态是什么。

在 SAMD2x SoC 设备树里有：

```dts
adc: adc@42004000 {
	compatible = "atmel,sam0-adc";
	status = "disabled";
	#io-channel-cells = <1>;
	prescaler = <4>;
};
```

这里得到三个关键信息：

- 控制器名字是 `adc`，所以 overlay 里可以写 `&adc { ... };`。
- `compatible` 是 `atmel,sam0-adc`，说明它用 SAM0 系列 ADC 驱动。
- `status = "disabled";`，说明应用如果要使用 ADC，需要把它改成 `okay`。

一句话总结：`&adc` 这个名字来自 SoC 设备树，`status` 决定它现在能不能被 Zephyr 当成可用设备。

第四步，看 ADC binding，知道 overlay 里能写哪些字段。

ADC binding 在：

```text
/Users/mengdu/zephyrproject/zephyr/dts/bindings/adc/atmel,sam0-adc.yaml
```

它包含：

```yaml
compatible: "atmel,sam0-adc"

include:
  - name: adc-controller.yaml
  - name: pinctrl-device.yaml
  - name: atmel,assigned-clocks.yaml

io-channel-cells:
  - input
```

这里的意思是：`atmel,sam0-adc` 这个 ADC 控制器遵守通用 ADC 控制器规则，也支持 pinctrl 和时钟相关配置。`io-channel-cells` 里的 `input` 表示 `<&adc 4>` 这种写法里的数字 `4` 是“ADC 输入编号”。

通用 ADC 子节点规则在：

```text
/Users/mengdu/zephyrproject/zephyr/dts/bindings/adc/adc-controller.yaml
```

里面规定 ADC 通道子节点可以写：

```yaml
zephyr,gain
zephyr,reference
zephyr,acquisition-time
zephyr,input-positive
zephyr,resolution
```

这些字段分别描述增益、参考电压、采样时间、正输入、分辨率。

一句话总结：binding 文件告诉你设备树字段的“合法菜单”，写 overlay 时要从这里选，不能凭感觉自己编字段。

第五步，找同系列官方示例，看实际写法。

SAMD21 ADC 测试示例可以看：

```text
/Users/mengdu/zephyrproject/zephyr/tests/drivers/adc/adc_api/boards/samd21_xpro.overlay
```

里面的结构是：

```dts
/ {
	zephyr,user {
		io-channels = <&adc 0>;
	};
};

&adc {
	#address-cells = <1>;
	#size-cells = <0>;

	channel@0 {
		reg = <0>;
		zephyr,gain = "ADC_GAIN_1";
		zephyr,reference = "ADC_REF_INTERNAL";
		zephyr,acquisition-time = <ADC_ACQ_TIME_DEFAULT>;
		zephyr,resolution = <12>;
		zephyr,input-positive = <ADC_INPUTCTRL_MUXPOS_SCALEDIOVCC_Val>;
	};
};
```

这个示例读的是芯片内部电压，不是 XIAO 的 `A1` 外部引脚，所以我们不能直接复制 `ADC_INPUTCTRL_MUXPOS_SCALEDIOVCC_Val`。但是它告诉我们通用结构：

- `/ { zephyr,user { io-channels = <&adc ...>; }; };` 用来让应用代码从设备树里拿 ADC 通道。
- `&adc { ... };` 用来给 ADC 控制器补通道配置。
- `channel@...` 用来描述某个 ADC 通道的采样参数。

一句话总结：官方示例提供结构，但具体通道号和输入源仍然要按自己的板子重新判断。

第六步，把 XIAO SAMD21 的 ADC overlay 推出来。

根据前面的来源链，`A1` 对应 `PA4`，`PA4` 对应 `ADC AIN4`。因此，后面我们写 ADC 部分时，overlay 的核心方向会是：

```dts
/ {
	zephyr,user {
		io-channels = <&adc 4>;
	};
};

&adc {
	status = "okay";
	#address-cells = <1>;
	#size-cells = <0>;

	channel@4 {
		reg = <4>;
		zephyr,gain = "ADC_GAIN_1";
		zephyr,reference = "ADC_REF_VDD_1";
		zephyr,acquisition-time = <ADC_ACQ_TIME_DEFAULT>;
		zephyr,resolution = <12>;
		zephyr,input-positive = <4>;
	};
};
```

这段现在先作为“推导结果”理解，下一节我们再正式写进 `app.overlay`，并逐行确认 C 代码会如何读取它。

一句话总结：自己写 ADC 设备树时，最终要回答三个问题：哪个 ADC 控制器、哪个输入通道、这个通道用什么采样参数。

第七步，写完以后用构建产物反查。

设备树 overlay 写完后，不能只看源文件，还要看 Zephyr 合并后的结果。构建后可以检查：

```bash
rg -n "adc|zephyr,user|io-channels" build/zephyr/zephyr.dts
rg -n "CONFIG_ADC|CONFIG_ADC_SAM0" build/zephyr/.config
```

`build/zephyr/zephyr.dts` 是最终合并后的设备树。它像“打印出来的最终硬件地图”，能看到 overlay、板级 DTS、SoC DTS 合并后的真实结果。

`build/zephyr/.config` 是最终 Kconfig 结果。它能告诉你 `CONFIG_ADC=y` 和具体驱动 `CONFIG_ADC_SAM0=y` 是否真的生效。

一句话总结：设备树写完以后，用 `zephyr.dts` 查最终硬件地图，用 `.config` 查最终功能开关。

## 9. 在 `app.overlay` 中加入 ADC 配置

这一节开始正式修改 `app.overlay`。你自己在文件里改，我在这里把每一段该写什么、为什么这么写讲清楚。

当前 `app.overlay` 已经有 USB 虚拟串口控制台。现在要加的是 ADC 输入，也就是 Arduino 示例里的 `analogRead(A1)` 对应的 Zephyr 设备树描述。

一句话总结：这一节的目标是让 Zephyr 知道“我要从 ADC 输入 4 读取电压”。

### 9.1 先打开要修改的文件

在仓库根目录运行：

```bash
sed -n '1,120p' examples/boards/xiao_samd21/dac/app.overlay
```

这个命令只是查看文件，不会修改文件。

- `sed` 是一个文本查看和处理工具。
- `-n` 表示先不自动打印所有行。
- `'1,120p'` 表示打印第 1 到第 120 行。
- 后面的路径就是我们当前示例自己的 overlay 文件。

你应该能看到 USB console 相关内容：

```dts
/ {
	chosen {
		zephyr,console = &cdc_acm_uart0;
	};
};

&zephyr_udc0 {
	cdc_acm_uart0: cdc_acm_uart0 {
		compatible = "zephyr,cdc-acm-uart";
		label = "CDC_ACM_0";
	};
};
```

一句话总结：先确认你要改的是应用自己的 `app.overlay`，不是 Zephyr 源码里的板级 `.dts`。

### 9.2 在文件顶部加入 ADC 宏头文件

把下面这一行加到 SPDX 注释后面：

```dts
#include <zephyr/dt-bindings/adc/adc.h>
```

加完以后，文件开头应该类似这样：

```dts
/*
 * SPDX-License-Identifier: Apache-2.0
 */

#include <zephyr/dt-bindings/adc/adc.h>
```

这一行的作用是把 ADC 相关的设备树宏引进来。宏可以理解成“有名字的固定值”。后面我们会写：

```dts
zephyr,acquisition-time = <ADC_ACQ_TIME_DEFAULT>;
```

其中 `ADC_ACQ_TIME_DEFAULT` 就来自：

```text
/Users/mengdu/zephyrproject/zephyr/include/zephyr/dt-bindings/adc/adc.h
```

它的定义是：

```c
#define ADC_ACQ_TIME_DEFAULT 0
```

这里写宏名比直接写 `0` 更容易读。看到 `ADC_ACQ_TIME_DEFAULT`，你能知道它表示“使用 ADC 默认采样时间”。

一句话总结：`#include <zephyr/dt-bindings/adc/adc.h>` 是为了让 overlay 能使用 ADC 相关的名字，比如 `ADC_ACQ_TIME_DEFAULT`。

### 9.3 在根节点里加入 `zephyr,user`

你当前已经有一个根节点：

```dts
/ {
	chosen {
		zephyr,console = &cdc_acm_uart0;
	};
};
```

我们要把它扩展成：

```dts
/ {
	chosen {
		zephyr,console = &cdc_acm_uart0;
	};

	zephyr,user {
		io-channels = <&adc 4>;
	};
};
```

逐行看：

```dts
/ {
```

这表示设备树的根节点。可以把它理解成“整张硬件地图的最外层”。

```dts
chosen {
	zephyr,console = &cdc_acm_uart0;
};
```

这是之前 USB 串口控制台用的内容，保留不变。它告诉 Zephyr：程序里的打印输出走 `cdc_acm_uart0`。

```dts
zephyr,user {
	io-channels = <&adc 4>;
};
```

这是我们新加的 ADC 使用入口。

`zephyr,user` 是 Zephyr 示例里常用的应用自定义节点。它本身不是一个真实芯片外设，更像是应用放配置的“便签”。后面写 C 代码时，可以通过 `DT_PATH(zephyr_user)` 找到这张便签。

`io-channels` 表示“这个应用要用哪些输入/输出通道”。对于 ADC 来说，它常用来列出要读取的 ADC 通道。

`<&adc 4>` 分成两部分：

- `&adc`：引用 SoC 设备树里的 ADC 控制器节点。
- `4`：ADC 输入编号，也就是前面从 `A1 -> PA4 -> ADC AIN4` 推出来的输入 4。

一句话总结：`zephyr,user` 这段是在告诉后面的 C 代码：本示例要读 `adc` 控制器的输入 4。

### 9.4 在文件末尾加入 `&adc` 配置

接下来在 `app.overlay` 末尾加入：

```dts
&adc {
	status = "okay";
	#address-cells = <1>;
	#size-cells = <0>;

	channel@4 {
		reg = <4>;
		zephyr,gain = "ADC_GAIN_1";
		zephyr,reference = "ADC_REF_VDD_1";
		zephyr,acquisition-time = <ADC_ACQ_TIME_DEFAULT>;
		zephyr,resolution = <12>;
		zephyr,input-positive = <4>;
	};
};
```

逐行看。

```dts
&adc {
```

`&adc` 表示引用已经存在的 ADC 节点。这个节点不是我们新建的，它来自：

```text
/Users/mengdu/zephyrproject/zephyr/dts/arm/atmel/samd2x.dtsi
```

里面的标签是：

```dts
adc: adc@42004000
```

设备树里 `adc:` 是定义名字，`&adc` 是引用名字。

一句话总结：`&adc` 是在修改芯片里已经存在的 ADC 控制器节点。

```dts
status = "okay";
```

SoC 文件里 ADC 默认是：

```dts
status = "disabled";
```

应用要用它，就要在 overlay 里把状态改成 `okay`。`okay` 可以理解成“这次构建里启用这个硬件”。

一句话总结：`status = "okay";` 是把 ADC 从“存在但关闭”改成“本应用启用”。

```dts
#address-cells = <1>;
#size-cells = <0>;
```

这两行是为了下面的 `channel@4` 子节点服务的。

`#address-cells = <1>;` 表示子节点地址用 1 个数字描述。这里的子节点地址就是通道号，比如 `4`。

`#size-cells = <0>;` 表示子节点不需要描述大小。ADC 通道不是一段内存空间，所以这里是 `0`。

一句话总结：这两行是在告诉设备树解析器：ADC 子节点用通道号当地址，不需要大小字段。

```dts
channel@4 {
```

这是 ADC 通道 4 的配置节点。`@4` 表示这个节点的地址是 4，对应下面的 `reg = <4>;`。

ADC binding 里要求 ADC 通道子节点使用 `channel` 这个名字，所以这里写成 `channel@4`。

一句话总结：`channel@4` 是在描述 ADC 输入 4 这个通道怎么采样。

```dts
reg = <4>;
```

`reg` 是这个子节点的编号。这里写 `4`，和 `channel@4` 里的 `4` 对应，也和 `io-channels = <&adc 4>;` 里的 `4` 对应。

一句话总结：`reg = <4>;` 表示这个通道节点就是 ADC 通道 4。

```dts
zephyr,gain = "ADC_GAIN_1";
```

`gain` 是增益。可以先理解成“读到的电压要不要在 ADC 内部放大或缩小”。

`ADC_GAIN_1` 表示 1 倍，也就是不放大、不缩小。我们读取的是 0 到 3.3V 之间的普通电压，所以先用 1 倍。

一句话总结：`ADC_GAIN_1` 表示按原始比例读取电压。

```dts
zephyr,reference = "ADC_REF_VDD_1";
```

`reference` 是参考电压。ADC 读电压时，需要一个“满分标准”。

`ADC_REF_VDD_1` 表示用芯片供电电压 VDD 作为参考。XIAO SAMD21 通常按 3.3V 逻辑工作，所以这和 Arduino 示例里用 `3.3 / 4096.0` 换算电压的思路一致。

一句话总结：`ADC_REF_VDD_1` 表示 ADC 的满量程参考电压来自板子的 VDD。

```dts
zephyr,acquisition-time = <ADC_ACQ_TIME_DEFAULT>;
```

`acquisition-time` 是采样保持时间。通俗讲，就是 ADC 在真正转换之前，给输入电压一点时间稳定下来。

`ADC_ACQ_TIME_DEFAULT` 表示使用驱动默认值。这个值来自前面 include 的 ADC dt-bindings 头文件。

一句话总结：这行表示采样时间先使用驱动默认设置。

```dts
zephyr,resolution = <12>;
```

`resolution` 是 ADC 分辨率。Arduino 示例里有：

```cpp
analogReadResolution(12);
```

所以 Zephyr 这里也写 `12`。12 位 ADC 的结果范围通常是 `0` 到 `4095`，一共有 4096 个等级。

一句话总结：`zephyr,resolution = <12>;` 对应 Arduino 的 `analogReadResolution(12)`。

```dts
zephyr,input-positive = <4>;
```

`input-positive` 是 ADC 的正输入选择。SAMD21 的 ADC 驱动会用这个数字去设置硬件里的输入选择寄存器。

我们前面查到 `PA4` 对应 `ADC AIN4`，所以这里写 `4`。

一句话总结：`zephyr,input-positive = <4>;` 表示真正采样的外部输入是 AIN4，也就是 XIAO 的 A1/D1。

### 9.5 这一节完成后，`app.overlay` 应该长什么样

你最终应该把 `app.overlay` 整理成类似这样：

```dts
/*
 * SPDX-License-Identifier: Apache-2.0
 */

#include <zephyr/dt-bindings/adc/adc.h>

/ {
	chosen {
		zephyr,console = &cdc_acm_uart0;
	};

	zephyr,user {
		io-channels = <&adc 4>;
	};
};

&zephyr_udc0 {
	cdc_acm_uart0: cdc_acm_uart0 {
		compatible = "zephyr,cdc-acm-uart";
		label = "CDC_ACM_0";
	};
};

&adc {
	status = "okay";
	#address-cells = <1>;
	#size-cells = <0>;

	channel@4 {
		reg = <4>;
		zephyr,gain = "ADC_GAIN_1";
		zephyr,reference = "ADC_REF_VDD_1";
		zephyr,acquisition-time = <ADC_ACQ_TIME_DEFAULT>;
		zephyr,resolution = <12>;
		zephyr,input-positive = <4>;
	};
};
```

一句话总结：这个文件现在同时做两件事：把打印输出接到 USB 串口，把 ADC 输入 4 暴露给应用代码。

### 9.6 修改后先做文本检查

改完后先运行：

```bash
sed -n '1,160p' examples/boards/xiao_samd21/dac/app.overlay
```

你要检查四件事：

1. 顶部有 `#include <zephyr/dt-bindings/adc/adc.h>`。
2. 根节点 `/ { ... };` 里同时有 `chosen` 和 `zephyr,user`。
3. `io-channels = <&adc 4>;` 里的数字是 `4`。
4. 文件末尾有 `&adc { ... channel@4 { ... }; };`。

一句话总结：先用文本检查确认结构完整，再进入构建验证。

### 9.7 下一步要验证什么

这一节只是写设备树。写完以后，下一步不是马上写 `main.c`，而是先构建一次，查看 Zephyr 合并后的结果。

构建后重点看两个文件：

```text
build/zephyr/zephyr.dts
build/zephyr/.config
```

`zephyr.dts` 用来确认最终设备树里 ADC 已经是 `okay`，并且 `zephyr,user` 里有 `io-channels = <&adc 4>`。

`.config` 用来确认 `CONFIG_ADC=y` 和 `CONFIG_ADC_SAM0=y` 是否生效。

一句话总结：源码里的 overlay 是你写的意图，`build/zephyr/zephyr.dts` 才是 Zephyr 最终接受的硬件地图。

## 10. 构建并反查设备树结果

上一节你已经把 ADC 配置写进 `app.overlay`。这一节不写新代码，先做一次构建，目的只有一个：确认 Zephyr 最终合并出来的设备树和 Kconfig 结果符合预期。

一句话总结：写完 overlay 以后，第一件事是构建并检查生成文件，而不是马上写 `main.c`。

### 10.1 为什么这次构建命令不直接写 `west build`

如果当前终端已经激活 Zephyr 环境，可以直接使用 `west`。如果终端提示：

```text
command not found: west
```

说明当前 shell 没有把 Zephyr 虚拟环境加入 `PATH`。

本机可以直接使用 Zephyr 虚拟环境里的 `west`：

```text
/Users/mengdu/zephyrproject/.venv/bin/west
```

这不是另一个构建工具，只是 `west` 的完整路径。使用完整路径的好处是：即使当前终端没有配置好 `PATH`，命令也能准确找到 `west`。

一句话总结：`/Users/mengdu/zephyrproject/.venv/bin/west` 就是本机 Zephyr 环境里的 `west` 命令。

### 10.2 运行构建命令

在任意目录都可以运行下面这条命令：

```bash
/Users/mengdu/zephyrproject/.venv/bin/west build \
  -b seeeduino_xiao \
  -s /Users/mengdu/Desktop/Seeed-Zephyr-Project/examples/boards/xiao_samd21/dac \
  -d /Users/mengdu/Desktop/Seeed-Zephyr-Project/build/xiao_samd21_dac \
  -p always
```

逐段解释：

```bash
/Users/mengdu/zephyrproject/.venv/bin/west build
```

调用 Zephyr 的构建命令。`west` 是 Zephyr 推荐的项目管理和构建入口。

```bash
-b seeeduino_xiao
```

指定 board target。也就是告诉 Zephyr：这次固件是给 `seeeduino_xiao` 这块板子构建的。

```bash
-s /Users/mengdu/Desktop/Seeed-Zephyr-Project/examples/boards/xiao_samd21/dac
```

指定应用源码目录。`-s` 是 source 的意思，告诉 Zephyr：当前应用在这个目录里。

```bash
-d /Users/mengdu/Desktop/Seeed-Zephyr-Project/build/xiao_samd21_dac
```

指定构建输出目录。`-d` 是 build directory 的意思，告诉 Zephyr：生成文件统一放到这里。

```bash
-p always
```

要求重新生成构建目录。这样可以确保刚刚修改过的 overlay 被重新解析。

一句话总结：这条命令明确告诉 Zephyr 三件事：给哪块板子构建、源码在哪里、生成文件放哪里。

### 10.3 构建成功时要看到什么

构建成功时，输出里应该能看到类似内容：

```text
-- Found BOARD.dts: /Users/mengdu/zephyrproject/zephyr/boards/seeed/seeeduino_xiao/seeeduino_xiao.dts
-- Found devicetree overlay: /Users/mengdu/Desktop/Seeed-Zephyr-Project/examples/boards/xiao_samd21/dac/app.overlay
-- Generated zephyr.dts: /Users/mengdu/Desktop/Seeed-Zephyr-Project/build/xiao_samd21_dac/zephyr/zephyr.dts
Configuration saved to '/Users/mengdu/Desktop/Seeed-Zephyr-Project/build/xiao_samd21_dac/zephyr/.config'
```

这几行分别说明：

- Zephyr 找到了板级设备树 `seeeduino_xiao.dts`。
- Zephyr 找到了你的应用 overlay：`app.overlay`。
- Zephyr 生成了最终合并设备树：`zephyr.dts`。
- Zephyr 生成了最终 Kconfig 配置：`.config`。

构建最后还会生成固件文件，例如：

```text
zephyr.elf
zephyr.uf2
```

`zephyr.uf2` 后面可以用于烧录到 XIAO SAMD21。

一句话总结：构建成功不仅说明 C 代码能编译，也说明设备树语法已经被 Zephyr 接受。

### 10.4 反查最终设备树

运行：

```bash
rg -n "zephyr,user|io-channels|adc@42004000|channel@4|input-positive" \
  /Users/mengdu/Desktop/Seeed-Zephyr-Project/build/xiao_samd21_dac/zephyr/zephyr.dts
```

这个命令是在最终合并设备树里搜索 ADC 相关内容。

你应该能看到类似结果：

```text
adc: xiao_adc: adc@42004000 {
	status = "okay";

	channel@4 {
		reg = < 0x4 >;
		zephyr,resolution = < 0xc >;
		zephyr,input-positive = < 0x4 >;
	};
};

zephyr,user {
	io-channels = < &adc 0x4 >;
};
```

这里有两个细节要看懂。

第一，`adc: xiao_adc: adc@42004000` 表示这个节点现在同时有两个标签：`adc` 和 `xiao_adc`。`adc` 来自 SoC 设备树，`xiao_adc` 来自 XIAO connector 文件。

第二，`0x4` 和 `0xc` 是十六进制写法。十六进制可以理解成计算机常用的另一种数字写法：

- `0x4` 等于十进制的 `4`。
- `0xc` 等于十进制的 `12`。

所以：

```dts
zephyr,resolution = < 0xc >;
```

就是你在 overlay 里写的：

```dts
zephyr,resolution = <12>;
```

一句话总结：`zephyr.dts` 里出现 `status = "okay"`、`channel@4`、`io-channels = <&adc 0x4>`，说明 ADC 设备树已经合并成功。

### 10.5 反查最终 Kconfig

运行：

```bash
rg -n "CONFIG_ADC|CONFIG_ADC_SAM0|CONFIG_DAC|CONFIG_DAC_SAM0" \
  /Users/mengdu/Desktop/Seeed-Zephyr-Project/build/xiao_samd21_dac/zephyr/.config
```

你应该能看到：

```text
CONFIG_ADC=y
CONFIG_ADC_CONFIGURABLE_INPUTS=y
CONFIG_ADC_SAM0=y
CONFIG_DAC=y
CONFIG_DAC_SAM0=y
```

这些配置说明：

- `CONFIG_ADC=y`：ADC 子系统已经打开。
- `CONFIG_ADC_SAM0=y`：SAMD21 使用的 SAM0 ADC 驱动已经打开。
- `CONFIG_ADC_CONFIGURABLE_INPUTS=y`：ADC 驱动支持 `zephyr,input-positive` 这种输入选择配置。
- `CONFIG_DAC=y`：DAC 子系统已经打开。
- `CONFIG_DAC_SAM0=y`：SAMD21 使用的 SAM0 DAC 驱动已经打开。

一句话总结：`.config` 证明“功能开关”和“具体芯片驱动”都已经生效。

### 10.6 这一阶段的结论

现在可以确认三件事：

1. `app.overlay` 的语法能被 Zephyr 接受。
2. ADC 节点最终已经从 `disabled` 变成 `okay`。
3. SAM0 ADC 驱动已经启用，后面的 C 代码可以开始使用 ADC API。

一句话总结：设备树和配置层已经准备好，下一步才进入 `main.c`，开始把 Arduino 的 `analogWrite()` 和 `analogRead()` 翻译成 Zephyr C API。

## 11. 写最小 `main.c`，先确认程序入口和 USB 输出

设备树和 Kconfig 已经验证通过。现在进入 C 代码，但先不写 DAC 和 ADC。第一步只做一个最小程序：启动 USB 设备栈，然后用 `printk()` 每秒打印一行文字。

为什么先做这个？因为 DAC/ADC 代码后面都需要通过串口看输出。如果最基础的 USB console 还没确认，后面读不到 ADC 数据时，就很难判断是 ADC 错了，还是打印通道没通。

一句话总结：先确认“程序能启动、USB 能输出”，再写真正的 DAC/ADC 逻辑。

### 11.1 当前 `main.c` 为什么要先简化

当前 `main.c` 还是从 `blinky` 复制来的，里面有 LED 和 GPIO 逻辑。DAC 示例最终不依赖 LED 闪烁，所以这一节先把它简化掉。

这一步不是最终功能，只是建立一个干净入口。可以把它理解成“先确认房子的大门能打开，再往里面搬家具”。

一句话总结：把 blinky 逻辑清掉，是为了让后面的 DAC/ADC 代码从一个干净主程序开始。

### 11.2 替换 `src/main.c`

打开：

```text
examples/boards/xiao_samd21/dac/src/main.c
```

把内容替换成：

```c
#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>
#include <zephyr/usb/usb_device.h>

#define HEARTBEAT_INTERVAL_MS 1000

int main(void)
{
	int ret;

	ret = usb_enable(NULL);
	if (ret != 0) {
		printk("USB device initialization failed: %d\n", ret);
		return 0;
	}

	printk("XIAO SAMD21 DAC example started\n");

	while (1) {
		printk("Console heartbeat\n");
		k_msleep(HEARTBEAT_INTERVAL_MS);
	}

	return 0;
}
```

一句话总结：这份 `main.c` 只做一件事：启动 USB console，然后持续打印文字。

### 11.3 逐行理解这份代码

```c
#include <zephyr/kernel.h>
```

引入 Zephyr 内核 API。这里主要用到 `k_msleep()`，它的作用是让当前程序暂停一段时间。

一句话总结：`kernel.h` 提供 Zephyr 的基础系统能力，比如延时。

```c
#include <zephyr/sys/printk.h>
```

引入 `printk()`。它和 Arduino 里的 `Serial.println()` 作用相近，都是把文字输出到控制台。

一句话总结：`printk()` 是 Zephyr 里最基础的打印函数。

```c
#include <zephyr/usb/usb_device.h>
```

引入 USB device API。这里主要用到 `usb_enable()`，它负责启动 USB 设备栈。

一句话总结：`usb_device.h` 让程序可以手动启动 USB 设备功能。

```c
#define HEARTBEAT_INTERVAL_MS 1000
```

定义一个常量，表示 heartbeat 打印间隔是 1000 毫秒，也就是 1 秒。

`heartbeat` 可以理解成“心跳包”。程序每秒打印一次，说明它还在运行。

一句话总结：这个常量控制每隔多久打印一次状态信息。

```c
int main(void)
```

这是程序入口。Zephyr 启动完成后，会调用这里的 `main()`。

一句话总结：`main()` 就是应用代码开始执行的地方。

```c
int ret;
```

定义一个整数变量，用来接收函数返回值。Zephyr 里的很多函数会返回 `0` 表示成功，返回负数或非零值表示失败。

一句话总结：`ret` 用来判断某一步有没有成功。

```c
ret = usb_enable(NULL);
```

启动 USB 设备栈。因为 `prj.conf` 里写了：

```conf
CONFIG_USB_DEVICE_INITIALIZE_AT_BOOT=n
```

所以 USB 不会在系统启动时自动初始化。我们需要在 `main()` 里手动调用 `usb_enable(NULL)`。

一句话总结：`usb_enable(NULL)` 是让电脑能看到这个 USB 设备的启动动作。

```c
if (ret != 0) {
	printk("USB device initialization failed: %d\n", ret);
	return 0;
}
```

检查 USB 启动是否成功。如果失败，就打印错误码并结束主程序。

一句话总结：这段是在检查 USB 是否启动失败。

```c
printk("XIAO SAMD21 DAC example started\n");
```

打印启动信息。看到这行，说明 `main()` 已经跑起来，而且 USB console 能输出文字。

一句话总结：这行是程序启动成功的可见信号。

```c
while (1) {
	printk("Console heartbeat\n");
	k_msleep(HEARTBEAT_INTERVAL_MS);
}
```

这是无限循环。嵌入式程序通常不会自然退出，而是一直运行。

循环里每秒打印一次 `Console heartbeat`。如果你在串口里持续看到这行，说明程序没有卡死。

一句话总结：这个循环用每秒一行打印证明程序还活着。

### 11.4 构建验证

改完后重新构建：

```bash
/Users/mengdu/zephyrproject/.venv/bin/west build \
  -b seeeduino_xiao \
  -s /Users/mengdu/Desktop/Seeed-Zephyr-Project/examples/boards/xiao_samd21/dac \
  -d /Users/mengdu/Desktop/Seeed-Zephyr-Project/build/xiao_samd21_dac \
  -p always
```

如果构建成功，说明这份最小 `main.c` 的语法和依赖都没有问题。

一句话总结：这一步只验证 C 代码能编译，还不验证板子上的运行结果。

### 11.5 烧录和串口预期结果

构建成功后，会生成：

```text
/Users/mengdu/Desktop/Seeed-Zephyr-Project/build/xiao_samd21_dac/zephyr/zephyr.uf2
```

把它烧录到 XIAO SAMD21 后，打开串口，预期能看到：

```text
XIAO SAMD21 DAC example started
Console heartbeat
Console heartbeat
Console heartbeat
```

如果能看到这些文字，说明三件事成立：

1. `main()` 已经运行。
2. USB device 已经启动。
3. `printk()` 已经通过 USB console 输出到电脑。

一句话总结：看到 heartbeat，才说明后面打印 ADC 电压有可靠输出通道。

### 11.6 下一步做什么

下一步才开始引入 DAC API。我们会先让 DAC 输出一个固定电压，比如中间值，然后再逐步改成正弦波。

一句话总结：先固定输出，再动态输出；先让一件事工作，再叠加复杂逻辑。

## 12. 加入 DAC，先输出一个固定电压

这一节开始真正使用 DAC。

DAC 的全称是 Digital-to-Analog Converter，中文可以叫“数字转模拟转换器”。大白话说：程序里写的是一个数字，比如 `512`；DAC 会把这个数字变成一个真实电压。

一句话总结：DAC 就是把程序里的数字变成引脚上的电压。

### 12.1 这一步要做什么

先不要直接写正弦波。我们先让 XIAO SAMD21 的 A0/D0 输出一个固定的中间值。

原因很简单：如果固定值都输出不了，后面正弦波也一定不可靠。固定值更容易测量，也更容易排查。

这一节的目标是：

1. 让程序找到 Zephyr 里的 DAC 设备。
2. 配置 DAC 通道。
3. 向 DAC 写入一个固定数值 `512`。
4. 用万用表测 A0/D0 和 GND 之间的电压。按当前默认 DAC 参考源，`512` 的预期电压接近 `0.5V`。

一句话总结：这一步只验证“DAC 能不能输出电压”。

### 12.2 这些值从哪里来

我们这一步会用到三个核心值：

```c
#define DAC_NODE DT_NODELABEL(dac0)
#define DAC_CHANNEL_ID 0
#define DAC_RESOLUTION 10
```

它们不是随便编的，来源分别是：

`dac0` 来自 Zephyr 的设备树。XIAO SAMD21 的板级设备树文件是：

```text
/Users/mengdu/zephyrproject/zephyr/boards/seeed/seeeduino_xiao/seeeduino_xiao.dts
```

里面已经有：

```dts
&dac0 {
	status = "okay";

	pinctrl-0 = <&dac_default>;
	pinctrl-names = "default";
};
```

这表示 XIAO SAMD21 这块板子的 DAC 控制器已经启用。

一句话总结：`dac0` 是 Zephyr 给 SAMD21 DAC 控制器起的设备树名字。

`DAC_CHANNEL_ID 0` 来自 SAMD21 的 DAC 驱动。驱动文件是：

```text
/Users/mengdu/zephyrproject/zephyr/drivers/dac/dac_sam0.c
```

里面的检查逻辑要求：

```c
if (channel_cfg->channel_id != 0) {
	return -EINVAL;
}
```

这说明 SAMD21 这颗芯片的 DAC 通道编号只能用 `0`。

一句话总结：SAMD21 只有一个 DAC 输出通道，所以通道编号是 `0`。

`DAC_RESOLUTION 10` 也来自同一个驱动文件：

```c
if (channel_cfg->resolution != 10) {
	return -ENOTSUP;
}
```

这说明 Zephyr 的 SAMD21 DAC 驱动只接受 10-bit 分辨率。

10-bit 的意思是：可用数字范围是 `0` 到 `1023`，一共有 `1024` 个档位。

一句话总结：XIAO SAMD21 的 DAC 在这里按 10-bit 使用，数值范围是 `0` 到 `1023`。

### 12.3 为什么输出脚是 A0/D0

XIAO 的连接器映射文件是：

```text
/Users/mengdu/zephyrproject/zephyr/boards/seeed/seeeduino_xiao/seeed_xiao_connector.dtsi
```

里面写了：

```dts
gpio-map = <0 0 &porta 2 0>,		/* D0 */
```

这表示 XIAO 的 D0 对应 SAMD21 芯片的 `PA2`。

然后 pinctrl 文件是：

```text
/Users/mengdu/zephyrproject/zephyr/boards/seeed/seeeduino_xiao/seeeduino_xiao-pinctrl.dtsi
```

里面写了：

```dts
dac_default: dac_default {
	group1 {
		pinmux = <PA2B_DAC_VOUT>;
	};
};
```

这表示 `PA2` 这个芯片脚可以切换成 `DAC_VOUT`，也就是 DAC 电压输出。

把两条信息连起来看：

1. XIAO 的 D0 是 SAMD21 的 `PA2`。
2. SAMD21 的 `PA2` 可以作为 `DAC_VOUT`。
3. 所以 XIAO 的 D0/A0 就是 DAC 输出脚。

一句话总结：D0/A0 不是猜的，是由 XIAO 连接器映射和 SAMD21 pinctrl 一起证明出来的。

### 12.4 替换 main.c

现在把 `examples/boards/xiao_samd21/dac/src/main.c` 替换成下面这份代码：

```c
#include <zephyr/device.h>
#include <zephyr/drivers/dac.h>
#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>
#include <zephyr/usb/usb_device.h>

#define HEARTBEAT_INTERVAL_MS 1000
#define DAC_NODE DT_NODELABEL(dac0)
#define DAC_CHANNEL_ID 0
#define DAC_RESOLUTION 10
#define DAC_MID_VALUE 512

static const struct device *const dac_dev = DEVICE_DT_GET(DAC_NODE);

static const struct dac_channel_cfg dac_cfg = {
	.channel_id = DAC_CHANNEL_ID,
	.resolution = DAC_RESOLUTION,
};

int main(void)
{
	int ret;

	ret = usb_enable(NULL);
	if (ret != 0) {
		printk("USB device initialization failed: %d\n", ret);
		return 0;
	}

	printk("XIAO SAMD21 DAC example started\n");

	if (!device_is_ready(dac_dev)) {
		printk("DAC device is not ready\n");
		return 0;
	}

	ret = dac_channel_setup(dac_dev, &dac_cfg);
	if (ret != 0) {
		printk("DAC channel setup failed: %d\n", ret);
		return 0;
	}

	ret = dac_write_value(dac_dev, DAC_CHANNEL_ID, DAC_MID_VALUE);
	if (ret != 0) {
		printk("DAC write failed: %d\n", ret);
		return 0;
	}

	printk("DAC fixed output value: %u\n", DAC_MID_VALUE);

	while (1) {
		printk("DAC output is holding value: %u\n", DAC_MID_VALUE);
		k_msleep(HEARTBEAT_INTERVAL_MS);
	}

	return 0;
}
```

一句话总结：这份代码会启动 USB 输出，然后让 DAC 在 A0/D0 上保持输出 `512`。

### 12.5 逐段解释 main.c

```c
#include <zephyr/device.h>
```

引入 Zephyr 的设备模型。

设备模型可以理解成 Zephyr 的“设备通讯录”。ADC、DAC、UART、GPIO 这些硬件外设，都会在这个通讯录里登记。程序要用某个硬件，就先从这里拿到它。

一句话总结：`device.h` 让程序能拿到 Zephyr 里的硬件设备对象。

```c
#include <zephyr/drivers/dac.h>
```

引入 DAC 驱动 API。

API 可以理解成“别人写好的工具按钮”。我们不用自己操作芯片寄存器，只需要调用 `dac_channel_setup()` 和 `dac_write_value()`。

一句话总结：`dac.h` 提供了使用 DAC 的函数。

```c
#define DAC_NODE DT_NODELABEL(dac0)
```

`DT_NODELABEL(dac0)` 的意思是：从设备树里找名字叫 `dac0` 的节点。

设备树可以理解成“硬件说明书”。`dac0` 就是说明书里登记的 DAC 控制器。

一句话总结：这一行告诉 C 代码去设备树里找 DAC 控制器。

```c
#define DAC_CHANNEL_ID 0
#define DAC_RESOLUTION 10
#define DAC_MID_VALUE 512
```

`DAC_CHANNEL_ID 0` 表示使用第 0 个 DAC 通道。

`DAC_RESOLUTION 10` 表示 DAC 使用 10-bit 分辨率。

`DAC_MID_VALUE 512` 是要输出的数值。10-bit 的范围是 `0` 到 `1023`，`512` 大约在中间。

当前代码没有单独配置 DAC 的参考电压。SAMD21 DAC 驱动默认使用内部参考源，`512` 的输出电压会接近 `0.5V`。这就是当前教程继续使用的稳定基线。

一句话总结：这三行定义了“用哪个 DAC、按多少位输出、输出多大的值”。

```c
static const struct device *const dac_dev = DEVICE_DT_GET(DAC_NODE);
```

这行会根据设备树节点拿到 DAC 设备对象。

可以把它理解成：我们已经知道通讯录里有个叫 `dac0` 的设备，现在把它的联系方式取出来，后面调用 DAC 函数时要用。

一句话总结：`dac_dev` 是后面操作 DAC 时要传进去的设备对象。

```c
static const struct dac_channel_cfg dac_cfg = {
	.channel_id = DAC_CHANNEL_ID,
	.resolution = DAC_RESOLUTION,
};
```

这是 DAC 通道配置。

`struct dac_channel_cfg` 是 Zephyr 定义好的结构体。结构体可以理解成“一张表格”，里面每一项都是配置字段。

这里填了两个字段：

1. `.channel_id`：使用哪个 DAC 通道。
2. `.resolution`：使用多少 bit 的输出分辨率。

一句话总结：`dac_cfg` 是给 DAC 通道的配置表。

```c
if (!device_is_ready(dac_dev)) {
	printk("DAC device is not ready\n");
	return 0;
}
```

这段检查 DAC 设备是否已经准备好。

设备树里写了 `status = "okay"`，表示这个设备可以参与构建；但程序运行时，还要确认驱动初始化是否成功。

一句话总结：设备树说“可以用”，`device_is_ready()` 检查“现在真的准备好了没有”。

```c
ret = dac_channel_setup(dac_dev, &dac_cfg);
```

这行把前面的 `dac_cfg` 应用到 DAC 通道。

`&dac_cfg` 里的 `&` 表示“把这张配置表的位置告诉函数”。函数拿到位置后，就能读到里面的 `channel_id` 和 `resolution`。

一句话总结：`dac_channel_setup()` 是正式配置 DAC 通道。

```c
ret = dac_write_value(dac_dev, DAC_CHANNEL_ID, DAC_MID_VALUE);
```

这行向 DAC 写入数值 `512`。

如果把 DAC 想成一个电子音量旋钮，`0` 是最低，`1023` 是最高，`512` 就是大约旋到一半。

一句话总结：`dac_write_value()` 是真正让 A0/D0 输出电压的动作。

```c
while (1) {
	printk("DAC output is holding value: %u\n", DAC_MID_VALUE);
	k_msleep(HEARTBEAT_INTERVAL_MS);
}
```

DAC 写入一次后会保持输出。这里的循环不是反复写 DAC，而是每秒打印一次状态，方便你确认程序还在运行。

一句话总结：循环用来持续告诉电脑“程序还活着，DAC 还保持这个值”。

### 12.6 构建命令

改完后重新构建：

```bash
/Users/mengdu/zephyrproject/.venv/bin/west build \
  -b seeeduino_xiao \
  -s /Users/mengdu/Desktop/Seeed-Zephyr-Project/examples/boards/xiao_samd21/dac \
  -d /Users/mengdu/Desktop/Seeed-Zephyr-Project/build/xiao_samd21_dac \
  -p always
```

这个命令前面已经用过，这里再解释一次：

`west build` 是 Zephyr 的构建命令。

`-b seeeduino_xiao` 表示目标板子是 XIAO SAMD21。

`-s .../dac` 表示源码目录是我们正在写的 `dac` 示例。

`-d .../build/xiao_samd21_dac` 表示把构建产物放到这个目录。

`-p always` 表示每次都重新整理构建目录，减少旧配置影响新结果。

一句话总结：这条命令把 `dac` 示例编译成可以烧录到 XIAO SAMD21 的固件。

### 12.7 烧录和测量

构建成功后，UF2 文件在：

```text
/Users/mengdu/Desktop/Seeed-Zephyr-Project/build/xiao_samd21_dac/zephyr/zephyr.uf2
```

把它烧录进 XIAO SAMD21。

然后用万用表测量：

1. 黑表笔接 `GND`。
2. 红表笔接 `A0/D0`。
3. 预期电压接近 `0.5V`。

同时打开串口，预期能看到：

```text
XIAO SAMD21 DAC example started
DAC fixed output value: 512
DAC output is holding value: 512
DAC output is holding value: 512
```

如果串口有输出，并且 A0/D0 接近 `0.5V`，说明这一步是成功的。

一句话总结：这一节成功的标志是串口打印正常，并且 A0/D0 能测到接近 `0.5V` 的电压。

### 12.8 下一步做什么

下一步先学习 DAC 参考电压。你已经验证到：保持默认 DAC 参考源时，USB 输出稳定，A0/D0 能稳定输出接近 `0.5V`。

接下来我们会沿着这个稳定基线继续做波形。先让电压在默认参考范围内动起来，再考虑更复杂的参考电压配置。

一句话总结：先沿着稳定基线继续做功能，再研究更复杂的参考源。

## 13. 理解 DAC 参考电压，并保持稳定基线

你测到 `0.5V`，这不是失败。它说明程序确实写进了 DAC，而且当前 DAC 使用的是内部参考电压。

参考电压可以理解成“DAC 的最高刻度”。如果最高刻度大约是 `1V`，那么 10-bit 中间值 `512` 就会接近 `0.5V`。

一句话总结：同样写 `512`，最终电压是多少，取决于 DAC 的参考电压是多少。

### 13.1 为什么现在是 0.5V

SAMD21 DAC 驱动文件是：

```text
/Users/mengdu/zephyrproject/zephyr/drivers/dac/dac_sam0.c
```

里面有参考源映射：

```c
#define SAM0_DAC_REFSEL_0 DAC_CTRLB_REFSEL_INT1V_Val
#define SAM0_DAC_REFSEL_1 DAC_CTRLB_REFSEL_AVCC_Val
#define SAM0_DAC_REFSEL_2 DAC_CTRLB_REFSEL_VREFP_Val
```

这三行表示：

1. 第 0 种参考源是内部 `1V` 参考。
2. 第 1 种参考源是 `AVCC`，也就是芯片的模拟供电。
3. 第 2 种参考源是外部参考输入。

驱动里还有：

```c
#define SAM0_DAC_REFSEL(n) \
	COND_CODE_1(DT_INST_NODE_HAS_PROP(n, reference), \
		    (DT_INST_ENUM_IDX(n, reference)), (0))
```

这段的意思是：如果设备树里写了 `reference` 属性，就用设备树指定的参考源；如果没有写，就用默认值 `0`。

默认值 `0` 对应上面的 `INT1V`，所以 `512` 输出接近 `0.5V` 是合理结果。

一句话总结：现在是 `0.5V`，因为设备树没有写 DAC reference，驱动默认用了内部约 `1V` 参考源。

### 13.2 去哪里看 reference 可以写什么

DAC 的设备树绑定文件是：

```text
/Users/mengdu/zephyrproject/zephyr/dts/bindings/dac/atmel,sam0-dac.yaml
```

里面定义了 `reference` 允许写的值：

```yaml
reference:
  type: string
  description: Reference voltage source
  enum:
    - "intref"
    - "vddana"
    - "vrefa"
```

这表示 Zephyr 允许在设备树里选择不同参考源。当前教程先使用默认内部参考源，因为它已经在 XIAO SAMD21 上验证稳定。

一句话总结：设备树属性能写什么，要去对应的 binding YAML 文件里查；当前教程先使用已经稳定的默认参考源。

### 13.3 当前稳定基线是什么

当前稳定基线包含三点：

1. `app.overlay` 里启用 USB console 和 ADC channel 4。
2. `main.c` 使用 `dac_channel_setup()` 配置 DAC channel 0，resolution 10。
3. DAC 参考源保持驱动默认值，`512` 输出接近 `0.5V`。

这和 Zephyr 官方 DAC sample 的思路一致：先使用板级设备树已经定义好的 DAC 输出脚，把 DAC 设备、通道和分辨率跑通。

一句话总结：稳定基线就是先让 DAC 默认参考源稳定输出，再逐步增加功能。

### 13.4 这一步学到的判断方法

以后你遇到 DAC、ADC 这类“数字和电压互相转换”的外设时，判断顺序是：

1. 先看分辨率，比如 10-bit 表示 `0` 到 `1023`。
2. 再看参考电压，比如当前默认内部参考源约 `1V`。
3. 最后用“当前数值 / 最大数值 × 参考电压”估算结果。

这次就是：

```text
512 / 1023 × 1V ≈ 0.5V
```

一句话总结：电压换算不能只看写入值，还必须同时看分辨率和参考电压。

## 14. 把固定输出改成递增波形

现在开始让 DAC 输出的电压动起来。

上一节我们只写了一次 `512`，所以 A0/D0 一直保持在接近 `0.5V`。这一节改成从 `0` 写到 `1023`，再回到 `0`，不断重复。

这种波形叫 sawtooth wave，中文常叫“锯齿波”。大白话说，它像楼梯一样一级一级往上走，走到最高后马上回到最低，再重新往上走。

一句话总结：这一节把“固定电压”改成“不断升高再归零的电压”。

### 14.1 这一节要改哪里

只改一个文件：

```text
/Users/mengdu/Desktop/Seeed-Zephyr-Project/examples/boards/xiao_samd21/dac/src/main.c
```

不改 `app.overlay`，不改 `prj.conf`。

原因是：DAC 设备、通道、USB console、Kconfig 功能开关都已经跑通了。现在只是改变 `main.c` 里写给 DAC 的数值。

一句话总结：硬件配置不动，只改 C 代码里的输出数值变化方式。

### 14.2 替换 main.c

把 `main.c` 替换成下面这份：

```c
#include <stdbool.h>

#include <zephyr/device.h>
#include <zephyr/drivers/dac.h>
#include <zephyr/drivers/uart.h>
#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>
#include <zephyr/usb/usb_device.h>

#define CONSOLE_NODE DT_CHOSEN(zephyr_console)
#define DAC_NODE DT_NODELABEL(dac0)
#define DAC_CHANNEL_ID 0
#define DAC_RESOLUTION 10
#define DAC_MAX_VALUE ((1U << DAC_RESOLUTION) - 1U)
#define DAC_STEP_DELAY_MS 2
#define DAC_LOG_INTERVAL 128

static const struct device *const console_dev = DEVICE_DT_GET(CONSOLE_NODE);
static const struct device *const dac_dev = DEVICE_DT_GET(DAC_NODE);

static const struct dac_channel_cfg dac_cfg = {
	.channel_id = DAC_CHANNEL_ID,
	.resolution = DAC_RESOLUTION,
};

/* Returns whether the host serial monitor has asserted USB CDC DTR.
 * 返回主机串口监视器是否已置位 USB CDC DTR。
 */
static bool console_is_connected(void)
{
	uint32_t dtr = 0U;

	return device_is_ready(console_dev) &&
	       uart_line_ctrl_get(console_dev, UART_LINE_CTRL_DTR, &dtr) == 0 &&
	       dtr != 0U;
}

/* Prints the DAC status while the host serial monitor is connected.
 * 在主机串口监视器已连接时输出 DAC 状态。
 */
static void log_dac_status(uint32_t value, bool *was_connected)
{
	bool is_connected = console_is_connected();

	if (is_connected && !*was_connected) {
		printk("XIAO SAMD21 DAC ramp example started\n");
	}
	if (is_connected) {
		printk("DAC ramp value: %u\n", value);
	}

	*was_connected = is_connected;
}

int main(void)
{
	int ret;
	uint32_t value = 0;
	bool console_was_connected = false;

	ret = usb_enable(NULL);
	if (ret != 0) {
		printk("USB device initialization failed: %d\n", ret);
		return 0;
	}

	if (!device_is_ready(dac_dev)) {
		printk("DAC device is not ready\n");
		return 0;
	}

	ret = dac_channel_setup(dac_dev, &dac_cfg);
	if (ret != 0) {
		printk("DAC channel setup failed: %d\n", ret);
		return 0;
	}

	while (1) {
		ret = dac_write_value(dac_dev, DAC_CHANNEL_ID, value);
		if (ret != 0) {
			printk("DAC write failed: %d\n", ret);
			return 0;
		}

		if ((value % DAC_LOG_INTERVAL) == 0U) {
			log_dac_status(value, &console_was_connected);
		}

		if (value >= DAC_MAX_VALUE) {
			value = 0;
		} else {
			value++;
		}

		k_msleep(DAC_STEP_DELAY_MS);
	}

	return 0;
}
```

一句话总结：这份代码会让 DAC 数值从 `0` 一直加到 `1023`，然后回到 `0`。

### 14.3 新增宏是什么意思

```c
#define DAC_MAX_VALUE ((1U << DAC_RESOLUTION) - 1U)
```

这行计算 DAC 的最大值。

`1U << DAC_RESOLUTION` 的意思是把数字 `1` 左移 `DAC_RESOLUTION` 位。现在 `DAC_RESOLUTION` 是 `10`，所以结果是：

```text
1 << 10 = 1024
```

DAC 的数值从 `0` 开始，所以最大值不是 `1024`，而是 `1023`。因此后面要减 `1`。

一句话总结：10-bit DAC 有 `1024` 个档位，最大编号是 `1023`。

```c
#define DAC_STEP_DELAY_MS 2
```

这表示每写一个 DAC 数值，就等 `2ms`。

如果延时太小，波形变化很快，串口打印和测量都不容易观察。如果延时太大，变化又太慢。这里先用 `2ms` 做学习用。

一句话总结：`DAC_STEP_DELAY_MS` 控制电压上升的速度。

```c
#define DAC_LOG_INTERVAL 128
```

这表示每隔 `128` 个数值打印一次。

如果每写一次 DAC 都打印，串口会输出太多内容，反而影响观察。现在只打印 `0`、`128`、`256`、`384` 这些关键点。

一句话总结：`DAC_LOG_INTERVAL` 用来减少串口打印量。

### 14.4 USB 串口连接检查是怎么工作的

```c
static bool console_is_connected(void)
```

这个辅助函数会读取 `UART_LINE_CTRL_DTR`。DTR 是串口连接信号，大白话说，主机上的串口
监视器打开 USB CDC 端口后，就会把这个信号置为有效。

`log_dac_status()` 只在这个信号有效时打印。监视器打开或重新连接时，程序先输出一次启动
信息，再继续报告当前 DAC 数值；监视器关闭后，波形仍然继续运行。

循环末尾仍然执行 `k_msleep(DAC_STEP_DELAY_MS)`。这样 Zephyr 调度器可以定期运行 USB
相关工作，同时 DAC 锯齿波继续输出。

开发板层面的上传与监视机制见
[Runtime Loop Timing for Upload and Monitor](../../en/boards/xiao-samd21.md#runtime-loop-timing-for-upload-and-monitor)。

一句话总结：DAC 始终持续运行，周期日志只发送给已经连接的串口监视器。

### 14.5 新变量 value 是什么

```c
uint32_t value = 0;
```

`value` 就是当前要写进 DAC 的数字。

`uint32_t` 是一种整数类型，可以理解成“只能放非负整数的盒子”。这里用它保存 `0` 到 `1023` 的 DAC 数值。

一句话总结：`value` 是当前输出电压对应的数字。

### 14.6 while 循环里发生了什么

```c
ret = dac_write_value(dac_dev, DAC_CHANNEL_ID, value);
```

这一行把当前 `value` 写进 DAC。

如果 `value` 是 `0`，输出接近最低电压。如果 `value` 是 `512`，输出接近中间电压。如果 `value` 是 `1023`，输出接近当前参考范围的最高电压。

一句话总结：这一行负责把当前数字变成 A0/D0 上的电压。

```c
if ((value % DAC_LOG_INTERVAL) == 0U) {
	log_dac_status(value, &console_was_connected);
}
```

`%` 是取余数。比如 `256 % 128` 等于 `0`，所以 `256` 会被打印；`257 % 128` 不等于 `0`，所以 `257` 不打印。

这段会先检查监视器连接状态，再让串口只显示一部分关键数值。

一句话总结：这段让程序每隔一段数值打印一次状态。

```c
if (value >= DAC_MAX_VALUE) {
	value = 0;
} else {
	value++;
}
```

这段控制数值怎么变化。

如果 `value` 已经到最大值 `1023`，下一步就回到 `0`。否则就加 `1`。

`value++` 的意思是让 `value` 自己加 `1`。

一句话总结：这段负责让数值不断上升，到顶后归零。

```c
k_msleep(DAC_STEP_DELAY_MS);
```

每写完一个值，等 `2ms` 再写下一个值。

一句话总结：这行控制波形变化速度。

### 14.7 构建和验证

重新构建：

```bash
/Users/mengdu/zephyrproject/.venv/bin/west build \
  -b seeeduino_xiao \
  -s /Users/mengdu/Desktop/Seeed-Zephyr-Project/examples/boards/xiao_samd21/dac \
  -d /Users/mengdu/Desktop/Seeed-Zephyr-Project/build/xiao_samd21_dac \
  -p always
```

烧录后，串口应该看到类似：

```text
XIAO SAMD21 DAC ramp example started
DAC ramp value: 0
DAC ramp value: 128
DAC ramp value: 256
DAC ramp value: 384
DAC ramp value: 512
```

如果用万用表测 A0/D0，读数可能会跳动或显示一个平均值。万用表刷新比较慢，不适合看快速波形。如果你想真正看到锯齿波形，需要用示波器。

在当前 XIAO SAMD21 默认 DAC 参考源下，如果你能观察到 D0/A0 电压大约在 `0.1V` 到 `1V` 之间变化，说明递增输出已经生效。

一句话总结：串口能看到数值递增，就说明 DAC 正在按递增波形输出。

### 14.8 下一步做什么

下一步把“线性递增”改成“查表正弦波”。Arduino 示例里用 `sin(x)` 实时算正弦值；在嵌入式里，我们会先学习更稳定、更常见的做法：准备一张 sine table，然后循环写表里的数值。

一句话总结：先做锯齿波理解动态输出，再做正弦波。
