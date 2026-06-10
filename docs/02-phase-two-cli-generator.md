# Phase 2: CLI Generator

## 1. Goal

Phase 2 turns the Zephyr base into a deterministic project generator.

The command-line interface should let users and tools generate complete XIAO + Grove Zephyr projects from validated metadata and templates.

The CLI is not an AI code writer. It is a rules-based generator.

One-sentence summary: Phase 2 changes the foundation from "data that exists" into "projects that can be generated."

## 2. Why A CLI Comes Before A Plugin

A CLI is the best shared engine for future interfaces.

The same generator can be used by:

- VS Code plugin
- web project builder
- documentation generator
- CI validation
- AI assistant
- internal engineering scripts

If generation logic is written only inside a VS Code plugin, it becomes harder to test and reuse.

One-sentence summary: the CLI is the engine; graphical tools are steering wheels.

## 3. User Experience

Example command:

```bash
seeed-zephyr generate \
  --board xiao_esp32c6 \
  --expansion xiao_grove_shield \
  --grove grove_sht40 \
  --template sensor_to_serial \
  --toolchain west \
  --output ./xiao-sht40-demo
```

Expected output:

```text
xiao-sht40-demo/
  CMakeLists.txt
  prj.conf
  app.overlay
  README.md
  wiring.svg
  seeed-project.json
  src/
    main.c
```

One-sentence summary: the user describes hardware and intent, and the CLI writes a complete project.

## 4. Deterministic Generation

The generator should use:

- metadata
- templates
- compatibility rules
- validation rules

It should not ask a large language model to invent source code, drivers, overlays, or pin assignments.

Large language models may later explain errors or help users choose options, but the generated project itself must come from verified inputs.

One-sentence summary: correctness should come from verified templates, not from probabilistic code generation.

## 5. Generation Pipeline

The generator should follow a simple pipeline.

### Step 1: Validate Input

Check that:

- the board exists
- the Grove modules exist
- the expansion board exists
- the template exists
- requested options are allowed

One-sentence summary: first confirm the user's choices are real.

### Step 2: Resolve Compatibility

Check that:

- the board exposes required interfaces
- the expansion board maps those interfaces
- the Grove module can connect to one of those interfaces
- the template's required features are supported
- there are no pin or bus conflicts

One-sentence summary: then confirm the chosen parts can work together.

### Step 3: Compose Project Data

Combine:

- board metadata
- Grove metadata
- expansion-board metadata
- template metadata
- user settings
- recommended Zephyr version

One-sentence summary: this creates one complete project plan before any files are written.

### Step 4: Render Files

Render:

- source files
- Devicetree overlay
- prj.conf
- CMakeLists.txt
- west manifest or PlatformIO config
- README
- wiring diagram
- project metadata snapshot

One-sentence summary: file rendering turns the project plan into a real folder.

### Step 5: Verify Output

Optional verification modes:

```bash
seeed-zephyr verify ./xiao-sht40-demo
seeed-zephyr build ./xiao-sht40-demo
```

Verification should check:

- required files exist
- metadata snapshot is valid
- generated config is parseable
- project can build with the selected toolchain

One-sentence summary: the generator should check its own work.

## 6. Core Commands

Recommended first commands:

```bash
seeed-zephyr list boards
seeed-zephyr list grove
seeed-zephyr list expansions
seeed-zephyr list templates
seeed-zephyr check --board xiao_esp32c6 --grove grove_sht40
seeed-zephyr generate ...
seeed-zephyr build ./project
seeed-zephyr flash ./project
seeed-zephyr monitor ./project
```

One-sentence summary: the CLI should support discovery, generation, and common development tasks.

## 7. Template Types

Initial templates should focus on useful but simple scenarios.

Recommended first templates:

- `blinky`
- `button_to_serial`
- `sensor_to_serial`
- `relay_control`
- `i2c_scan`

Second-wave templates:

- `sensor_to_mqtt`
- `ble_sensor`
- `low_power_sensor`
- `home_assistant_mqtt`

One-sentence summary: start with simple local workflows, then add network and low-power scenarios.

## 8. Toolchain Outputs

### west Output

west is Zephyr's standard command-line workflow.

Generated west projects should include:

- `CMakeLists.txt`
- `prj.conf`
- `app.overlay`
- `src/main.c`
- README instructions for `west build`, `west flash`, and `west debug`

One-sentence summary: west support should be the reference path because it is closest to upstream Zephyr.

### PlatformIO Output

PlatformIO support should be added after west generation is stable.

Generated PlatformIO projects should include:

- `platformio.ini`
- Zephyr-specific project structure
- documentation for known PlatformIO differences

PlatformIO can be user-friendly, but it may lag behind upstream Zephyr or use different board IDs. The generator should expose that clearly.

One-sentence summary: PlatformIO is valuable, but west should remain the primary reference path.

## 9. Project Metadata Snapshot

Every generated project should include a snapshot file, for example:

```json
{
  "generator": "seeed-zephyr",
  "generator_version": "0.1.0",
  "board": "xiao_esp32c6",
  "expansion": "xiao_grove_shield",
  "grove": ["grove_sht40"],
  "template": "sensor_to_serial",
  "toolchain": "west",
  "zephyr_version": "v4.4.0",
  "generated_at": "2026-06-10T00:00:00Z"
}
```

This helps support teams reproduce user issues.

One-sentence summary: every generated project should carry a receipt of how it was created.

## 10. Error Design

CLI errors should be specific and actionable.

Bad:

```text
Generation failed.
```

Good:

```text
Grove SHT40 requires I2C, but the selected expansion board does not expose an I2C Grove port.
Choose XIAO Grove Shield or use custom wiring.
```

One-sentence summary: error messages should tell the user what happened and what to do next.

## 11. Phase 2 Success Criteria

Phase 2 should be considered successful when:

- the CLI can list supported boards, modules, expansions, and templates
- the CLI can generate complete west projects
- generated projects build in CI
- generated README files are understandable
- generated wiring diagrams are accurate for supported combinations
- at least several projects are flashed and tested on real hardware
- the generator is reusable by a future VS Code plugin

One-sentence summary: Phase 2 succeeds when generation is repeatable, testable, and useful outside one interface.

## 12. Phase 2 Non-Goals

Phase 2 should not include:

- a full graphical interface
- a browser-based IDE
- full AI code generation
- full hardware simulation
- all Grove modules
- all advanced Zephyr scenarios

One-sentence summary: Phase 2 should perfect the engine before adding a polished cockpit.
