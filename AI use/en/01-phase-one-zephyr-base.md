# Phase 1: Examples, Projects, Metadata, And Validation Base

## 1. Goal

Phase 1 creates the trustworthy base of the repository.

Phase 1 proves upstream Zephyr builds and creates repository-owned examples and
projects that users can find, build, flash, learn from, and contribute to.

By the end of Phase 1, the repository should answer:

- Which XIAO boards have minimal Zephyr examples here?
- Which board capabilities have examples here?
- Which Grove modules have examples here?
- Which expansion boards have examples here?
- Which complete projects exist here?
- Which examples are build-only, hardware-tested, blocked, unsupported, or unknown?
- Which Zephyr version was used as evidence?

One-sentence summary: Phase 1 turns scattered Zephyr support into a verified
XIAO + Grove example and project base.

## 2. Non-Negotiable Product Principle

The repository's user-facing assets are examples and projects.

Metadata, scripts, setup instructions, build matrices, and future generators
exist to support examples and projects.

Every Phase 1 task should improve at least one of these:

- an example a user can build
- a project a user can study or modify
- validation evidence for an example or project
- contribution quality for future examples and projects
- metadata that helps users discover or validate examples and projects

One-sentence summary: Phase 1 priority work makes examples, projects,
validation, or contribution clearer.

## 3. Repository Assets

### Board Examples

Board examples prove one board capability at a time.

Recommended categories:

- `hello_world`
- `blinky` when the board has an LED
- `gpio`
- `button`
- `serial_log`
- `i2c_scan`
- `spi_loopback` or supported SPI device example
- `uart`
- `adc_read`
- `pwm_fade`
- `usb_cdc`
- `ble_beacon`
- `wifi_scan` or `wifi_mqtt`
- `display_basic`
- `storage_basic`
- `low_power_basic`

One-sentence summary: board examples are the smallest proof that a XIAO
capability works under Zephyr.

### Grove Examples

Grove examples show how one Grove module works with Zephyr and XIAO.

Recommended categories:

- `basic_read` for sensors
- `basic_control` for actuators
- `display_text` for displays
- `i2c_address_scan` or address confirmation where useful
- `interrupt` examples when the module supports it
- `calibration` examples when setup matters

One-sentence summary: Grove examples should let a user plug in a module and see
the first useful result.

### Expansion-Board Examples

Expansion-board examples show how a XIAO board uses a shield, display, button,
battery feature, or Grove port layout.

One-sentence summary: expansion-board examples prove the physical add-on board
is represented correctly.

### Complete Projects

Projects combine multiple parts into a real scenario.

Examples:

- XIAO ESP32C6 + Grove SCD41 + 1.47inch LCD dashboard
- XIAO nRF52840 + sensor + BLE broadcaster
- XIAO MG24 + button + low-power wake flow
- XIAO ESP32S3 + display + Wi-Fi dashboard

Projects should be more complete than minimal examples. They may include a
README, wiring notes, configuration choices, expected logs, and known limits.

One-sentence summary: projects show how building blocks become real user
outcomes.

## 4. Metadata Boundary

Metadata describes product-level facts:

- display names
- categories
- interfaces
- supported examples/projects
- documentation links
- default settings
- validation status
- known issues

Zephyr-native files describe hardware truth:

- Devicetree
- overlays
- shields
- Kconfig
- drivers

Keep pin routing in the Zephyr shield or overlay when those files own the
hardware truth.

One-sentence summary: metadata helps users discover and validate; Zephyr files
own hardware description.

## 5. Suggested Directory Structure

```text
examples/
  boards/
    xiao_esp32c3/
      hello_world/
    xiao_esp32c6/
      blinky/
      i2c_scan/
  grove/
    grove_scd41_co2_temperature_humidity_sensor/
      basic_read/
  expansion_boards/
    xiao_expansion_board/
      display_basic/

projects/
  xiao_esp32c6_grove_scd41_lcd_dashboard/

metadata/
  boards/
  grove_modules/
  expansion_boards/
  examples/
  projects/
  status/

boards/
  shields/

tools/
  validate_metadata/
  build_matrix/
  sync_status/

scripts/
  setup-macos.sh
  seeed-zephyr
  build-example.sh

docs/
  getting-started.md
  examples.md
  contributing-examples.md
```

One-sentence summary: `examples/` and `projects/` are user-facing assets;
metadata and tools keep them discoverable and honest.

## 6. Validation Strategy

Validation must be evidence-based.

Statuses:

- `hardware-tested`: built, flashed, and observed on real hardware
- `build-only`: compiled successfully, no hardware test yet
- `experimental`: expected to work but not stable enough to recommend
- `blocked`: known issue prevents normal use
- `unsupported`: not supported by the selected Zephyr baseline or by hardware
- `unknown`: not evaluated yet

Rules:

- Status fields are derived from evidence.
- Each example and project should have a build target and expected result.
- Hardware-tested examples must record board, module, Zephyr version, date, and
  observed output.
- Community examples can be accepted as build-only first, then promoted when
  hardware evidence exists.

One-sentence summary: support claims are test outputs backed by evidence.

## 7. Community Contributions

The repository should be ready for outside examples and projects.

Every contributed example should include:

- supported board(s)
- required module(s) or expansion board(s)
- build command through project tooling
- expected serial output or visible behavior
- wiring notes when hardware is required
- validation status
- known limitations

One-sentence summary: community examples are welcome only when they are
structured enough to build, review, and validate.

## 8. Phase 1 Success Criteria

Phase 1 succeeds when:

- at least five representative XIAO boards have repository-owned examples
- at least ten high-frequency Grove modules have example plans or initial examples
- at least one expansion board has a working example
- at least three complete projects exist or are specified with clear acceptance criteria
- examples can be built from the repository root
- metadata validation passes
- the build matrix covers the first examples
- selected examples run on real hardware
- contribution rules are clear enough for an external author

One-sentence summary: Phase 1 succeeds when the repository is already useful as
an example and project hub before any polished UI exists.

## 9. Phase 1 Delivery Boundary

Phase 1 work is accepted through concrete repository assets:

- a board example under `examples/boards/`
- a Grove example under `examples/grove/`
- an expansion-board example under `examples/expansion_boards/`
- a complete project under `projects/`
- metadata that describes one of those assets
- validation evidence for one of those assets
- documentation that helps users build, flash, verify, or contribute those assets

Future product work enters Phase 1 as data contracts, template requirements,
validation records, or contribution rules that directly support examples and
projects.

One-sentence summary: Phase 1 work is finished when it leaves behind a concrete
example, project, metadata record, validation record, or contribution path.
