# Phase 1: Zephyr Base

## 1. Goal

Phase 1 builds the reliable technical foundation for XIAO, Grove, expansion boards, and Zephyr.

The goal is not to create a polished user interface. The goal is to create a trustworthy source of truth that future tools can use.

By the end of this phase, Seeed should know:

- which XIAO boards work well with Zephyr
- which features are supported, experimental, blocked, or unknown
- which Grove modules can be represented in a reusable way
- which examples compile
- which examples run on real hardware
- which Zephyr version should be recommended

One-sentence summary: Phase 1 turns scattered Zephyr support into a structured, testable, and reusable foundation.

## 2. Core Principle

The foundation should be upstream-friendly and product-focused.

It should not become a private fork of Zephyr. A long-running Seeed-specific Zephyr fork would create upgrade friction, split the user experience, and make security maintenance harder.

Instead:

- board and driver fixes should be contributed upstream when possible
- temporary patches should be clearly tracked
- Seeed-specific product metadata should live in this repository
- examples should use normal Zephyr project structure
- Grove integration should use Zephyr-native concepts where practical

One-sentence summary: use upstream Zephyr as the base, and add Seeed's product layer around it.

## 3. Repository Responsibilities

This repository should own the following data and assets.

### XIAO Board Metadata

Each board should have a machine-readable metadata file.

Example fields:

```yaml
id: xiao_esp32c6
display_name: Seeed Studio XIAO ESP32C6
zephyr_target: seeed_xiao_esp32c6
vendor: espressif
status: experimental
recommended_zephyr_version: v4.1.0
interfaces:
  gpio: tested
  i2c: tested
  spi: build-only
  uart: tested
  adc: unknown
  pwm: unknown
  wifi: experimental
  ble: experimental
  usb: tested
power:
  deep_sleep: unknown
validation:
  build: passed
  hardware: partial
known_issues:
  - id: esp32c6_wifi_pm_unverified
    severity: medium
    summary: Wi-Fi power management is not yet validated against ESP-IDF behavior.
```

One-sentence summary: board metadata is the board's machine-readable status card.

### Grove Module Metadata

Each Grove module should also have a metadata file.

Example fields:

```yaml
id: grove_sht40
display_name: Grove Temperature and Humidity Sensor SHT40
category: sensor
interface: i2c
default_address: "0x44"
zephyr_driver: sht4x
required_configs:
  - CONFIG_SENSOR=y
  - CONFIG_SHT4X=y
supported_templates:
  - sensor_to_serial
  - sensor_to_mqtt
wiring:
  power: 3v3
  signals:
    sda: xiao_i2c.sda
    scl: xiao_i2c.scl
validation:
  build: passed
  hardware: tested
```

One-sentence summary: Grove metadata lets software tools understand a physical module without manual explanation.

### Expansion-Board Metadata

Expansion boards should be treated as first-class objects because Grove users often connect modules through a shield or expansion board.

Example fields:

```yaml
id: xiao_grove_shield
display_name: XIAO Grove Shield
compatible_form_factor: xiao
ports:
  - id: i2c_0
    type: i2c
    label: Grove I2C
    maps_to: xiao_i2c
  - id: d0
    type: gpio
    label: Grove D0
    maps_to: gpio_d0
```

One-sentence summary: expansion-board metadata tells the system where the user can plug modules in.

### Examples and Samples

Initial samples should be small and diagnostic.

Recommended baseline samples:

- blinky
- button
- serial_log
- i2c_scan
- adc_read
- pwm_fade
- sensor_basic
- ble_beacon
- wifi_mqtt

The first set should focus on the shortest useful path:

```text
build -> flash -> boot -> log -> peripheral -> Grove module
```

One-sentence summary: baseline samples are health checks for boards and modules.

### Compatibility Matrix

The compatibility matrix should be generated or validated from metadata and CI results.

Status terms should be explicit:

- `tested`: verified on real hardware
- `build-only`: compile validation passed, but hardware is not tested
- `experimental`: expected to work, but not stable enough to recommend
- `blocked`: known issue prevents normal use
- `unsupported`: not supported by design or hardware limitations
- `unknown`: not yet evaluated

One-sentence summary: the matrix should tell the truth, not just advertise support.

## 4. Suggested Directory Structure

```text
metadata/
  boards/
  grove_modules/
  expansion_boards/
  templates/
  compatibility/

samples/
  blinky/
  serial_log/
  i2c_scan/
  sensor_basic/

overlays/
  grove/
  expansion_boards/

templates/
  west-basic/
  west-sensor/
  platformio-basic/
  platformio-sensor/

tools/
  validate_metadata/
  build_matrix/
  render_docs/

tests/
  compile_matrix/
  hardware_matrix/

docs/
  board-matrix.md
  grove-matrix.md
  getting-started.md
```

One-sentence summary: keep facts, samples, templates, tools, tests, and documentation in separate drawers.

## 5. Validation Strategy

### Build Validation

Every supported board and sample combination should be compiled by CI where practical.

Build validation answers:

```text
Does this project compile with the recommended Zephyr version?
Did a metadata or template change break any generated project?
Which board, module, or template caused the failure?
```

One-sentence summary: build validation catches broken examples before users find them.

### Hardware-in-Loop Validation

Hardware-in-loop means the system tests real boards and real Grove modules instead of only compiling code.

The first hardware tests should be simple:

- flash success
- boot success
- serial output contains expected text
- I2C scan finds expected address
- sensor value is present and within a reasonable range

Hardware-in-loop should start with a small number of high-value combinations.

One-sentence summary: real hardware tests prove that examples work beyond the compiler.

### Power and Performance Validation

Zephyr should not be assumed to match vendor SDK performance automatically.

For selected boards, compare:

- boot time
- firmware size
- RAM usage
- active current
- sleep current
- wake-up time
- Wi-Fi or BLE stability

The goal is not always to beat vendor SDKs. The goal is to know where Zephyr is good enough and where vendor SDKs remain the better recommendation.

One-sentence summary: performance data prevents Zephyr from becoming a blind strategic bet.

## 6. Version Strategy

Zephyr changes frequently. Users need reproducible builds.

Recommended policy:

- choose a recommended Zephyr release or LTS line
- lock sample and template validation to that version
- test upgrades on a schedule
- keep experimental branches separate from user-facing releases
- document which version each matrix result uses

One-sentence summary: stable users need pinned versions, not moving targets.

## 7. Phase 1 Success Criteria

Phase 1 should be considered successful when:

- at least five representative XIAO boards have metadata
- at least ten high-frequency Grove modules have metadata
- at least one expansion board is represented
- baseline samples compile in CI
- selected combinations pass hardware validation
- compatibility status is visible and reproducible
- Zephyr limitations are documented honestly

One-sentence summary: Phase 1 succeeds when Seeed can prove what works, what does not, and what is still unknown.

## 8. Phase 1 Non-Goals

Phase 1 should not include:

- a full online IDE
- a full VS Code plugin
- a full Wokwi-style simulator
- a large Seeed-specific SDK abstraction
- all XIAO boards
- all Grove modules
- complex Matter, AI, or camera projects

One-sentence summary: Phase 1 should stay focused on evidence and foundation.
