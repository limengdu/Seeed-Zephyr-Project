---
description: A beginner-friendly Zephyr course that uses a Seeed Studio XIAO SAMD21 DAC example to explain project structure, configuration, Devicetree, and driver APIs step by step.
title: "Getting Started with Zephyr: Create a XIAO SAMD21 DAC Example"
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

# Getting Started with Zephyr: Create a XIAO SAMD21 DAC Example

This is an incremental Zephyr course for beginners. Its goal is not to provide final code to copy, but to build `examples/boards/xiao_samd21/dac` by hand while understanding every command, project file, and important configuration line.

The course currently covers creating the example skeleton, understanding and editing `CMakeLists.txt`, writing `example.yaml`, and registering `dac` as a repository example type.

One-sentence summary: we will learn how Zephyr projects are organized and executed by completing a real DAC example.

## 1. Moving from Arduino Concepts to Zephyr

Arduino hides much of the hardware configuration behind simple functions. Zephyr separates the application into clear responsibilities: C code describes behavior, Kconfig selects software features, Devicetree describes hardware connections, and CMake selects the source files to compile.

<div class="table-center">
	<table align="center">
		<tr>
			<th>Arduino</th>
			<th>Zephyr Equivalent</th>
		</tr>
		<tr>
			<td><code>analogWriteResolution(10)</code></td>
			<td>Configure the DAC channel for 10-bit resolution</td>
		</tr>
		<tr>
			<td><code>analogWrite(A0, value)</code></td>
			<td>Call <code>dac_write_value()</code></td>
		</tr>
		<tr>
			<td><code>analogReadResolution(12)</code></td>
			<td>Declare 12-bit resolution in the ADC channel Devicetree configuration</td>
		</tr>
		<tr>
			<td><code>analogRead(A1)</code></td>
			<td>Call <code>adc_read_dt()</code></td>
		</tr>
		<tr>
			<td><code>Serial.println()</code></td>
			<td>Call <code>printk()</code> through the USB CDC console</td>
		</tr>
		<tr>
			<td><code>delay(1)</code></td>
			<td>Call <code>k_msleep(1)</code></td>
		</tr>
		<tr>
			<td><code>sin(x)</code></td>
			<td>Use <code>sinf()</code> from the C math library</td>
		</tr>
	</table>
</div>

The original Arduino example declares `frequency = 440`, but does not use it in the calculation. With `x += 0.02` and an approximately 1 ms delay, one cycle takes about 314 samples, so the actual frequency is approximately `1 / 0.314 = 3.18 Hz`.

To generate a sine wave at a selected frequency, the course will use:

```text
phase_increment = 2 * pi * frequency / sample_rate
```

One-sentence summary: Zephyr describes software features and hardware resources explicitly, and the sine-wave frequency must be calculated from the sample rate.

## 2. Creating the DAC Example Skeleton

### 2.1 Enter the Repository Root

```bash
cd /Users/mengdu/Desktop/Seeed-Zephyr-Project
```

- `cd` is short for `change directory` and changes the terminal's current directory.
- The absolute path points to the Seeed Zephyr repository.
- Subsequent relative paths start from this repository root.

### 2.2 Copy the Validated Baseline Example

```bash
cp -R examples/boards/xiao_samd21/blinky examples/boards/xiao_samd21/dac
```

- `cp` copies files or directories.
- `-R` recursively copies all files and subdirectories.
- The first path is the source: the existing working `blinky` example.
- The second path is the destination: the new `dac` example.

Starting from the existing example reuses a validated Zephyr project structure and the XIAO SAMD21 USB CDC console configuration.

The copied directory contains:

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

One-sentence summary: copying `blinky` provides a known working Zephyr skeleton that can be converted into a DAC example one part at a time.

## 3. Understanding the Project Files

- `CMakeLists.txt`: tells the build system which source files to compile.
- `prj.conf`: enables the software features and drivers required by the application through Kconfig options.
- `app.overlay`: adds application-specific hardware connections to the board's base Devicetree.
- `src/main.c`: contains the application entry point and runtime logic.
- `example.yaml`: stores repository example metadata used by the extension, build scripts, and validation tools.
- `README.md`: explains the example to its users.
- `src/README.md`: describes the source directory.

`example.yaml` belongs to this Seeed repository's management layer. CMake, Kconfig, Devicetree, and the C source files form the core Zephyr application.

One-sentence summary: each file solves one class of problem, and together they form a complete Zephyr application.

## 4. Understanding `CMakeLists.txt`

The DAC example currently uses:

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

- CMake is the build system that organizes the compilation process.
- `cmake_minimum_required()` declares the minimum CMake version required by the project.
- `VERSION 3.20.0` requires CMake 3.20.0 or newer.

This line checks the CMake version, not the Zephyr version.

### 4.2 `find_package`

```cmake
find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
```

- `find_package(Zephyr ...)` finds and loads Zephyr's CMake build support.
- `REQUIRED` marks Zephyr as a mandatory dependency.
- `HINTS` supplies a preferred search location.
- `$ENV{ZEPHYR_BASE}` reads the `ZEPHYR_BASE` environment variable, which points to the Zephyr source tree.

After this package is loaded, the project can use the Zephyr kernel, device drivers, Kconfig, Devicetree, and board configuration.

### 4.3 `project`

```cmake
project(xiao_samd21_dac)
```

- `project()` gives the current CMake project a name.
- `xiao_samd21_dac` identifies this project as the XIAO SAMD21 DAC application.

The name is used internally by CMake and in build logs. The board is selected separately with the `-b seeeduino_xiao` build argument.

### 4.4 `target_sources`

```cmake
target_sources(app PRIVATE src/main.c)
```

- `target_sources()` adds source files to a build target.
- `app` is the application target created by Zephyr.
- `PRIVATE` means the source belongs to this application.
- `src/main.c` is the C source file to compile.

### 4.5 Inspect the File

```bash
sed -n '1,20p' examples/boards/xiao_samd21/dac/CMakeLists.txt
```

- `sed` is a text-processing command.
- `-n` disables the default full output.
- `'1,20p'` prints lines 1 through 20.
- This command reads the file without changing it.

One-sentence summary: `CMakeLists.txt` connects the directory to the Zephyr build system and adds `src/main.c` to the application.

## 5. Understanding `example.yaml`

The current file contains:

```yaml
id: xiao_samd21_dac
board_id: xiao_samd21
demo: dac
zephyr_target: seeeduino_xiao
validation_status: experimental
expected_behavior: Generates a 440 Hz, 10-bit sine wave on D0 and reports the loopback voltage sampled from D1.
```

YAML records configuration as `name: value`. A space follows each colon. This file has no nested levels, so every line starts at the left edge.

### 5.1 `id`

```yaml
id: xiao_samd21_dac
```

`id` is the example's unique repository identity. It combines the board name `xiao_samd21` and the feature name `dac`.

### 5.2 `board_id`

```yaml
board_id: xiao_samd21
```

`board_id` connects the example to `metadata/boards/xiao_samd21.yaml` and identifies the product as Seeed Studio XIAO SAMD21.

### 5.3 `demo`

```yaml
demo: dac
```

`demo` is the short feature name. It matches the directory `examples/boards/xiao_samd21/dac`.

### 5.4 `zephyr_target`

```yaml
zephyr_target: seeeduino_xiao
```

`xiao_samd21` is this repository's product identifier. `seeeduino_xiao` is the upstream Zephyr board target. A native build command uses `west build -b seeeduino_xiao`.

### 5.5 `validation_status`

```yaml
validation_status: experimental
```

`experimental` records that the example is under development and validation. Its status can be updated from actual build and hardware evidence later.

### 5.6 `expected_behavior`

```yaml
expected_behavior: Generates a 440 Hz, 10-bit sine wave on D0 and reports the loopback voltage sampled from D1.
```

This field describes the final acceptance result: D0 produces a 10-bit, 440 Hz sine wave; D1 samples the loopback voltage; and the console reports the result. It documents the goal but does not directly configure the program frequency.

One-sentence summary: `example.yaml` tells the repository and extension which board owns the example, what it is called, its validation stage, and its expected result.

## 6. Registering the `dac` Example Type

The repository validator keeps the allowed board-example names in `tools/validate_metadata/validate.py`:

```python
VALID_EXAMPLE_DEMOS = {"blinky", "dac", "hello_world"}
```

- `VALID_EXAMPLE_DEMOS` names the set of valid example types.
- `=` assigns the data on the right to the variable on the left.
- `{}` creates a Python set, which stores unique members.
- `"blinky"`, `"dac"`, and `"hello_world"` are the allowed example names.

When the validator reads `demo: dac` from `example.yaml`, it confirms that `dac` is present in this set.

### 6.1 Run Metadata Validation

```bash
/Users/mengdu/zephyrproject/.venv/bin/python tools/validate_metadata/validate.py
```

- `/Users/mengdu/zephyrproject/.venv/bin/python` is the Python interpreter in the Zephyr virtual environment.
- `tools/validate_metadata/validate.py` is the repository metadata validator.
- The validator reads board, module, expansion-board, and example YAML files.
- The command validates metadata and file structure; it does not compile firmware.

Successful output includes:

```text
PASS examples/boards/xiao_samd21/dac/example.yaml
SUMMARY: ... passed, 0 failed, ... total
```

One-sentence summary: after `dac` is registered and validated, the repository tools and extension recognize it as an official example type.

## 7. Configuring `prj.conf`

`prj.conf` is the feature-switch file for a Zephyr application. You can think of it as a shopping list: when the application needs DAC, ADC, USB serial, or console support, those features must be listed here so Zephyr can include the matching drivers and subsystems in the firmware.

This section introduces Kconfig. Kconfig is Zephyr's configuration system for enabling and disabling features. `CONFIG_XXX=y` means “enable this feature”, and `CONFIG_XXX=n` means “disable this feature”.

One-sentence summary: `prj.conf` does not contain application logic; it tells Zephyr which system features the program needs.

### 7.1 Features Required by This Example

After migrating the Arduino DAC example, the program needs three main capabilities:

- Output an analog voltage, matching Arduino's `analogWrite(A0, dacVoltage)`.
- Read an analog voltage, matching Arduino's `analogRead(A1)`.
- Print the sampled voltage through USB serial, matching Arduino's `Serial.println(voltage)`.

So `prj.conf` needs to enable DAC, ADC, and serial console related features.

One-sentence summary: the three Arduino actions map to three Zephyr configuration groups: DAC, ADC, and USB serial console.

### 7.2 Understand the Configuration by Feature Group

`prj.conf` contains many names that start with `CONFIG_`. At the beginning, you do not need to memorize them. It is easier to read them as 4 feature groups.

The first group is analog input and output:

```conf
CONFIG_DAC=y
CONFIG_ADC=y
```

`CONFIG_DAC=y` enables the “number to voltage” capability. The program gives a number, and the DAC turns it into an analog voltage on a pin.

`CONFIG_ADC=y` enables the “voltage to number” capability. The board reads a voltage, and the ADC turns it into a number the program can process.

One-sentence summary: DAC writes voltage, and ADC reads voltage.

The second group is printing support:

```conf
CONFIG_PRINTK=y
CONFIG_STDOUT_CONSOLE=y
```

`CONFIG_PRINTK=y` enables Zephyr's basic `printk()` function. You can first understand it as Zephyr's version of `Serial.print()`.

`CONFIG_STDOUT_CONSOLE=y` connects the program's default text output to the console. In simple terms, it gives printed text a path out of the program.

One-sentence summary: these two lines let the program print voltage values.

The third group is the serial console:

```conf
CONFIG_SERIAL=y
CONFIG_CONSOLE=y
CONFIG_UART_CONSOLE=y
CONFIG_UART_LINE_CTRL=y
```

`CONFIG_SERIAL=y` enables serial drivers. Serial communication is the text channel between the computer and the board.

`CONFIG_CONSOLE=y` enables Zephyr's console subsystem. The console is the shared place where Zephyr manages text output.

`CONFIG_UART_CONSOLE=y` tells Zephyr to use UART as the console path. In this example, the UART does not have to be a separate hardware UART pin, because a USB CDC virtual serial port can also appear to Zephyr as a UART device.

`CONFIG_UART_LINE_CTRL=y` enables UART line-control support. USB serial commonly uses it to check whether the serial monitor on the computer is open, such as through the DTR state.

One-sentence summary: these lines connect printed text to the USB virtual serial path.

The fourth group is USB device support:

```conf
CONFIG_USB_DEVICE_STACK=y
CONFIG_DEPRECATION_TEST=y
CONFIG_USB_DEVICE_PRODUCT="Seeed XIAO SAMD21 DAC"
CONFIG_USB_DEVICE_PID=0x0004
CONFIG_USB_DEVICE_INITIALIZE_AT_BOOT=n
CONFIG_USB_DEVICE_STACK_NEXT=n
```

`CONFIG_USB_DEVICE_STACK=y` enables the USB device stack. A stack is a set of communication rules; Zephyr uses it to let the board appear as a USB device to the computer.

`CONFIG_DEPRECATION_TEST=y` allows this example to continue using the legacy Zephyr USB device stack interfaces. This follows the USB configuration pattern used by the existing XIAO SAMD21 examples in this repository.

`CONFIG_USB_DEVICE_PRODUCT="Seeed XIAO SAMD21 DAC"` sets the USB device name shown by the computer. The copied `blinky` name is changed to `DAC` so the device identity matches this example.

`CONFIG_USB_DEVICE_PID=0x0004` sets the USB Product ID. The computer uses this value when identifying the USB device. This example keeps the existing configured value.

`CONFIG_USB_DEVICE_INITIALIZE_AT_BOOT=n` means USB is not initialized automatically as soon as the system boots. Later, when writing `main.c`, the program can enable USB at the right point.

`CONFIG_USB_DEVICE_STACK_NEXT=n` disables Zephyr's newer USB device stack and keeps the legacy USB configuration used by the current example.

One-sentence summary: these lines let the XIAO SAMD21 appear to the computer as a USB serial device.

### 7.3 Recommended `prj.conf` Content

Update `examples/boards/xiao_samd21/dac/prj.conf` to the following content:

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

At this stage, only the configuration is changed. The `main.c` logic will be written later, after the required system features are enabled.

If your file still keeps this line copied from the `blinky` example:

```conf
CONFIG_GPIO=y
```

It enables GPIO drivers. GPIO means General Purpose Input/Output, which refers to general digital input and output pins. The main DAC example flow does not rely on GPIO yet; keeping this line does not affect this section, and the minimal configuration can be cleaned up later.

One-sentence summary: enable the required features first, then write the C code that controls the hardware.

### 7.4 What Each Line Does

```conf
CONFIG_DAC=y
```

Enables the DAC subsystem. DAC means Digital-to-Analog Converter. It converts numbers from the program, such as `0` to `1023`, into an analog voltage on a board pin.

```conf
CONFIG_ADC=y
```

Enables the ADC subsystem. ADC means Analog-to-Digital Converter. It does the opposite of DAC: it reads an analog voltage from a pin and converts it into a number for the program.

```conf
CONFIG_PRINTK=y
```

Enables `printk()` output. `printk()` is Zephyr's basic print function, similar in purpose to Arduino's `Serial.print()`.

```conf
CONFIG_SERIAL=y
```

Enables serial drivers. Serial communication is the text channel between the computer and the board.

```conf
CONFIG_CONSOLE=y
```

Enables the console subsystem. The console is Zephyr's common output path for text messages.

```conf
CONFIG_UART_CONSOLE=y
```

Uses UART as the console backend. UART is common serial hardware; in this example, the USB CDC virtual serial port is exposed to Zephyr as a UART device.

```conf
CONFIG_STDOUT_CONSOLE=y
```

Connects standard output to the console. Standard output is the default place where a program prints text.

```conf
CONFIG_UART_LINE_CTRL=y
```

Enables UART line-control support. USB CDC serial commonly uses line states such as DTR to know whether the serial monitor on the computer is open.

```conf
CONFIG_USB_DEVICE_STACK=y
```

Enables the USB device stack. A stack is a set of communication rules; Zephyr uses it to let the board appear as a USB device to the computer.

```conf
CONFIG_DEPRECATION_TEST=y
```

Allows the example to continue using the legacy Zephyr USB device stack interfaces. The existing XIAO SAMD21 examples in this repository use this USB configuration pattern.

```conf
CONFIG_USB_DEVICE_PRODUCT="Seeed XIAO SAMD21 DAC"
```

Sets the USB product name shown by the computer. The copied `blinky` name is changed to `DAC` so the device identity matches this example.

```conf
CONFIG_USB_DEVICE_PID=0x0004
```

Sets the USB Product ID. This keeps the existing value used by the current example configuration.

```conf
CONFIG_USB_DEVICE_INITIALIZE_AT_BOOT=n
```

Keeps the USB device stack from initializing automatically at boot. The application code can enable USB at the right point later.

```conf
CONFIG_USB_DEVICE_STACK_NEXT=n
```

Uses the legacy USB device stack configuration for this example. `STACK_NEXT` is Zephyr's newer USB device stack switch, and it stays disabled here.

One-sentence summary: each line in `prj.conf` requests a system feature from Zephyr; it does not directly operate a hardware pin.

### 7.5 Check the File After Editing

After editing, run this command from the repository root:

```bash
sed -n '1,80p' examples/boards/xiao_samd21/dac/prj.conf
```

This command prints lines 1 to 80 of `prj.conf`:

- `sed` is a text viewing and processing tool.
- `-n` disables automatic full-file printing.
- `'1,80p'` prints only lines 1 through 80.
- `examples/boards/xiao_samd21/dac/prj.conf` is the file to inspect.

The expected output should include `CONFIG_DAC=y`, `CONFIG_ADC=y`, and the USB product name `Seeed XIAO SAMD21 DAC`.

One-sentence summary: this step only confirms that the configuration file is correct; it does not build the firmware yet.

## 8. Understanding `app.overlay`

`app.overlay` is the application's devicetree overlay file. Devicetree is Zephyr's hardware map: it describes which peripherals exist on the board, what they are called, and how pins are connected.

An `overlay` supplements the board devicetree. It does not replace the whole board description; it adds the application-specific hardware description on top of the board's existing devicetree.

One-sentence summary: `prj.conf` enables features, while `app.overlay` tells Zephyr which hardware device those features should use.

### 8.0 Build the Mental Model First

It helps to read Zephyr hardware information as three layers:

The first layer is the SoC devicetree. SoC means System on Chip, which means the chip itself. Peripherals built into the SAMD21 chip, such as USB, ADC, DAC, and SERCOM, are described at this layer.

The second layer is the board devicetree. This describes how the XIAO SAMD21 board uses the chip: which peripherals are enabled, which pins are connected to LEDs, USB, or DAC, and which devices are available to applications.

The third layer is the application overlay. A specific example can use its own `app.overlay` to adjust default selections or add a child device under an existing peripheral.

This example's `app.overlay` works at the third layer. It does not describe the whole XIAO SAMD21 board again; it only adds “there is a CDC ACM virtual serial port under the USB controller, and the console should use it”.

One-sentence summary: devicetree is the hardware map, and `app.overlay` is a small application-specific note added on top of that map.

### 8.1 Current File Content

The current `examples/boards/xiao_samd21/dac/app.overlay` contains:

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

This file already satisfies the current requirement: it routes Zephyr console output to a USB CDC ACM virtual serial port. CDC ACM can be understood as the “USB virtual serial port” that appears on the computer.

One-sentence summary: this `app.overlay` lets output from functions such as `printk()` come out through USB serial.

### 8.2 What Each Line Does

```dts
/*
 * SPDX-License-Identifier: Apache-2.0
 */
```

This is the license declaration. It does not affect runtime behavior, but it matters in an open-source project.

```dts
/ {
```

`/` is the devicetree root node. You can think of it as the top-level folder of the hardware map.

```dts
	chosen {
```

`chosen` is a special devicetree area used for Zephyr's default selections, such as the default console, shell UART, flash, or RAM.

```dts
		zephyr,console = &cdc_acm_uart0;
```

This tells Zephyr to use `cdc_acm_uart0` as the console output device. The `&` in `&cdc_acm_uart0` means “reference the node with this label”.

```dts
	};
};
```

These lines close the `chosen` node and the root node. Devicetree uses `{}` for node contents and `};` to end a node.

```dts
&zephyr_udc0 {
```

This references the USB device controller that already exists in the board devicetree. `UDC` means USB Device Controller: the controller that lets the board appear as a USB device to the computer.

In the XIAO SAMD21 board devicetree, `zephyr_udc0` already points to `usb0`, and its status is `okay`. So the application can add a USB CDC ACM child device under it.

```dts
	cdc_acm_uart0: cdc_acm_uart0 {
```

This creates a new devicetree node. The `cdc_acm_uart0` before the colon is the label, so later code can reference it as `&cdc_acm_uart0`. The `cdc_acm_uart0` after the colon is the node name.

```dts
		compatible = "zephyr,cdc-acm-uart";
```

`compatible` tells Zephyr which driver should match this node. Here, `zephyr,cdc-acm-uart` means the USB CDC ACM device is exposed as a UART serial device.

```dts
		label = "CDC_ACM_0";
```

`label` is the readable device name. It may appear in debugging output or logs.

```dts
	};
};
```

These lines close the `cdc_acm_uart0` node and the `zephyr_udc0` node.

One-sentence summary: this devicetree overlay creates a virtual serial device under the USB controller and points Zephyr's console to it.

### 8.3 How to Read This DTS Syntax

Devicetree files usually use DTS syntax. DTS can be understood as a configuration language made for describing hardware.

```dts
node_name {
	property = value;
};
```

This is the most common structure:

- `node_name` is the node name, like one entry in the hardware map.
- `{ ... }` contains the node's properties or child nodes.
- `property = value;` is a property that records one piece of information about the node.
- The `;` after each property ends that statement.
- The final `};` ends the node.

This file also uses this form:

```dts
cdc_acm_uart0: cdc_acm_uart0 {
```

The `cdc_acm_uart0` before the colon is the label. The label lets other places find this node by writing `&cdc_acm_uart0`.

The `cdc_acm_uart0` after the colon is the node name. The node name describes what this node is.

It also uses this form:

```dts
&zephyr_udc0 {
```

`&zephyr_udc0` means “reference the existing `zephyr_udc0` node and add more content to it”. The added content is the `cdc_acm_uart0` USB virtual serial port.

One-sentence summary: the key DTS reading skills are nodes, properties, labels, and references; read it as hardware description, not as C code.

### 8.4 How Zephyr Uses This Configuration

This configuration creates a clear output path:

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

Step by step:

- The application calls `printk()` to print text.
- Zephyr sends that text to the console subsystem.
- `zephyr,console = &cdc_acm_uart0;` tells the console to use `cdc_acm_uart0`.
- `compatible = "zephyr,cdc-acm-uart";` makes Zephyr match this node with the USB CDC ACM UART driver.
- `&zephyr_udc0` means this virtual serial port is attached under the USB device controller.
- The computer finally sees a serial device through the USB cable.

One-sentence summary: this overlay connects “text printed by the program” to “the USB serial port on the computer”.

### 8.5 Why No DAC Node Is Added Here, and Why ADC Still Needs Checking

The XIAO SAMD21 board devicetree already enables DAC:

```dts
&dac0 {
	status = "okay";

	pinctrl-0 = <&dac_default>;
	pinctrl-names = "default";
};
```

The board connector file also provides aliases:

```dts
xiao_dac: &dac0 {};
xiao_adc: &adc {};
```

There are two different ideas here.

`xiao_dac: &dac0 {};` gives `dac0` a XIAO-friendly reference name. Because `seeeduino_xiao.dts` already sets `&dac0` to `status = "okay";`, Zephyr can treat the DAC as available hardware.

`xiao_adc: &adc {};` gives `adc` a reference name too. But having a name does not automatically mean the hardware is enabled. The real ADC controller node comes from the SoC devicetree:

```text
/Users/mengdu/zephyrproject/zephyr/dts/arm/atmel/samd2x.dtsi
```

It defines ADC as:

```dts
adc: adc@42004000 {
	compatible = "atmel,sam0-adc";
	reg = <0x42004000 0x2b>;
	status = "disabled";

	#io-channel-cells = <1>;

	prescaler = <4>;
};
```

So ADC still needs another check: the node exists and has a useful name, but its default status is `disabled`. When the ADC part of this example is written, the application overlay needs to enable it and select the ADC input channel to read.

One-sentence summary: DAC is already enabled by the board devicetree; ADC has a name and a base node, but it still needs an overlay to enable it and select an input channel.

### 8.6 Check `app.overlay`

Run this command from the repository root:

```bash
sed -n '1,80p' examples/boards/xiao_samd21/dac/app.overlay
```

This command prints lines 1 to 80 of `app.overlay`. The expected output should include:

- `zephyr,console = &cdc_acm_uart0;`
- `&zephyr_udc0 {`
- `compatible = "zephyr,cdc-acm-uart";`

If these three parts are present, the USB virtual serial console devicetree description is ready for the application.

One-sentence summary: this step does not require editing `app.overlay`; it only confirms that the USB serial console configuration exists.

### 8.7 Where These Settings Come From

Zephyr configuration should not be guessed. When working with a peripheral, use the following source path.

First, look at what the application needs to do.

The Arduino example has three actions:

- `analogWrite(A0, dacVoltage)`: needs DAC.
- `analogRead(A1)`: needs ADC.
- `Serial.println(voltage)`: needs serial output.

So the Zephyr example needs DAC, ADC, and a console path for printed text.

One-sentence summary: start from the required behavior, then decide which hardware capabilities are needed.

Second, check whether the board devicetree already has the hardware.

The XIAO SAMD21 board devicetree is in the Zephyr source tree:

```text
/Users/mengdu/zephyrproject/zephyr/boards/seeed/seeeduino_xiao/seeeduino_xiao.dts
```

Inspect it with:

```bash
sed -n '1,120p' /Users/mengdu/zephyrproject/zephyr/boards/seeed/seeeduino_xiao/seeeduino_xiao.dts
```

It contains:

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

This proves two things:

- `zephyr_udc0` comes from the board devicetree; it is not invented by the application.
- `dac0` is already `okay`, so the board devicetree already enables DAC.

One-sentence summary: check the board `.dts` first to confirm whether the hardware node already exists and is enabled.

Third, check the XIAO connector aliases.

The XIAO connector file is:

```text
/Users/mengdu/zephyrproject/zephyr/boards/seeed/seeeduino_xiao/seeed_xiao_connector.dtsi
```

Inspect it with:

```bash
sed -n '1,80p' /Users/mengdu/zephyrproject/zephyr/boards/seeed/seeeduino_xiao/seeed_xiao_connector.dtsi
```

It contains:

```dts
gpio-map = <0 0 &porta 2 0>,		/* D0 */
	   <1 0 &porta 4 0>,		/* D1 */

xiao_dac: &dac0 {};
xiao_adc: &adc {};
```

This shows:

- XIAO `D0` maps to chip pin `PA2`.
- XIAO `D1` maps to chip pin `PA4`.
- `xiao_dac` is an alias for `dac0`.
- `xiao_adc` is an alias for `adc`.

One-sentence summary: the connector file connects board silkscreen names such as D0 and D1 to chip pins and Zephyr device names.

Fourth, check official samples or snippets for the overlay pattern.

The official USB CDC ACM console snippet is in:

```text
/Users/mengdu/zephyrproject/zephyr/snippets/cdc-acm-console/
```

Inspect its overlay:

```bash
sed -n '1,80p' /Users/mengdu/zephyrproject/zephyr/snippets/cdc-acm-console/cdc-acm-console.overlay
```

It uses this structure:

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

This is the source pattern for the current `app.overlay`. This example only needs console output, so it sets `zephyr,console`.

One-sentence summary: when unsure how to write an overlay, first search Zephyr official samples or snippets.

Fifth, check the binding to confirm that `compatible` is valid.

The definition of `compatible = "zephyr,cdc-acm-uart";` is in:

```text
/Users/mengdu/zephyrproject/zephyr/dts/bindings/serial/zephyr,cdc-acm-uart.yaml
```

It contains:

```yaml
description: USB CDC ACM UART
compatible: "zephyr,cdc-acm-uart"
include: uart-controller.yaml
on-bus: usb
```

This confirms that `zephyr,cdc-acm-uart` is a formally defined Zephyr device type and that it lives on the USB bus.

One-sentence summary: check `dts/bindings/` to confirm what a `compatible` string means.

Sixth, check Kconfig to know which `CONFIG_` options are required.

The DAC top-level switch comes from:

```text
/Users/mengdu/zephyrproject/zephyr/drivers/dac/Kconfig
```

It contains:

```kconfig
menuconfig DAC
	bool "Digital-to-Analog Converter (DAC) drivers"
```

So the application enables:

```conf
CONFIG_DAC=y
```

SAMD21 is part of the SAM0 family. Its DAC driver configuration is in:

```text
/Users/mengdu/zephyrproject/zephyr/drivers/dac/Kconfig.sam0
```

It contains:

```kconfig
config DAC_SAM0
	default y
	depends on DT_HAS_ATMEL_SAM0_DAC_ENABLED
```

This means the SAM0 DAC driver is enabled by default when devicetree contains an enabled `atmel,sam0-dac` node.

ADC follows the same pattern in:

```text
/Users/mengdu/zephyrproject/zephyr/drivers/adc/Kconfig.sam0
```

It contains:

```kconfig
config ADC_SAM0
	default y
	depends on DT_HAS_ATMEL_SAM0_ADC_ENABLED
```

One-sentence summary: `CONFIG_DAC=y` and `CONFIG_ADC=y` come from Zephyr Kconfig; whether the concrete SAM0 driver is available also depends on enabled devicetree hardware nodes.

### 8.8 How to Decide Whether a Peripheral Needs an Overlay

Use this process for future peripherals.

First, check whether the board devicetree already has the device.

- If the node exists and has `status = "okay";`, the application usually does not need to declare that hardware again.
- If the node exists but has `status = "disabled";`, the application overlay may need to enable it and provide pinctrl information.
- If the node does not exist, first confirm that the chip and board really support that peripheral.

Second, check whether the application needs to change a default choice.

For example, the XIAO SAMD21 board default console is `sercom4`, but this DAC example wants printed text over USB virtual serial. That is why `app.overlay` sets:

```dts
zephyr,console = &cdc_acm_uart0;
```

Third, check whether the application needs to add a child device.

The USB controller `zephyr_udc0` already exists, but the CDC ACM virtual serial child device is application-specific, so `app.overlay` adds:

```dts
&zephyr_udc0 {
	cdc_acm_uart0: cdc_acm_uart0 {
		compatible = "zephyr,cdc-acm-uart";
	};
};
```

One-sentence summary: do not invent devicetree content; check the board first, copy the pattern from official examples, and verify the result through bindings and Kconfig.

### 8.9 First Learn How to Find the Right Files

The Zephyr source tree is large. For beginners, the hard part is often not reading one file, but knowing why that file is the correct one. The practical answer is to follow Zephyr's hardware description entry points instead of memorizing paths.

Think of Zephyr hardware data as a filing cabinet: the `board target` is the file number, the board `.dts` file is the first document, `.dtsi` files are included pages, bindings are property manuals, and Kconfig is the feature switch list.

One-sentence summary: the first skill is not memorizing filenames; it is knowing the order Zephyr uses to find hardware information.

First, identify the current `board target`.

The `board target` is the board name selected during build. In a build command, it is the value after `-b`:

```bash
west build -b seeeduino_xiao examples/boards/xiao_samd21/dac
```

Here, `seeeduino_xiao` is the board target. Zephyr uses this name to find the board devicetree.

If you only know that the board is a XIAO board, list matching boards first:

```bash
west boards | rg -i "xiao|seeeduino"
```

You can also search the local Zephyr board metadata directly:

```bash
rg -n "^identifier: seeeduino_xiao$" /Users/mengdu/zephyrproject/zephyr/boards -g "*.yaml"
```

This finds:

```text
/Users/mengdu/zephyrproject/zephyr/boards/seeed/seeeduino_xiao/seeeduino_xiao.yaml
```

So the board directory for `seeeduino_xiao` is:

```text
/Users/mengdu/zephyrproject/zephyr/boards/seeed/seeeduino_xiao/
```

One-sentence summary: start from the board target because Zephyr uses it to choose the board hardware map for the build.

Second, open the board `.dts` file from that board directory.

In the board directory, you usually see files like:

```text
seeeduino_xiao.dts
seeeduino_xiao.yaml
seeeduino_xiao-pinctrl.dtsi
seeed_xiao_connector.dtsi
```

The most important file is `seeeduino_xiao.dts`. `.dts` means Devicetree Source. In plain language, it is the main hardware map for this board. Once Zephyr selects the `seeeduino_xiao` board target, this `.dts` file is the entry point for the board devicetree.

Inspect the beginning:

```bash
sed -n '1,30p' /Users/mengdu/zephyrproject/zephyr/boards/seeed/seeeduino_xiao/seeeduino_xiao.dts
```

You will see:

```dts
/dts-v1/;
#include <atmel/samd21.dtsi>
#include <atmel/samx2xx18.dtsi>
#include "seeeduino_xiao-pinctrl.dtsi"
#include "seeed_xiao_connector.dtsi"
```

There are two include styles:

- `"seeed_xiao_connector.dtsi"` usually refers to a file near the board `.dts` file.
- `<atmel/samd21.dtsi>` usually refers to a common Zephyr include file for the chip or chip family.

So the connector file is not chosen randomly; the board `.dts` explicitly includes it. The SoC file is not guessed either; the board `.dts` explicitly includes it.

One-sentence summary: the board `.dts` is the entry point; follow the files it includes.

Third, check how the board exposes pins.

For Arduino `A1`, the question is “which chip pin does this board label connect to?” This is a board-pin mapping question, so the connector file is the right place to start.

Open the connector file:

```bash
sed -n '1,80p' /Users/mengdu/zephyrproject/zephyr/boards/seeed/seeeduino_xiao/seeed_xiao_connector.dtsi
```

It contains:

```dts
gpio-map = <0 0 &porta 2 0>,		/* D0 */
	   <1 0 &porta 4 0>,		/* D1 */
```

Read it like this:

- `D1` in the comment is the board pin name.
- `&porta` is the SAMD21 GPIO port A controller.
- `4` means pin 4 on port A, which is `PA4`.

On XIAO SAMD21, `A1` and `D1` are two usage names for the same physical board pin: it is called `D1` for digital IO and `A1` for analog input. So this step gives `A1/D1 -> PA4`.

One-sentence summary: for board labels such as `A1`, start from the connector file or official pinout because they translate board names into chip pins.

Fourth, check whether that chip pin supports ADC.

After finding `PA4`, the next question is whether `PA4` has an ADC function, and which ADC input number it uses.

This is why we look at pinctrl. `pinctrl` means Pin Control. In plain language, it is the chip pin function table. One chip pin can often work as GPIO, UART, I2C, ADC, or another function.

First inspect the board pinctrl file:

```bash
sed -n '1,20p' /Users/mengdu/zephyrproject/zephyr/boards/seeed/seeeduino_xiao/seeeduino_xiao-pinctrl.dtsi
```

It includes:

```dts
#include <dt-bindings/pinctrl/samd21-da1gXabcd-pinctrl.h>
```

Then search that included header for the ADC function of `PA4`:

```bash
rg -n "PA4.*ADC|PA4B_ADC_AIN4" /Users/mengdu/zephyrproject/modules/hal/atmel/include/dt-bindings/pinctrl/samd21-da1gXabcd-pinctrl.h
```

It contains:

```c
/* pa4b_adc_ain4 */
#define PA4B_ADC_AIN4 \
	SAM_PINMUX(a, 4, b, periph)
```

This means `PA4` can connect to the ADC peripheral through function group B, and it maps to `AIN4`, ADC analog input 4.

One-sentence summary: the chain `A1 -> PA4 -> ADC AIN4` comes from the connector file and the chip pinctrl definition.

Fifth, find the ADC controller node name in Zephyr.

Now we know the external input is ADC input 4, but we still need to know whether the overlay should use `&adc`, `&adc0`, or another label. That label comes from the SoC devicetree.

Why the SoC devicetree? Because the ADC controller is inside the SAMD21 chip. Chip-internal peripherals, their register addresses, and their default status are normally described in SoC `.dtsi` files.

The board `.dts` includes:

```dts
#include <atmel/samd21.dtsi>
```

Open it:

```bash
sed -n '1,30p' /Users/mengdu/zephyrproject/zephyr/dts/arm/atmel/samd21.dtsi
```

It includes:

```dts
#include <atmel/samd2x.dtsi>
```

So continue to the common SAMD2x file:

```bash
sed -n '200,215p' /Users/mengdu/zephyrproject/zephyr/dts/arm/atmel/samd2x.dtsi
```

There you find the real ADC node:

```dts
adc: adc@42004000 {
	compatible = "atmel,sam0-adc";
	reg = <0x42004000 0x2b>;
	status = "disabled";
	#io-channel-cells = <1>;
	prescaler = <4>;
};
```

The `adc:` part is the devicetree label. `&adc` in an overlay refers to this label.

One-sentence summary: the controller name comes from the SoC `.dtsi`; follow the include chain and read the node label.

Sixth, use `compatible` to find the binding.

The ADC node contains:

```dts
compatible = "atmel,sam0-adc";
```

`compatible` is the device type label. Zephyr uses it to match the node with bindings and drivers.

A binding is the property manual for a devicetree node. It says which properties are allowed, which are required, and what type each property uses.

Search bindings by `compatible`:

```bash
rg -n 'compatible: "atmel,sam0-adc"' /Users/mengdu/zephyrproject/zephyr/dts/bindings
```

This finds:

```text
/Users/mengdu/zephyrproject/zephyr/dts/bindings/adc/atmel,sam0-adc.yaml
```

Open it:

```bash
sed -n '1,80p' /Users/mengdu/zephyrproject/zephyr/dts/bindings/adc/atmel,sam0-adc.yaml
```

It contains:

```yaml
compatible: "atmel,sam0-adc"

include:
  - name: adc-controller.yaml
  - name: pinctrl-device.yaml
  - name: atmel,assigned-clocks.yaml

io-channel-cells:
  - input
```

The `io-channel-cells: input` entry means the number in `<&adc 4>` is an ADC input number. General ADC channel properties are described in the included `adc-controller.yaml` file.

One-sentence summary: use the node's `compatible` string to find the binding, then use the binding to know which overlay properties are valid.

Seventh, find an official example of the same kind, but use it for structure only.

After reading the binding, search official samples or tests to see how Zephyr projects usually organize this kind of overlay:

```bash
rg -n "io-channels = <&adc|channel@" /Users/mengdu/zephyrproject/zephyr/tests/drivers/adc /Users/mengdu/zephyrproject/zephyr/samples
```

For SAMD21, one useful file is:

```text
/Users/mengdu/zephyrproject/zephyr/tests/drivers/adc/adc_api/boards/samd21_xpro.overlay
```

This file is useful because it uses the same SAMD21 / SAM0 ADC driver family, not because it is the same board as XIAO. Learn the overlay structure from it, but keep the actual input channel from the XIAO-specific chain `A1 -> PA4 -> AIN4`.

One-sentence summary: official examples teach the structure; your own board files and pinctrl data decide the real pin and channel.

Eighth, read Kconfig to understand why `CONFIG_ADC=y` is only one half of the story.

Kconfig is Zephyr's feature switch system. `CONFIG_ADC=y` in `prj.conf` tells Zephyr that the application wants the ADC subsystem. But the concrete SAMD21 ADC driver also depends on an enabled `atmel,sam0-adc` devicetree node.

Search the ADC Kconfig files:

```bash
rg -n "menuconfig ADC|config ADC_SAM0" /Users/mengdu/zephyrproject/zephyr/drivers/adc
```

The SAM0 ADC driver contains:

```kconfig
config ADC_SAM0
	default y
	depends on DT_HAS_ATMEL_SAM0_ADC_ENABLED
```

This means `ADC_SAM0` becomes available when devicetree contains an enabled node with `compatible = "atmel,sam0-adc"`. In other words, `prj.conf` and `app.overlay` work together.

One-sentence summary: `CONFIG_ADC=y` enables the ADC subsystem; `&adc { status = "okay"; };` makes the concrete hardware driver eligible.

For another peripheral, use the same search order:

1. Find the board target from `west build -b ...` or the board `.yaml` file.
2. Use the board target to locate the board directory.
3. Open the board `.dts` and follow its included `.dtsi` files.
4. For board pins, check connector files, pinctrl files, and the official pinout.
5. For chip-internal controllers, follow the SoC `.dtsi` chain and read the node label and `status`.
6. Use the node's `compatible` string to find the binding under `dts/bindings/`.
7. Use similar samples or tests to learn the structure.
8. After writing the overlay, inspect `build/zephyr/zephyr.dts` and `build/zephyr/.config`.

One-sentence summary: the method stays the same when the peripheral changes; only the search keyword changes, such as ADC, I2C, SPI, UART, PWM, or DAC.

### 8.10 How to Write ADC Devicetree Yourself

Now apply the file-finding method to `analogRead(A1)` and build the full evidence chain.

First, translate Arduino `A1` into the real XIAO board pin.

The XIAO SAMD21 connector file contains:

```dts
gpio-map = <0 0 &porta 2 0>,		/* D0 */
	   <1 0 &porta 4 0>,		/* D1 */
```

For XIAO SAMD21, Arduino `A1` refers to the board pin `D1/A1`. The connector file tells us that `D1` is connected to chip pin `PA4`.

One-sentence summary: the first step is to map the board label `A1` to the chip pin `PA4`.

Second, confirm that `PA4` can be used as an ADC input.

The XIAO board pinctrl file includes this header:

```dts
#include <dt-bindings/pinctrl/samd21-da1gXabcd-pinctrl.h>
```

That header is located at:

```text
/Users/mengdu/zephyrproject/modules/hal/atmel/include/dt-bindings/pinctrl/samd21-da1gXabcd-pinctrl.h
```

It contains:

```c
/* pa4b_adc_ain4 */
#define PA4B_ADC_AIN4 \
	SAM_PINMUX(a, 4, b, periph)
```

Read this as:

- `PA4`: port A, pin 4 on the chip.
- `ADC`: this pin can connect to the ADC peripheral.
- `AIN4`: this pin maps to ADC analog input 4.
- `B`: this uses the chip's peripheral function group B.

So the chain is `A1 -> D1 -> PA4 -> ADC AIN4`.

One-sentence summary: the ADC channel number is not invented; it comes from the chip pinctrl definition or the chip datasheet.

Third, confirm the ADC controller name and default status in Zephyr.

The SAMD2x SoC devicetree contains:

```dts
adc: adc@42004000 {
	compatible = "atmel,sam0-adc";
	status = "disabled";
	#io-channel-cells = <1>;
	prescaler = <4>;
};
```

This gives three important facts:

- The controller label is `adc`, so the overlay can use `&adc { ... };`.
- The `compatible` string is `atmel,sam0-adc`, so it uses the SAM0 ADC driver.
- `status = "disabled";` means the application needs to change it to `okay` before using it.

One-sentence summary: `&adc` comes from the SoC devicetree, and `status` decides whether Zephyr can use it as an enabled device.

Fourth, read the ADC binding to learn which properties are valid.

The ADC binding is:

```text
/Users/mengdu/zephyrproject/zephyr/dts/bindings/adc/atmel,sam0-adc.yaml
```

It contains:

```yaml
compatible: "atmel,sam0-adc"

include:
  - name: adc-controller.yaml
  - name: pinctrl-device.yaml
  - name: atmel,assigned-clocks.yaml

io-channel-cells:
  - input
```

This means the `atmel,sam0-adc` controller follows the common ADC controller rules and also supports pinctrl and assigned-clock properties. The `input` entry under `io-channel-cells` means the number in `<&adc 4>` is the ADC input number.

The common ADC channel rules are in:

```text
/Users/mengdu/zephyrproject/zephyr/dts/bindings/adc/adc-controller.yaml
```

It defines channel properties such as:

```yaml
zephyr,gain
zephyr,reference
zephyr,acquisition-time
zephyr,input-positive
zephyr,resolution
```

These fields describe gain, reference voltage, acquisition time, positive input, and resolution.

One-sentence summary: the binding file is the legal menu for devicetree properties; choose fields from it instead of inventing property names.

Fifth, find an official example from the same chip family.

For a SAMD21 ADC example, inspect:

```text
/Users/mengdu/zephyrproject/zephyr/tests/drivers/adc/adc_api/boards/samd21_xpro.overlay
```

It uses this structure:

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

This sample reads an internal chip voltage, not the external XIAO `A1` pin. Therefore, `ADC_INPUTCTRL_MUXPOS_SCALEDIOVCC_Val` should not be copied directly. But the sample does show the useful structure:

- `/ { zephyr,user { io-channels = <&adc ...>; }; };` lets application code fetch an ADC channel from devicetree.
- `&adc { ... };` adds configuration under the ADC controller.
- `channel@...` describes the sampling parameters of one ADC channel.

One-sentence summary: official examples give the structure, but the channel number and input source still come from your own board.

Sixth, derive the ADC overlay direction for XIAO SAMD21.

From the source chain above, `A1` maps to `PA4`, and `PA4` maps to `ADC AIN4`. Therefore, the ADC overlay direction for the later lesson is:

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

For now, treat this as the result of the investigation. In the next lesson, this can be written into `app.overlay` and connected to the C code line by line.

One-sentence summary: when writing ADC devicetree yourself, answer three questions: which ADC controller, which input channel, and which sampling parameters.

Seventh, verify the final merged result after building.

After writing an overlay, inspect the generated files instead of only reading the source file:

```bash
rg -n "adc|zephyr,user|io-channels" build/zephyr/zephyr.dts
rg -n "CONFIG_ADC|CONFIG_ADC_SAM0" build/zephyr/.config
```

`build/zephyr/zephyr.dts` is the final merged devicetree. It shows the real hardware map after Zephyr combines the SoC devicetree, board devicetree, and application overlay.

`build/zephyr/.config` is the final Kconfig result. It shows whether `CONFIG_ADC=y` and the concrete `CONFIG_ADC_SAM0=y` driver option are actually enabled.

One-sentence summary: after writing devicetree, use `zephyr.dts` to check the final hardware map and `.config` to check the final feature switches.

## 9. Add ADC Configuration to `app.overlay`

This section starts the actual `app.overlay` update. You will edit the file yourself; this section explains what to add and why each line exists.

The current `app.overlay` already contains the USB virtual serial console. Now we add the ADC input description for Arduino's `analogRead(A1)`.

One-sentence summary: the goal of this section is to tell Zephyr that this application reads voltage from ADC input 4.

### 9.1 Open the File to Be Modified

Run this command from the repository root:

```bash
sed -n '1,120p' examples/boards/xiao_samd21/dac/app.overlay
```

This only prints the file content. It does not modify the file.

- `sed` is a text viewing and processing tool.
- `-n` disables automatic printing.
- `'1,120p'` prints lines 1 to 120.
- The path points to the overlay file of this example.

You should see the USB console section:

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

One-sentence summary: confirm that you are editing the application's `app.overlay`, not the board `.dts` file inside Zephyr.

### 9.2 Add the ADC Macro Header

Add this line after the SPDX comment:

```dts
#include <zephyr/dt-bindings/adc/adc.h>
```

The beginning of the file should look like this:

```dts
/*
 * SPDX-License-Identifier: Apache-2.0
 */

#include <zephyr/dt-bindings/adc/adc.h>
```

This line brings ADC-related devicetree macros into the overlay. A macro is a named fixed value. Later we will write:

```dts
zephyr,acquisition-time = <ADC_ACQ_TIME_DEFAULT>;
```

`ADC_ACQ_TIME_DEFAULT` comes from:

```text
/Users/mengdu/zephyrproject/zephyr/include/zephyr/dt-bindings/adc/adc.h
```

It is defined as:

```c
#define ADC_ACQ_TIME_DEFAULT 0
```

Using the macro name is easier to understand than writing `0` directly. `ADC_ACQ_TIME_DEFAULT` clearly means “use the default ADC acquisition time”.

One-sentence summary: `#include <zephyr/dt-bindings/adc/adc.h>` lets the overlay use ADC names such as `ADC_ACQ_TIME_DEFAULT`.

### 9.3 Add `zephyr,user` Under the Root Node

You already have this root node:

```dts
/ {
	chosen {
		zephyr,console = &cdc_acm_uart0;
	};
};
```

Expand it to:

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

Line by line:

```dts
/ {
```

This is the root node of the devicetree. Think of it as the outermost layer of the hardware map.

```dts
chosen {
	zephyr,console = &cdc_acm_uart0;
};
```

This is the existing USB serial console configuration. Keep it unchanged. It tells Zephyr to route printed output to `cdc_acm_uart0`.

```dts
zephyr,user {
	io-channels = <&adc 4>;
};
```

This is the new ADC entry point for the application.

`zephyr,user` is a common application-defined node in Zephyr samples. It is not a physical chip peripheral. It is more like a small note where the application stores devicetree references. Later, C code can find it with `DT_PATH(zephyr_user)`.

`io-channels` means “the input/output channels used by this application”. For ADC, it commonly lists ADC channels to read.

`<&adc 4>` has two parts:

- `&adc`: references the ADC controller node from the SoC devicetree.
- `4`: the ADC input number, derived from `A1 -> PA4 -> ADC AIN4`.

One-sentence summary: the `zephyr,user` block tells the later C code that this example reads input 4 from the `adc` controller.

### 9.4 Add the `&adc` Configuration at the End

Add this block at the end of `app.overlay`:

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

Line by line:

```dts
&adc {
```

`&adc` references the existing ADC node. This node is not created here; it comes from:

```text
/Users/mengdu/zephyrproject/zephyr/dts/arm/atmel/samd2x.dtsi
```

The label there is:

```dts
adc: adc@42004000
```

In devicetree, `adc:` defines the label, and `&adc` references it.

One-sentence summary: `&adc` modifies the ADC controller node that already exists inside the chip description.

```dts
status = "okay";
```

The SoC file sets ADC to:

```dts
status = "disabled";
```

The application enables it by setting the status to `okay` in the overlay. `okay` means this hardware is enabled for this build.

One-sentence summary: `status = "okay";` changes ADC from “present but disabled” to “enabled for this application”.

```dts
#address-cells = <1>;
#size-cells = <0>;
```

These two lines support the `channel@4` child node below.

`#address-cells = <1>;` means each child node address is represented by one number. Here, that number is the channel number.

`#size-cells = <0>;` means child nodes do not need a size value. An ADC channel is not a memory region, so its size is `0`.

One-sentence summary: these two lines tell the devicetree parser that ADC child nodes use channel numbers as addresses and do not need size fields.

```dts
channel@4 {
```

This is the configuration node for ADC channel 4. `@4` means the node address is 4, matching `reg = <4>;`.

The ADC binding expects ADC channel child nodes to use the `channel` name, so this node is written as `channel@4`.

One-sentence summary: `channel@4` describes how ADC input 4 should be sampled.

```dts
reg = <4>;
```

`reg` is the child node number. Here it is `4`, matching `channel@4` and `io-channels = <&adc 4>;`.

One-sentence summary: `reg = <4>;` means this child node describes ADC channel 4.

```dts
zephyr,gain = "ADC_GAIN_1";
```

`gain` controls whether the ADC internally scales the input voltage.

`ADC_GAIN_1` means 1x gain: no amplification and no reduction. For a normal 0 to 3.3V input, this is the simple starting point.

One-sentence summary: `ADC_GAIN_1` reads the voltage at its original scale.

```dts
zephyr,reference = "ADC_REF_VDD_1";
```

`reference` is the full-scale voltage standard used by the ADC.

`ADC_REF_VDD_1` means the ADC uses VDD as the reference. XIAO SAMD21 normally works with 3.3V logic, which matches the Arduino example's `3.3 / 4096.0` voltage conversion idea.

One-sentence summary: `ADC_REF_VDD_1` uses board VDD as the ADC full-scale reference.

```dts
zephyr,acquisition-time = <ADC_ACQ_TIME_DEFAULT>;
```

`acquisition-time` is the sampling hold time. In plain language, it gives the input voltage time to settle before conversion.

`ADC_ACQ_TIME_DEFAULT` uses the driver's default setting. This value comes from the ADC dt-bindings header included earlier.

One-sentence summary: this line uses the driver's default ADC sampling time.

```dts
zephyr,resolution = <12>;
```

`resolution` is the ADC resolution. The Arduino example uses:

```cpp
analogReadResolution(12);
```

So the Zephyr overlay also uses `12`. A 12-bit ADC result usually ranges from `0` to `4095`, which gives 4096 levels.

One-sentence summary: `zephyr,resolution = <12>;` matches Arduino's `analogReadResolution(12)`.

```dts
zephyr,input-positive = <4>;
```

`input-positive` selects the positive ADC input. The SAMD21 ADC driver uses this number to configure the hardware input selection.

We already traced `PA4` to `ADC AIN4`, so this value is `4`.

One-sentence summary: `zephyr,input-positive = <4>;` selects AIN4, which is XIAO A1/D1.

### 9.5 Expected `app.overlay` After This Section

Your final `app.overlay` should look like this:

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

One-sentence summary: the file now does two jobs: route printed output to USB serial and expose ADC input 4 to the application code.

### 9.6 Check the Text After Editing

After editing, run:

```bash
sed -n '1,160p' examples/boards/xiao_samd21/dac/app.overlay
```

Check these four points:

1. The top includes `#include <zephyr/dt-bindings/adc/adc.h>`.
2. The root node `/ { ... };` contains both `chosen` and `zephyr,user`.
3. `io-channels = <&adc 4>;` uses `4`.
4. The end of the file contains `&adc { ... channel@4 { ... }; };`.

One-sentence summary: first check the text structure, then move on to build verification.

### 9.7 What to Verify Next

This section only writes the devicetree. After editing it, the next step is not writing `main.c` yet. First build once and inspect Zephyr's merged output.

After building, focus on two files:

```text
build/zephyr/zephyr.dts
build/zephyr/.config
```

`zephyr.dts` confirms whether ADC is finally `okay` and whether `zephyr,user` contains `io-channels = <&adc 4>`.

`.config` confirms whether `CONFIG_ADC=y` and `CONFIG_ADC_SAM0=y` are enabled.

One-sentence summary: the source overlay is your intention; `build/zephyr/zephyr.dts` is the final hardware map accepted by Zephyr.

## 10. Build and Inspect the Generated Devicetree

The ADC configuration is now in `app.overlay`. This section does not add new source code. It builds the project once and checks whether Zephyr's final merged devicetree and Kconfig output match the intended configuration.

One-sentence summary: after writing an overlay, build once and inspect generated files before moving to `main.c`.

### 10.1 Why This Command Uses the Full `west` Path

If the Zephyr environment is already active, `west` can be used directly. If the terminal prints:

```text
command not found: west
```

then the current shell does not have the Zephyr virtual environment in `PATH`.

On this machine, `west` is available at:

```text
/Users/mengdu/zephyrproject/.venv/bin/west
```

This is not a different build tool. It is the full path to the same `west` command. Using the full path makes the command work even when the shell environment is not fully configured.

One-sentence summary: `/Users/mengdu/zephyrproject/.venv/bin/west` is the local Zephyr environment's `west` command.

### 10.2 Run the Build Command

Run:

```bash
/Users/mengdu/zephyrproject/.venv/bin/west build \
  -b seeeduino_xiao \
  -s /Users/mengdu/Desktop/Seeed-Zephyr-Project/examples/boards/xiao_samd21/dac \
  -d /Users/mengdu/Desktop/Seeed-Zephyr-Project/build/xiao_samd21_dac \
  -p always
```

Line by line:

```bash
/Users/mengdu/zephyrproject/.venv/bin/west build
```

Runs Zephyr's build command. `west` is Zephyr's recommended project and build tool.

```bash
-b seeeduino_xiao
```

Selects the board target. It tells Zephyr that this firmware is built for the `seeeduino_xiao` board.

```bash
-s /Users/mengdu/Desktop/Seeed-Zephyr-Project/examples/boards/xiao_samd21/dac
```

Selects the application source directory. `-s` means source.

```bash
-d /Users/mengdu/Desktop/Seeed-Zephyr-Project/build/xiao_samd21_dac
```

Selects the build output directory. `-d` means build directory.

```bash
-p always
```

Forces CMake to regenerate the build directory so the updated overlay is parsed again.

One-sentence summary: this command tells Zephyr which board to build for, where the application source is, and where generated files should go.

### 10.3 What a Successful Build Shows

A successful build should include output similar to:

```text
-- Found BOARD.dts: /Users/mengdu/zephyrproject/zephyr/boards/seeed/seeeduino_xiao/seeeduino_xiao.dts
-- Found devicetree overlay: /Users/mengdu/Desktop/Seeed-Zephyr-Project/examples/boards/xiao_samd21/dac/app.overlay
-- Generated zephyr.dts: /Users/mengdu/Desktop/Seeed-Zephyr-Project/build/xiao_samd21_dac/zephyr/zephyr.dts
Configuration saved to '/Users/mengdu/Desktop/Seeed-Zephyr-Project/build/xiao_samd21_dac/zephyr/.config'
```

These lines mean:

- Zephyr found the board devicetree `seeeduino_xiao.dts`.
- Zephyr found the application overlay `app.overlay`.
- Zephyr generated the final merged devicetree `zephyr.dts`.
- Zephyr generated the final Kconfig output `.config`.

The build also produces firmware files such as:

```text
zephyr.elf
zephyr.uf2
```

`zephyr.uf2` can later be used to flash XIAO SAMD21.

One-sentence summary: a successful build confirms that the C code builds and that the devicetree syntax was accepted by Zephyr.

### 10.4 Inspect the Final Merged Devicetree

Run:

```bash
rg -n "zephyr,user|io-channels|adc@42004000|channel@4|input-positive" \
  /Users/mengdu/Desktop/Seeed-Zephyr-Project/build/xiao_samd21_dac/zephyr/zephyr.dts
```

This searches the final merged devicetree for ADC-related content.

You should see output similar to:

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

Two details matter here.

First, `adc: xiao_adc: adc@42004000` means this node now has two labels: `adc` from the SoC devicetree and `xiao_adc` from the XIAO connector file.

Second, `0x4` and `0xc` are hexadecimal numbers:

- `0x4` equals decimal `4`.
- `0xc` equals decimal `12`.

So:

```dts
zephyr,resolution = < 0xc >;
```

is the generated form of:

```dts
zephyr,resolution = <12>;
```

One-sentence summary: if `zephyr.dts` contains `status = "okay"`, `channel@4`, and `io-channels = <&adc 0x4>`, the ADC devicetree has been merged correctly.

### 10.5 Inspect the Final Kconfig Output

Run:

```bash
rg -n "CONFIG_ADC|CONFIG_ADC_SAM0|CONFIG_DAC|CONFIG_DAC_SAM0" \
  /Users/mengdu/Desktop/Seeed-Zephyr-Project/build/xiao_samd21_dac/zephyr/.config
```

You should see:

```text
CONFIG_ADC=y
CONFIG_ADC_CONFIGURABLE_INPUTS=y
CONFIG_ADC_SAM0=y
CONFIG_DAC=y
CONFIG_DAC_SAM0=y
```

These settings mean:

- `CONFIG_ADC=y`: the ADC subsystem is enabled.
- `CONFIG_ADC_SAM0=y`: the SAM0 ADC driver used by SAMD21 is enabled.
- `CONFIG_ADC_CONFIGURABLE_INPUTS=y`: the ADC driver supports input selection through `zephyr,input-positive`.
- `CONFIG_DAC=y`: the DAC subsystem is enabled.
- `CONFIG_DAC_SAM0=y`: the SAM0 DAC driver used by SAMD21 is enabled.

One-sentence summary: `.config` proves that both the feature switches and the concrete chip drivers are active.

### 10.6 Result of This Stage

At this point, three things are confirmed:

1. The `app.overlay` syntax is accepted by Zephyr.
2. The ADC node is finally `okay` instead of `disabled`.
3. The SAM0 ADC driver is enabled, so the next step can use the ADC API from `main.c`.

One-sentence summary: the devicetree and configuration layers are ready; next we can translate Arduino `analogWrite()` and `analogRead()` into Zephyr C APIs.

## 11. Write a Minimal `main.c` to Verify the Entry Point and USB Output

The devicetree and Kconfig layers are verified. Now we move into C code, but not DAC or ADC yet. The first C step is a minimal application: start the USB device stack and print one line every second with `printk()`.

Why start here? Later DAC and ADC code will rely on serial output for debugging. If USB console is not verified first, ADC output problems become harder to diagnose.

One-sentence summary: first verify that the program starts and USB output works, then add DAC and ADC logic.

### 11.1 Why Simplify the Current `main.c`

The current `main.c` was copied from `blinky`, so it still contains LED and GPIO logic. The final DAC example does not depend on LED blinking, so this section removes that logic first.

This is not the final feature. It is a clean starting point, like checking that the front door opens before moving furniture into a house.

One-sentence summary: removing the blinky logic gives the later DAC and ADC code a clean main program.

### 11.2 Replace `src/main.c`

Open:

```text
examples/boards/xiao_samd21/dac/src/main.c
```

Replace it with:

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

One-sentence summary: this `main.c` only starts USB console and keeps printing text.

### 11.3 Understand the Code Line by Line

```c
#include <zephyr/kernel.h>
```

Includes Zephyr kernel APIs. This program uses `k_msleep()` from this header to pause execution.

One-sentence summary: `kernel.h` provides basic Zephyr system features such as sleeping.

```c
#include <zephyr/sys/printk.h>
```

Includes `printk()`. It is similar in purpose to Arduino's `Serial.println()`: it prints text to the console.

One-sentence summary: `printk()` is Zephyr's basic print function.

```c
#include <zephyr/usb/usb_device.h>
```

Includes the USB device API. This program uses `usb_enable()` to start the USB device stack.

One-sentence summary: `usb_device.h` lets the program manually start USB device support.

```c
#define HEARTBEAT_INTERVAL_MS 1000
```

Defines a constant for the heartbeat interval. `1000` milliseconds equals 1 second.

A heartbeat is a repeated message that proves the program is still running.

One-sentence summary: this constant controls how often the status message is printed.

```c
int main(void)
```

This is the application entry point. Zephyr calls `main()` after the system has started.

One-sentence summary: `main()` is where the application code begins.

```c
int ret;
```

Defines an integer used to store return values. Many Zephyr functions return `0` on success and a non-zero value on failure.

One-sentence summary: `ret` records whether a function succeeded.

```c
ret = usb_enable(NULL);
```

Starts the USB device stack. In `prj.conf`, this example uses:

```conf
CONFIG_USB_DEVICE_INITIALIZE_AT_BOOT=n
```

So USB is not initialized automatically at boot. The application must call `usb_enable(NULL)` from `main()`.

One-sentence summary: `usb_enable(NULL)` starts the USB device so the computer can see it.

```c
if (ret != 0) {
	printk("USB device initialization failed: %d\n", ret);
	return 0;
}
```

Checks whether USB started successfully. If it failed, the program prints the error code and exits `main()`.

One-sentence summary: this block catches USB initialization failure.

```c
printk("XIAO SAMD21 DAC example started\n");
```

Prints a startup message. If you see this line, `main()` is running and USB console output works.

One-sentence summary: this line is the visible signal that the program started correctly.

```c
while (1) {
	printk("Console heartbeat\n");
	k_msleep(HEARTBEAT_INTERVAL_MS);
}
```

This is an infinite loop. Embedded programs usually keep running instead of exiting.

The loop prints `Console heartbeat` once per second. Seeing repeated messages means the program is still alive.

One-sentence summary: the loop proves the program is still running by printing once per second.

### 11.4 Build Verification

After editing, rebuild:

```bash
/Users/mengdu/zephyrproject/.venv/bin/west build \
  -b seeeduino_xiao \
  -s /Users/mengdu/Desktop/Seeed-Zephyr-Project/examples/boards/xiao_samd21/dac \
  -d /Users/mengdu/Desktop/Seeed-Zephyr-Project/build/xiao_samd21_dac \
  -p always
```

If the build succeeds, the minimal `main.c` has valid syntax and dependencies.

One-sentence summary: this step verifies that the C code builds; it does not yet verify runtime behavior on the board.

### 11.5 Flashing and Expected Serial Output

After a successful build, the UF2 file is:

```text
/Users/mengdu/Desktop/Seeed-Zephyr-Project/build/xiao_samd21_dac/zephyr/zephyr.uf2
```

After flashing it to XIAO SAMD21 and opening the serial port, the expected output is:

```text
XIAO SAMD21 DAC example started
Console heartbeat
Console heartbeat
Console heartbeat
```

If you see these messages, three things are working:

1. `main()` is running.
2. USB device support is started.
3. `printk()` reaches the computer through USB console.

One-sentence summary: heartbeat output proves that later ADC voltage prints will have a reliable output path.

### 11.6 What Comes Next

Next, we will add the DAC API. We will first output a fixed voltage, such as a middle value, before generating a sine wave.

One-sentence summary: first make one fixed output work, then add dynamic waveform logic.

## 12. Add DAC Output with a Fixed Voltage First

This section starts using the DAC.

DAC means Digital-to-Analog Converter. In simple terms, your program writes a number, such as `512`, and the DAC turns that number into a real voltage.

One-sentence summary: a DAC turns a number in your program into a voltage on a pin.

### 12.1 What This Step Does

Do not start with the sine wave yet. First, make XIAO SAMD21 output one fixed middle value on A0/D0.

The reason is practical: if a fixed value does not work, a sine wave will not be reliable either. A fixed value is easier to measure and easier to debug.

The goals of this section are:

1. Find the DAC device from Zephyr.
2. Configure the DAC channel.
3. Write the fixed value `512` to the DAC.
4. Measure the voltage between A0/D0 and GND with a multimeter. With the current default DAC reference source, the expected voltage for `512` is close to `0.5V`.

One-sentence summary: this step only verifies whether the DAC can output a voltage.

### 12.2 Where These Values Come From

This step uses three key values:

```c
#define DAC_NODE DT_NODELABEL(dac0)
#define DAC_CHANNEL_ID 0
#define DAC_RESOLUTION 10
```

They are not guessed.

`dac0` comes from the Zephyr devicetree. The XIAO SAMD21 board devicetree file is:

```text
/Users/mengdu/zephyrproject/zephyr/boards/seeed/seeeduino_xiao/seeeduino_xiao.dts
```

It contains:

```dts
&dac0 {
	status = "okay";

	pinctrl-0 = <&dac_default>;
	pinctrl-names = "default";
};
```

This means the DAC controller is enabled for the XIAO SAMD21 board.

One-sentence summary: `dac0` is the devicetree name of the SAMD21 DAC controller.

`DAC_CHANNEL_ID 0` comes from the SAMD21 DAC driver:

```text
/Users/mengdu/zephyrproject/zephyr/drivers/dac/dac_sam0.c
```

The driver checks:

```c
if (channel_cfg->channel_id != 0) {
	return -EINVAL;
}
```

This means the SAMD21 DAC only accepts channel `0`.

One-sentence summary: SAMD21 has one DAC output channel here, so the channel ID is `0`.

`DAC_RESOLUTION 10` also comes from the same driver:

```c
if (channel_cfg->resolution != 10) {
	return -ENOTSUP;
}
```

This means the Zephyr SAMD21 DAC driver accepts 10-bit resolution.

10-bit means the usable value range is `0` to `1023`, giving `1024` levels.

One-sentence summary: the XIAO SAMD21 DAC is used as a 10-bit DAC here, with values from `0` to `1023`.

### 12.3 Why the Output Pin Is A0/D0

The XIAO connector mapping file is:

```text
/Users/mengdu/zephyrproject/zephyr/boards/seeed/seeeduino_xiao/seeed_xiao_connector.dtsi
```

It contains:

```dts
gpio-map = <0 0 &porta 2 0>,		/* D0 */
```

This means XIAO D0 maps to the SAMD21 chip pin `PA2`.

The pinctrl file is:

```text
/Users/mengdu/zephyrproject/zephyr/boards/seeed/seeeduino_xiao/seeeduino_xiao-pinctrl.dtsi
```

It contains:

```dts
dac_default: dac_default {
	group1 {
		pinmux = <PA2B_DAC_VOUT>;
	};
};
```

This means `PA2` can be switched to `DAC_VOUT`, which is the DAC voltage output function.

Putting the two facts together:

1. XIAO D0 is SAMD21 `PA2`.
2. SAMD21 `PA2` can work as `DAC_VOUT`.
3. Therefore, XIAO D0/A0 is the DAC output pin.

One-sentence summary: D0/A0 is proven by the XIAO connector mapping and the SAMD21 pinctrl file.

### 12.4 Replace main.c

Replace `examples/boards/xiao_samd21/dac/src/main.c` with this code:

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

One-sentence summary: this code starts USB output and keeps the DAC output value at `512` on A0/D0.

### 12.5 main.c Line-by-Line Explanation

```c
#include <zephyr/device.h>
```

This includes Zephyr's device model.

The device model is like Zephyr's hardware address book. Hardware blocks such as ADC, DAC, UART, and GPIO are registered there. When your program wants to use one hardware block, it first gets the device object from this address book.

One-sentence summary: `device.h` lets the program get hardware device objects from Zephyr.

```c
#include <zephyr/drivers/dac.h>
```

This includes the DAC driver API.

An API is like a set of ready-made buttons. You do not need to operate chip registers directly; you can call `dac_channel_setup()` and `dac_write_value()`.

One-sentence summary: `dac.h` provides the functions used to operate the DAC.

```c
#define DAC_NODE DT_NODELABEL(dac0)
```

`DT_NODELABEL(dac0)` means: find the devicetree node named `dac0`.

The devicetree is like a hardware description book. `dac0` is the DAC controller registered in that book.

One-sentence summary: this line tells the C code to find the DAC controller from devicetree.

```c
#define DAC_CHANNEL_ID 0
#define DAC_RESOLUTION 10
#define DAC_MID_VALUE 512
```

`DAC_CHANNEL_ID 0` means the program uses DAC channel 0.

`DAC_RESOLUTION 10` means the DAC uses 10-bit output resolution.

`DAC_MID_VALUE 512` is the value to output. A 10-bit DAC range is `0` to `1023`, and `512` is around the middle.

The current code does not configure the DAC reference voltage separately. The SAMD21 DAC driver uses the internal reference source by default, so `512` should output something close to `0.5V`. This is the stable baseline used by the tutorial for the next steps.

One-sentence summary: these three lines define which DAC to use, what resolution to use, and what value to output.

```c
static const struct device *const dac_dev = DEVICE_DT_GET(DAC_NODE);
```

This line gets the DAC device object from the devicetree node.

You can think of it like this: after finding `dac0` in the hardware address book, the program stores its contact information in `dac_dev` so later DAC functions can use it.

One-sentence summary: `dac_dev` is the device object passed to DAC functions.

```c
static const struct dac_channel_cfg dac_cfg = {
	.channel_id = DAC_CHANNEL_ID,
	.resolution = DAC_RESOLUTION,
};
```

This is the DAC channel configuration.

`struct dac_channel_cfg` is a structure defined by Zephyr. A structure is like a small form with named fields.

This code fills two fields:

1. `.channel_id`: which DAC channel to use.
2. `.resolution`: how many bits of output resolution to use.

One-sentence summary: `dac_cfg` is the configuration form for the DAC channel.

```c
if (!device_is_ready(dac_dev)) {
	printk("DAC device is not ready\n");
	return 0;
}
```

This checks whether the DAC device is ready.

The devicetree says `status = "okay"`, which means the device can be included in the build. At runtime, the program still checks whether the driver initialization succeeded.

One-sentence summary: devicetree says the device can be used; `device_is_ready()` checks whether it is actually ready now.

```c
ret = dac_channel_setup(dac_dev, &dac_cfg);
```

This applies `dac_cfg` to the DAC channel.

The `&` before `dac_cfg` means “give the function the address of this configuration form”. The function reads `channel_id` and `resolution` from that address.

One-sentence summary: `dac_channel_setup()` configures the DAC channel.

```c
ret = dac_write_value(dac_dev, DAC_CHANNEL_ID, DAC_MID_VALUE);
```

This writes the value `512` to the DAC.

If the DAC is like an electronic volume knob, `0` is the minimum, `1023` is the maximum, and `512` is around half scale.

One-sentence summary: `dac_write_value()` is the action that makes A0/D0 output the voltage.

```c
while (1) {
	printk("DAC output is holding value: %u\n", DAC_MID_VALUE);
	k_msleep(HEARTBEAT_INTERVAL_MS);
}
```

After one DAC write, the output holds that value. This loop does not repeatedly update the DAC. It only prints a status message once per second so you can see that the program is still running.

One-sentence summary: the loop keeps telling the computer that the program is alive and the DAC value is being held.

### 12.6 Build Command

After editing, rebuild:

```bash
/Users/mengdu/zephyrproject/.venv/bin/west build \
  -b seeeduino_xiao \
  -s /Users/mengdu/Desktop/Seeed-Zephyr-Project/examples/boards/xiao_samd21/dac \
  -d /Users/mengdu/Desktop/Seeed-Zephyr-Project/build/xiao_samd21_dac \
  -p always
```

This is the same command as before:

`west build` is the Zephyr build command.

`-b seeeduino_xiao` selects the XIAO SAMD21 board.

`-s .../dac` selects the `dac` example source directory.

`-d .../build/xiao_samd21_dac` selects the build output directory.

`-p always` regenerates the build directory every time to reduce stale-configuration issues.

One-sentence summary: this command compiles the `dac` example into firmware for XIAO SAMD21.

### 12.7 Flashing and Measurement

After a successful build, the UF2 file is:

```text
/Users/mengdu/Desktop/Seeed-Zephyr-Project/build/xiao_samd21_dac/zephyr/zephyr.uf2
```

Flash it to XIAO SAMD21.

Then measure with a multimeter:

1. Connect the black probe to `GND`.
2. Connect the red probe to `A0/D0`.
3. The expected voltage is close to `0.5V`.

At the same time, open the serial port. The expected output is:

```text
XIAO SAMD21 DAC example started
DAC fixed output value: 512
DAC output is holding value: 512
DAC output is holding value: 512
```

If serial output works and A0/D0 is close to `0.5V`, this step is working.

One-sentence summary: this section works when serial output is normal and A0/D0 measures close to `0.5V`.

### 12.8 What Comes Next

Next, we will learn the DAC reference voltage. You have verified that keeping the default DAC reference source gives stable USB output and a stable voltage close to `0.5V` on A0/D0.

We will continue from this stable baseline. First make the voltage move within the default reference range, then study more advanced reference-voltage configuration later.

One-sentence summary: continue from the stable baseline first, then study more advanced reference sources.

## 13. Understand DAC Reference Voltage and Keep the Stable Baseline

The measured `0.5V` is not a failure. It shows that the program did write to the DAC, and that the current DAC reference source is the internal reference.

Reference voltage is like the “top mark” of the DAC scale. If the top mark is about `1V`, the 10-bit middle value `512` is close to `0.5V`.

One-sentence summary: writing the same value `512` produces different voltages depending on the DAC reference voltage.

### 13.1 Why It Is 0.5V Now

The SAMD21 DAC driver file is:

```text
/Users/mengdu/zephyrproject/zephyr/drivers/dac/dac_sam0.c
```

It contains the reference source mapping:

```c
#define SAM0_DAC_REFSEL_0 DAC_CTRLB_REFSEL_INT1V_Val
#define SAM0_DAC_REFSEL_1 DAC_CTRLB_REFSEL_AVCC_Val
#define SAM0_DAC_REFSEL_2 DAC_CTRLB_REFSEL_VREFP_Val
```

These lines mean:

1. Reference source 0 is the internal `1V` reference.
2. Reference source 1 is `AVCC`, the chip analog supply.
3. Reference source 2 is the external reference input.

The driver also contains:

```c
#define SAM0_DAC_REFSEL(n) \
	COND_CODE_1(DT_INST_NODE_HAS_PROP(n, reference), \
		    (DT_INST_ENUM_IDX(n, reference)), (0))
```

This means: if the devicetree provides the `reference` property, the driver uses that value; if not, it uses the default value `0`.

Default value `0` maps to `INT1V`, so `512` producing about `0.5V` is a reasonable result.

One-sentence summary: the voltage is `0.5V` now because the devicetree does not set the DAC reference, so the driver defaults to the internal about-`1V` reference.

### 13.2 Where to Check Valid reference Values

The DAC devicetree binding file is:

```text
/Users/mengdu/zephyrproject/zephyr/dts/bindings/dac/atmel,sam0-dac.yaml
```

It defines the allowed `reference` values:

```yaml
reference:
  type: string
  description: Reference voltage source
  enum:
    - "intref"
    - "vddana"
    - "vrefa"
```

This means Zephyr can choose different reference sources in devicetree. This tutorial keeps the default internal reference first because it has already been verified as stable on XIAO SAMD21.

One-sentence summary: to know what a devicetree property can contain, read the corresponding binding YAML file; this tutorial keeps the verified default reference source first.

### 13.3 What the Current Stable Baseline Is

The current stable baseline has three parts:

1. `app.overlay` enables USB console and ADC channel 4.
2. `main.c` uses `dac_channel_setup()` to configure DAC channel 0 with 10-bit resolution.
3. The DAC reference source stays at the driver default, so `512` outputs about `0.5V`.

This follows the same idea as Zephyr's official DAC sample: first use the board-defined DAC output pin and verify the DAC device, channel, and resolution.

One-sentence summary: the stable baseline is to make DAC output work with the default reference first, then add more features step by step.

### 13.4 The Judgment Method You Learned Here

For peripherals such as DAC and ADC, where numbers and voltages are converted, use this order:

1. Check the resolution. For example, 10-bit means `0` to `1023`.
2. Check the reference voltage. For example, the current default internal reference is about `1V`.
3. Estimate the voltage with “current value / maximum value × reference voltage”.

This case is:

```text
512 / 1023 × 1V ≈ 0.5V
```

One-sentence summary: voltage conversion depends on the written value, the resolution, and the reference voltage together.

## 14. Change the Fixed Output into a Ramp Waveform

Now we will make the DAC voltage move.

In the previous section, the program wrote `512` once, so A0/D0 stayed close to `0.5V`. In this section, the program writes values from `0` to `1023`, then goes back to `0`, and repeats.

This waveform is called a sawtooth wave. In simple terms, it climbs upward step by step like stairs, jumps back to the bottom, and climbs again.

One-sentence summary: this section changes a fixed voltage into a voltage that rises and resets repeatedly.

### 14.1 What to Modify

Modify only this file:

```text
/Users/mengdu/Desktop/Seeed-Zephyr-Project/examples/boards/xiao_samd21/dac/src/main.c
```

Do not change `app.overlay` or `prj.conf`.

The DAC device, channel, USB console, and Kconfig options already work. This step only changes the values written to the DAC in `main.c`.

One-sentence summary: keep the hardware configuration unchanged and only change how the C code updates the DAC value.

### 14.2 Replace main.c

Replace `main.c` with this code:

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

One-sentence summary: this code makes the DAC value rise from `0` to `1023`, then return to `0`.

### 14.3 What the New Macros Mean

```c
#define DAC_MAX_VALUE ((1U << DAC_RESOLUTION) - 1U)
```

This calculates the maximum DAC value.

`1U << DAC_RESOLUTION` means shifting the number `1` left by `DAC_RESOLUTION` bits. Here `DAC_RESOLUTION` is `10`, so the result is:

```text
1 << 10 = 1024
```

DAC values start from `0`, so the maximum value is not `1024`; it is `1023`. That is why the expression subtracts `1`.

One-sentence summary: a 10-bit DAC has `1024` levels, and the largest value number is `1023`.

```c
#define DAC_STEP_DELAY_MS 2
```

This means the program waits `2ms` after writing each DAC value.

If the delay is too short, the waveform changes too fast to observe easily. If the delay is too long, the waveform changes very slowly. `2ms` is a simple learning value.

One-sentence summary: `DAC_STEP_DELAY_MS` controls how fast the voltage rises.

```c
#define DAC_LOG_INTERVAL 128
```

This means the program prints once every `128` values.

Printing after every DAC write would flood the serial output. With this interval, the program prints key values such as `0`, `128`, `256`, and `384`.

One-sentence summary: `DAC_LOG_INTERVAL` reduces serial output volume.

### 14.4 How the USB Monitor Check Works

```c
static bool console_is_connected(void)
```

This helper reads `UART_LINE_CTRL_DTR`. DTR is a serial-port connection signal.
In simple terms, the host monitor raises this signal when it opens the USB CDC
port.

`log_dac_status()` prints only while that signal is active. When the monitor is
opened or reopened, it prints the startup line once and then reports the current
DAC value. The waveform keeps running when the monitor is closed.

The loop still ends with `k_msleep(DAC_STEP_DELAY_MS)`. This gives the Zephyr
scheduler regular opportunities to run USB work while the DAC ramp continues.

See [Runtime Loop Timing for Upload and Monitor](../boards/xiao-samd21.md#runtime-loop-timing-for-upload-and-monitor)
for the board-level upload and monitor behavior.

One-sentence summary: the DAC keeps running continuously, while recurring logs
are sent only to an active serial monitor.

### 14.5 What value Means

```c
uint32_t value = 0;
```

`value` is the current number written to the DAC.

`uint32_t` is an integer type. In simple terms, it is a box that stores non-negative whole numbers. Here it stores DAC values from `0` to `1023`.

One-sentence summary: `value` is the number that represents the current output voltage.

### 14.6 What Happens in the while Loop

```c
ret = dac_write_value(dac_dev, DAC_CHANNEL_ID, value);
```

This writes the current `value` to the DAC.

If `value` is `0`, the output is close to the lowest voltage. If `value` is `512`, the output is close to the middle voltage. If `value` is `1023`, the output is close to the top of the current reference range.

One-sentence summary: this line turns the current number into a voltage on A0/D0.

```c
if ((value % DAC_LOG_INTERVAL) == 0U) {
	log_dac_status(value, &console_was_connected);
}
```

`%` means remainder. For example, `256 % 128` is `0`, so `256` gets printed. `257 % 128` is not `0`, so `257` does not get printed.

This checks the monitor connection and keeps the serial output readable instead
of printing every single value.

One-sentence summary: this block prints the status only at selected values.

```c
if (value >= DAC_MAX_VALUE) {
	value = 0;
} else {
	value++;
}
```

This controls how the value changes.

If `value` has reached the maximum `1023`, the next value becomes `0`. Otherwise, `value` increases by `1`.

`value++` means “increase `value` by 1”.

One-sentence summary: this block makes the value rise and reset at the top.

```c
k_msleep(DAC_STEP_DELAY_MS);
```

After writing one value, the program waits `2ms` before writing the next value.

One-sentence summary: this line controls the waveform speed.

### 14.7 Build and Verify

Rebuild:

```bash
/Users/mengdu/zephyrproject/.venv/bin/west build \
  -b seeeduino_xiao \
  -s /Users/mengdu/Desktop/Seeed-Zephyr-Project/examples/boards/xiao_samd21/dac \
  -d /Users/mengdu/Desktop/Seeed-Zephyr-Project/build/xiao_samd21_dac \
  -p always
```

After flashing, the serial output should look like:

```text
XIAO SAMD21 DAC ramp example started
DAC ramp value: 0
DAC ramp value: 128
DAC ramp value: 256
DAC ramp value: 384
DAC ramp value: 512
```

If you measure A0/D0 with a multimeter, the reading may jump or show an average value. A multimeter updates slowly and is not suitable for viewing a fast waveform. To see the actual sawtooth shape, use an oscilloscope.

With the current XIAO SAMD21 default DAC reference source, observing D0/A0 changing roughly between `0.1V` and `1V` means the ramp output is working.

One-sentence summary: if the serial output shows increasing values, the DAC is outputting the ramp waveform.

### 14.8 What Comes Next

Next, we will change the linear ramp into a sine table. The Arduino example calculates `sin(x)` directly. In embedded projects, a stable and common approach is to prepare a sine table first, then write the table values repeatedly.

One-sentence summary: first learn dynamic output with a sawtooth wave, then move to a sine wave.
