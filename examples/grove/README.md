# examples/grove

## English

This directory contains **board-agnostic** Zephyr examples for Seeed Grove modules.

Each Grove module has a single example tree that builds for every XIAO board with an
upstream Zephyr board target. The same source compiles unchanged across chips because
the examples program against the upstream `seeed_xiao_connector` abstraction:

- `app.overlay` references the connector labels `xiao_i2c`, `xiao_spi`, `xiao_serial`,
  and `xiao_d` instead of any board-specific pin.
- Each XIAO board's `seeed_xiao_connector.dtsi` maps those labels to its own I2C/SPI/UART
  controller and GPIO pins, so the build for a given board applies that board's mapping.

### Directory layout

```text
examples/grove/<grove_module_id>/<demo>/
  CMakeLists.txt
  prj.conf              # board-agnostic Kconfig
  app.overlay           # board-agnostic overlay, references xiao_i2c etc.
  boards/               # optional per-board overlay/conf tweaks
  example.yaml          # Grove example metadata contract
  src/main.c
  README.md
```

### `example.yaml` contract

```yaml
id: grove_scd41_basic_read
kind: grove
module_id: grove_scd41_co2_temperature_humidity_sensor
demo: basic_read
interface: i2c            # i2c | spi | uart | gpio | analog
connector: xiao
pin_policy: fixed-bus     # fixed-bus | selectable
excluded_boards:          # default: all boards; list exceptions here
  - xiao_esp32c5
expected_behavior: Prints CO2, temperature, and humidity every five seconds.
```

For `pin_policy: selectable` modules (GPIO/analog), add a `pins:` list of roles with
`default` and `allowed` pin sets. Fixed-bus modules (I2C/SPI/UART) need no pin selection.
Use an inline list for `allowed`, for example `allowed: [D0, D1, D2]`. Board-specific
selectable pin limits use `excluded_on_<board_id>` inside the role entry.

```yaml
pins:
  - role: signal
    default: D2
    allowed: [D0, D1, D2, D3]
    excluded_on_xiao_esp32c6: [D0]
```

### Building

```bash
seeed-zephyr build xiao_esp32c6 grove/<module>/<demo>
seeed-zephyr build xiao_nrf52840 grove/<module>/<demo>   # same source, another board
```

### Contributing a new Grove example

Author the overlay against the connector labels (`xiao_i2c`, `xiao_spi`, `xiao_serial`,
`xiao_d`) so the example stays board-agnostic. Place any board-specific deviation in a
`boards/<board_target>.overlay` or `.conf` file alongside the shared source. Run
`python3 tools/validate_metadata/validate.py` to check the `example.yaml` contract, and
`python3 tools/build_matrix/run_grove.py --example grove/<module>/<demo>` to record the
build status matrix into `metadata/status/`.

## 中文

这个目录保存 Seeed Grove 模块的**板级无关** Zephyr 示例。

每个 Grove 模块只有一份示例代码，可在所有具备上游 Zephyr board target 的 XIAO 板上构建。
示例面向上游 `seeed_xiao_connector` 抽象编程，因此同一份源码跨芯片无需修改：

- `app.overlay` 引用 connector 标签 `xiao_i2c`、`xiao_spi`、`xiao_serial`、`xiao_d`，
  不写任何板级专用引脚。
- 每块 XIAO 板的 `seeed_xiao_connector.dtsi` 把这些标签映射到自身的 I2C/SPI/UART 控制器
  与 GPIO 引脚，构建哪块板就套用哪块板的映射。

### 目录结构

```text
examples/grove/<grove_module_id>/<demo>/
  CMakeLists.txt
  prj.conf              # 板级无关 Kconfig
  app.overlay           # 板级无关 overlay，引用 xiao_i2c 等
  boards/               # 可选：按板差异 overlay/conf
  example.yaml          # Grove 示例元数据契约
  src/main.c
  README.md
```

### `example.yaml` 契约

```yaml
id: grove_scd41_basic_read
kind: grove
module_id: grove_scd41_co2_temperature_humidity_sensor
demo: basic_read
interface: i2c            # i2c | spi | uart | gpio | analog
connector: xiao
pin_policy: fixed-bus     # fixed-bus | selectable
excluded_boards:          # 默认全板支持，此处列例外
  - xiao_esp32c5
expected_behavior: Prints CO2, temperature, and humidity every five seconds.
```

`pin_policy: selectable` 的模块（GPIO/模拟）需额外声明 `pins:` 角色列表，含 `default` 与
`allowed` 引脚集合；fixed-bus 模块（I2C/SPI/UART）无需选引脚。
`allowed` 使用行内列表，例如 `allowed: [D0, D1, D2]`。按板限制可选引脚时，
在对应角色内使用 `excluded_on_<board_id>`。

```yaml
pins:
  - role: signal
    default: D2
    allowed: [D0, D1, D2, D3]
    excluded_on_xiao_esp32c6: [D0]
```

### 构建

```bash
seeed-zephyr build xiao_esp32c6 grove/<module>/<demo>
seeed-zephyr build xiao_nrf52840 grove/<module>/<demo>   # 同一份源码，换块板
```

### 新增 Grove 示例

overlay 请面向 connector 标签（`xiao_i2c`、`xiao_spi`、`xiao_serial`、`xiao_d`）编写，保持板级
无关；个别板的差异放进 `boards/<board_target>.overlay` 或 `.conf`。运行
`python3 tools/validate_metadata/validate.py` 校验 `example.yaml` 契约，并运行
`python3 tools/build_matrix/run_grove.py --example grove/<module>/<demo>` 把构建状态矩阵
写入 `metadata/status/`。
