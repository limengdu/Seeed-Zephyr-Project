# Seeed Zephyr Base

Seeed Zephyr Base is a strategic software foundation for the Seeed XIAO, Grove, and expansion-board ecosystem.

The project is not intended to replace the upstream Zephyr repository. Its purpose is to build a product-focused support layer around XIAO hardware: verified board metadata, Grove module descriptions, project templates, compatibility data, generation tools, and developer-facing workflows.

In simple terms, upstream Zephyr answers: "Can this board run Zephyr?"

This project answers: "Can a XIAO user choose a board, add Grove modules, generate a project, wire the hardware correctly, build it, flash it, and debug it with confidence?"

## Why This Exists

XIAO is becoming a multi-chip ecosystem. Different XIAO boards use different silicon vendors, wireless stacks, SDKs, flashing tools, and development workflows. Arduino remains important for beginner-friendly workflows, but new chips often support vendor SDKs or Zephyr before Arduino support is complete.

Zephyr can become the shared technical base for many XIAO boards, but Zephyr alone is not a complete product experience. It still expects users to understand board targets, Devicetree overlays, Kconfig options, west commands, toolchains, and driver details.

This repository defines the product layer that makes Zephyr practical for XIAO and Grove users.

## Strategic Position

The recommended position is Zephyr-first, not Zephyr-only.

Zephyr should become the default unified path for common XIAO projects, reusable samples, compatibility validation, Grove integration, and future developer tools. Vendor SDKs, Arduino, MicroPython, CircuitPython, and PlatformIO should remain available where they are the better fit.

## Three Phases

### Phase 1: Zephyr Base

Build the reliable foundation:

- XIAO board metadata
- Grove module metadata
- expansion-board metadata
- minimum Zephyr samples
- compatibility matrix
- CI build verification
- selected hardware-in-loop tests
- version and release policy

See [Phase 1: Zephyr Base](docs/01-phase-one-zephyr-base.md).

### Phase 2: CLI Generator

Turn the foundation into a deterministic project generator:

- generate west projects
- generate PlatformIO Zephyr projects
- compose board, Grove, expansion-board, and scenario templates
- output README, wiring data, overlays, configuration files, and source code
- avoid depending on large language models for correctness

See [Phase 2: CLI Generator](docs/02-phase-two-cli-generator.md).

### Phase 3: VS Code Plugin

Turn the CLI and metadata into a developer-facing product:

- select XIAO boards, Grove modules, and expansion boards
- display compatibility and validation status
- render wiring diagrams
- configure GPIO, I2C address, UART baud rate, sampling interval, and scenario settings
- generate projects
- hand off build, flash, monitor, and debug to the official Zephyr VS Code extension

See [Phase 3: VS Code Plugin](docs/03-phase-three-vscode-plugin.md).

## Repository Purpose

This repository should eventually become the single source of truth for:

- what XIAO boards support in Zephyr
- which Grove modules can be used with each board
- which examples are build-only, experimental, or hardware-tested
- how projects are generated
- how documentation and compatibility pages are produced
- which Zephyr versions are recommended

## Key Principle

Users should not need to become Zephyr experts before building a useful XIAO + Grove project.

The system should let users start from hardware and intent:

1. Select a XIAO board.
2. Select a Grove module or expansion board.
3. Select a project scenario.
4. Generate a working Zephyr project.
5. Build, flash, and verify it locally.

## Document Index

- [Executive Summary](docs/00-executive-summary.md)
- [Phase 1: Zephyr Base](docs/01-phase-one-zephyr-base.md)
- [Phase 2: CLI Generator](docs/02-phase-two-cli-generator.md)
- [Phase 3: VS Code Plugin](docs/03-phase-three-vscode-plugin.md)
- [Getting Started](docs/getting-started.md)
- [Roadmap and Risks](docs/04-roadmap-and-risks.md)
- [Glossary](docs/05-glossary.md)
