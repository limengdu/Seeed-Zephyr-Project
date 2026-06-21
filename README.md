# Seeed Zephyr Base

Seeed Zephyr Base is the Seeed XIAO + Grove Zephyr example library, project collection, capability catalog, validation knowledge base, and future project-generation foundation.

Its purpose is to make XIAO + Grove development on Zephyr discoverable, repeatable, and community-extensible. The repository should contain the smallest verified examples for supported XIAO boards, larger reusable project examples, board and Grove capability metadata, validation evidence, contribution rules, and developer-facing tools that are built from those assets.

In simple terms, upstream Zephyr answers: "Can this board run Zephyr?"

This project answers: "What can a XIAO + Grove user build with Zephyr, which examples are verified, and how can new examples be contributed safely?"

## Start Here

If you are new to this repository, start with the Getting Started guide before reading the phase documents:

- [English Getting Started](docs/en/getting-started.md)
- [English Board Notes](docs/en/boards/README.md)
- [中文入门指南](docs/zh/getting-started.md)
- [中文开发板说明](docs/zh/boards/README.md)

If you are an AI agent, maintainer, or contributor preparing project work, start with the AI project charter:

- [AI Project Charter](AI%20use/README.md)
- [AI Work Log](AI%20use/WORKLOG.md)

The short version: this repository stores XIAO/Grove examples, project examples, metadata, scripts, docs, and validation results. The actual Zephyr source tree and firmware builds live in a separate workspace, normally `~/zephyrproject`.

Run setup from the repository root. Choose the entry point for your host OS.
When setup asks `Install seeed-zephyr CLI? [Y/n]`, press Enter to install the
command.

macOS:

```sh
bash scripts/setup-macos.sh
```

Linux, written but pending real-Linux validation:

```sh
bash scripts/setup-linux.sh
```

Windows, written but pending real-Windows validation, prepares WSL2 first:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup-windows.ps1
```

Then run Linux setup inside WSL2:

```sh
bash scripts/setup-linux.sh
```

After setup installs the CLI, build a repository board demo from any directory:

```sh
seeed-zephyr build xiao_esp32c6
```

List supported boards and examples:

```sh
seeed-zephyr list boards
seeed-zephyr list examples
```

Build, flash, monitor, and start a debug session:

```sh
seeed-zephyr build xiao_esp32c6
seeed-zephyr flash xiao_esp32c6
seeed-zephyr monitor xiao_esp32c6
seeed-zephyr debug xiao_esp32c6
```

Flash and then open the monitor:

```sh
seeed-zephyr flash xiao_esp32c6 --monitor
seeed-zephyr flash xiao_samd21 --monitor
seeed-zephyr flash xiao_rp2040 --monitor
```

For XIAO MG24 flashing, the CLI uses Zephyr's PyOCD runner. See
[XIAO MG24 Board Notes](docs/en/boards/xiao-mg24.md).

The CLI selects repository examples and board metadata. Firmware build, flash,
monitor, and debug execution still run through Zephyr `west` commands and
Zephyr module tools. For non-Espressif serial monitor sessions, the CLI uses
pyserial miniterm from the Zephyr venv.

## Why This Exists

XIAO is becoming a multi-chip ecosystem. Different XIAO boards use different silicon vendors, wireless stacks, SDKs, flashing tools, and development workflows. Arduino remains important for beginner-friendly workflows, but new chips often support vendor SDKs or Zephyr before Arduino support is complete.

Zephyr can become the shared technical base for many XIAO boards. This repository adds the XIAO/Grove product experience around board targets, Devicetree overlays, Kconfig options, west commands, toolchains, and driver details.

This repository defines the example and validation layer that makes Zephyr practical for XIAO and Grove users. Project generators, CLIs, and editor extensions should be built from this layer.

## Strategic Position

The recommended position is Zephyr-first while keeping other ecosystems available where they are the better fit.

Zephyr should become the default unified path for common XIAO projects, reusable samples, compatibility validation, Grove integration, and future developer tools. Vendor SDKs, Arduino, MicroPython, CircuitPython, and PlatformIO should remain available where they are the better fit.

## Three Phases

### Phase 1: Examples, Projects, Metadata, And Validation Base

Build the reliable foundation:

- XIAO board metadata
- Grove module metadata
- expansion-board metadata
- minimum XIAO function examples
- reusable XIAO + Grove project examples
- compatibility matrix
- CI build verification
- selected hardware-in-loop tests
- contribution structure for external examples
- version and release policy

See [Phase 1: Examples, Projects, Metadata, And Validation Base](AI%20use/en/01-phase-one-zephyr-base.md).

### Phase 2: CLI For Discovery, Build, Validation, And Generation

Turn the foundation into a deterministic command-line workflow:

- list supported boards, modules, examples, projects, and validation status
- create new examples and project skeletons from repository templates
- generate west projects
- generate PlatformIO Zephyr projects
- build and validate selected examples
- compose board, Grove, expansion-board, and scenario templates
- output README, wiring data, overlays, configuration files, and source code
- base correctness on repository metadata, templates, and validation evidence

See [Phase 2: CLI For Discovery, Build, Validation, And Generation](AI%20use/en/02-phase-two-cli-generator.md).

### Phase 3: VS Code Product Experience

Turn the CLI and metadata into a developer-facing product:

- select XIAO boards, Grove modules, and expansion boards
- browse examples and project examples
- display compatibility and validation status
- render wiring diagrams
- configure GPIO, I2C address, UART baud rate, sampling interval, and scenario settings
- generate projects
- hand off build, flash, monitor, and debug to the official Zephyr VS Code extension

See [Phase 3: VS Code Product Experience](AI%20use/en/03-phase-three-vscode-plugin.md).

## Repository Purpose

This repository should eventually become the single source of truth for:

- what XIAO boards support in Zephyr
- which Grove modules can be used with each board
- which minimum examples exist for each supported XIAO board
- which larger XIAO + Grove project examples are available
- which examples are build-only, experimental, or hardware-tested
- how external contributors add examples and validation evidence
- how projects are generated
- how documentation and compatibility pages are produced
- which Zephyr versions are recommended

## Key Principle

Examples and project directories are the product core. Metadata, scripts, CLIs, generators, and editor extensions exist to make those examples easier to find, build, validate, and extend.

Users should be able to build a useful XIAO + Grove project before they understand every Zephyr detail.

The CLI should stay a thin repository knowledge layer. It can choose the board,
example, and validated metadata, but it must delegate build, flash, monitor,
and debug execution to Zephyr tooling.

The system should let users start from hardware and intent:

1. Select a XIAO board.
2. Select a Grove module or expansion board.
3. Browse a verified minimum example or project example.
4. Build, flash, and verify it locally.
5. Generate a new project from the same repository knowledge when the CLI or plugin supports it.

## Document Index

- [Executive Summary](AI%20use/en/00-executive-summary.md)
- [AI Project Charter](AI%20use/README.md)
- [AI Work Log](AI%20use/WORKLOG.md)
- [Phase 1: Examples, Projects, Metadata, And Validation Base](AI%20use/en/01-phase-one-zephyr-base.md)
- [Phase 2: CLI For Discovery, Build, Validation, And Generation](AI%20use/en/02-phase-two-cli-generator.md)
- [Phase 3: VS Code Product Experience](AI%20use/en/03-phase-three-vscode-plugin.md)
- [Onboarding and Distribution Design](AI%20use/en/onboarding-design.md)
- [Getting Started](docs/en/getting-started.md)
- [XIAO SAMD21 Board Notes](docs/en/boards/xiao-samd21.md)
- [XIAO MG24 Board Notes](docs/en/boards/xiao-mg24.md)
- [XIAO RP2040 Board Notes](docs/en/boards/xiao-rp2040.md)
- [Validation Log](AI%20use/en/validation-log.md)
- [Roadmap and Quality Controls](AI%20use/en/04-roadmap-and-risks.md)
- [Glossary](AI%20use/en/05-glossary.md)

## Chinese Documents

- [执行摘要](AI%20use/zh/00-executive-summary.md)
- [AI 项目纲领](AI%20use/README.md)
- [AI 工作记录](AI%20use/WORKLOG.md)
- [第一阶段: 示例、项目、元数据与验证基础](AI%20use/zh/01-phase-one-zephyr-base.md)
- [第二阶段: 发现、构建、验证与生成 CLI](AI%20use/zh/02-phase-two-cli-generator.md)
- [第三阶段: VS Code 产品体验](AI%20use/zh/03-phase-three-vscode-plugin.md)
- [入门指南](docs/zh/getting-started.md)
- [XIAO SAMD21 开发板说明](docs/zh/boards/xiao-samd21.md)
- [XIAO MG24 开发板说明](docs/zh/boards/xiao-mg24.md)
- [XIAO RP2040 开发板说明](docs/zh/boards/xiao-rp2040.md)
- [路线图与质量控制](AI%20use/zh/04-roadmap-and-risks.md)
- [术语表](AI%20use/zh/05-glossary.md)
