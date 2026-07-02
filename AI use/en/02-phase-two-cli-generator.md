# Phase 2: CLI For Discovery, Build, Validation, And Generation

## 1. Goal

Phase 2 turns the example/project base into a practical command-line tool.

The CLI is the shared engine that helps users, CI, maintainers, AI agents, and
future UI tools discover, build, validate, copy, and generate projects from
repository assets.

One-sentence summary: Phase 2 makes the example and project catalog usable from
one repeatable command interface.

## 2. Required Capabilities

The CLI should support five workflows.

### Discover

```bash
seeed-zephyr list boards
seeed-zephyr list grove
seeed-zephyr list capabilities
seeed-zephyr list examples
seeed-zephyr list projects
```

One-sentence summary: users should be able to find content before generating
anything.

### Inspect

```bash
seeed-zephyr show board xiao_esp32c6
seeed-zephyr show example boards/xiao_esp32c6/blinky
seeed-zephyr show project xiao_esp32c6_grove_scd41_lcd_dashboard
```

One-sentence summary: the CLI should explain what an asset needs and what its
validation status is.

### Build And Flash Repository Assets

```bash
seeed-zephyr build xiao_esp32c6
seeed-zephyr flash xiao_esp32c6
seeed-zephyr flash xiao_esp32c6 --monitor
seeed-zephyr build-project xiao_esp32c6_grove_scd41_lcd_dashboard
```

Build, flash, monitor, and debug execution should be delegated to Zephyr `west`
commands or Zephyr module-provided tools. The CLI should select repository
assets and validated metadata, then pass them to Zephyr tooling.

One-sentence summary: users should build repository assets through the CLI, and
the CLI should use Zephyr tooling for execution.

### Validate Contributions

```bash
seeed-zephyr validate metadata
seeed-zephyr validate example examples/grove/grove_scd41_co2_temperature_humidity_sensor/basic_read
seeed-zephyr validate project projects/xiao_esp32c6_grove_scd41_lcd_dashboard
```

One-sentence summary: community examples and projects need automated structure
and build checks.

### Generate New Projects

```bash
seeed-zephyr create \
  --from example/grove/grove_scd41_co2_temperature_humidity_sensor/basic_read \
  --board xiao_esp32c6 \
  --output ./my-scd41-project
```

Generation should copy and adapt known-good assets. Drivers, pin routing, and
source code should come from verified templates, examples, or Zephyr-native
files.

One-sentence summary: generation is based on validated examples, templates, and
evidence.

## 3. Deterministic Generation Rule

The CLI must use:

- metadata
- repository examples
- repository projects
- templates
- validation evidence
- compatibility rules

Large language models may help explain or choose options. Repository metadata,
templates, examples, and validation evidence remain the authority for generated
source, overlays, pins, and configuration.

One-sentence summary: correctness comes from checked repository assets and
evidence.

## 4. Project Snapshot

Every generated or copied project should include a snapshot such as:

```json
{
  "generator": "seeed-zephyr",
  "source_asset": "examples/grove/grove_scd41_co2_temperature_humidity_sensor/basic_read",
  "board": "xiao_esp32c6",
  "zephyr_version": "v4.4.0",
  "validation_status": "build-only"
}
```

One-sentence summary: generated projects need a receipt so support teams and AI
agents can reproduce them.

## 5. Phase 2 Success Criteria

Phase 2 succeeds when:

- users can list and inspect examples/projects
- users can build at least the first board examples from the repository root
- contributors can validate example structure before submitting
- CI can call the same CLI commands
- generated projects come from known examples/templates
- error messages are specific and actionable
- the CLI is reusable by a future VS Code plugin

One-sentence summary: Phase 2 succeeds when the repository content becomes easy
to operate and validate.

## 6. Phase 2 Delivery Boundary

Phase 2 work is accepted through command-line workflows that operate repository
assets:

- discovery commands for boards, modules, examples, projects, and status
- inspection commands that show wiring, build targets, expected output, and evidence
- validation commands for metadata, example structure, and project structure
- build orchestration commands that call the selected Zephyr workspace
- project creation commands that copy from known templates or examples
- machine-readable receipts for generated or validated outputs
- stable output contracts that future editor tools can consume

One-sentence summary: Phase 2 is complete when repository assets can be found,
checked, built, generated, and reported through predictable CLI commands.
