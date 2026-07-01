<div align="center">

<img src="docs/assets/logo.png" alt="Seeed Zephyr Base logo" width="140" />

# Seeed Zephyr Base

**The XIAO + Grove example library, capability catalog, and command-line workflow for [Zephyr RTOS](https://www.zephyrproject.org/).**

Discover what a Seeed Studio XIAO board can build on Zephyr, see which examples are verified, and go from a fresh checkout to flashing firmware with a single command.

[![Metadata Validation](https://github.com/limengdu/Seeed-Zephyr-Project/actions/workflows/metadata.yml/badge.svg)](https://github.com/limengdu/Seeed-Zephyr-Project/actions/workflows/metadata.yml)
[![Zephyr](https://img.shields.io/badge/Zephyr-v4.4.0-7929d3)](https://docs.zephyrproject.org/4.4.0/)
[![Boards](https://img.shields.io/badge/XIAO%20boards-11%20tracked-00979d)](#supported-boards)
[![Platform](https://img.shields.io/badge/host-macOS%20%7C%20Linux%20%7C%20Windows-blue)](#quick-start)

[Quick Start](#quick-start) · [Supported Boards](#supported-boards) · [CLI](#command-line-workflow) · [Documentation](#documentation) · [Roadmap](#roadmap)

**English** · [简体中文](README.zh-CN.md)

</div>

---

## Overview

XIAO is a multi-chip ecosystem. Different XIAO boards use different silicon vendors, wireless stacks, SDKs, flashing tools, and development workflows. Zephyr is becoming the shared technical base across these boards — and this repository adds the XIAO + Grove product experience on top of it.

Upstream Zephyr answers one question: *"Can this board run Zephyr?"*

**Seeed Zephyr Base answers the next ones:**

> What can a XIAO + Grove user actually build on Zephyr? Which examples are verified on real hardware? And how do I build and flash one without first learning Devicetree, Kconfig, and `west`?

You get the smallest verified example for each supported board, board and Grove capability metadata, a build matrix that proves what compiles, and a thin `seeed-zephyr` CLI that picks the right board target and example for you — then hands the real work to standard Zephyr tooling.

## Highlights

- **🧩 One example per board** — minimal, buildable demos for every tracked XIAO board, ready to flash.
- **⚡ Single-command workflow** — `seeed-zephyr build | flash | monitor | debug <board>` works from any directory after setup.
- **🔌 Auto board handling** — UF2 mode entry, DFU, PyOCD, and 1200-baud bootloader requests are handled per board, so you don't memorize each vendor's flash dance.
- **📇 Capability catalog** — structured metadata for XIAO boards, Grove modules, and expansion boards.
- **✅ Honest validation** — every board ships with a build-matrix result, and hardware-tested boards are marked as such.
- **🌍 Bilingual docs** — getting-started guides and board notes in English and 中文.
- **🤖 Thin by design** — the CLI is a repository knowledge layer; firmware build, flash, monitor, and debug always run through Zephyr `west` and vendor tools.

## Supported Boards

Status is taken from the [board build matrix](tools/build_matrix/results.md) against the Zephyr **v4.4.0** baseline.

| Board | Vendor | Zephyr target | Example | Status |
| --- | --- | --- | --- | --- |
| XIAO SAMD21 | Microchip | `seeeduino_xiao` | `blinky` | 🔵 Hardware-tested |
| XIAO nRF52840 | Nordic | `xiao_ble` | `blinky` | 🔵 Hardware-tested |
| XIAO nRF54L15 | Nordic | `xiao_nrf54l15/nrf54l15/cpuapp` | `blinky` | 🔵 Hardware-tested |
| XIAO MG24 | Silabs | `xiao_mg24` | `blinky` | 🔵 Hardware-tested |
| XIAO RP2040 | Raspberry Pi | `xiao_rp2040` | `blinky` | 🔵 Hardware-tested |
| XIAO RP2350 | Raspberry Pi | `xiao_rp2350/rp2350a/m33` | `blinky` | 🔵 Hardware-tested |
| XIAO ESP32-C6 | Espressif | `xiao_esp32c6/esp32c6/hpcore` | `blinky` | 🔵 Hardware-tested |
| XIAO ESP32-S3 | Espressif | `xiao_esp32s3/esp32s3/procpu` | `blinky` | 🔵 Hardware-tested |
| XIAO ESP32-C3 | Espressif | `xiao_esp32c3` | `hello_world` | 🔵 Hardware-tested · no on-board LED |
| XIAO RA4M1 | Renesas | `xiao_ra4m1` | `blinky` | 🔵 Hardware-tested · USB DFU |
| XIAO ESP32-C5 | Espressif | `xiao_esp32c5` | `hello_world` | ⛔ No target in v4.4.0 |

**Legend** — 🔵 verified on real hardware · 🟢 builds cleanly in CI · ⛔ tracked, but the selected Zephyr baseline provides no board target yet.

Board-specific flashing, reset, and bootloader behavior is documented in [board notes](docs/en/boards/README.md).

## Quick Start

You don't need to clone this repository to use the tools — install everything from published channels.

> **Where things live:** the `seeed-zephyr` CLI is installed on your `PATH`, and the Zephyr source tree, SDK, and `west` workspace live in `~/zephyrproject`. The installer prepares both for you.

### 1. Install the CLI and Zephyr environment

The one-line installer sets up the `seeed-zephyr` CLI **and** the full Zephyr toolchain (SDK, `west` workspace, and per-board flash tools). It runs on macOS and Linux (use it inside WSL2 on Windows):

```sh
curl -fsSL https://raw.githubusercontent.com/Seeed-Projects/seeed-zephyr-base/main/install.sh | bash
```

Set up a single board by passing `--board` through the pipe:

```sh
curl -fsSL https://raw.githubusercontent.com/Seeed-Projects/seeed-zephyr-base/main/install.sh | bash -s -- --board xiao_esp32c6
```

Prefer to install just the CLI? Use PyPI, [pipx](https://pipx.pypa.io/), or [Homebrew](https://brew.sh/), then set up the Zephyr toolchain from the [Getting Started guide](docs/en/getting-started.md#2b-zephyr-environment-setup):

```sh
pip install seeed-zephyr                        # all platforms
pipx install seeed-zephyr
brew install seeed-studio/seeed/seeed-zephyr    # macOS / Linux
```

On Windows without WSL2, follow the PowerShell setup in the [Getting Started guide](docs/en/getting-started.md).

### 2. Install the editor extension

The **Seeed XIAO Zephyr Assistant** browses boards and examples with validation badges and runs Build / Flash / Monitor from the editor. Install it from the Extensions view of Cursor, Windsurf, VSCodium, Gitpod, or Eclipse Theia — search **Seeed XIAO Zephyr** — or from the [Open VSX listing](https://open-vsx.org/extension/seeed-studio/seeed-xiao-zephyr-assistant).

### 3. Build your first example

Run the CLI from any directory:

```sh
seeed-zephyr build xiao_esp32c6
```

The CLI reads the board metadata, finds the matching example, and calls Zephyr's `west build` with the validated target.

### Uninstall

Remove the `seeed-zephyr` command and, if you choose, the Zephyr workspace and SDK:

```sh
bash uninstall.sh
```

It removes the `seeed-zephyr` CLI symlink, then asks before removing the Zephyr workspace (`~/zephyrproject`) and SDK. Shared build tools installed with Homebrew or your Linux package manager are listed with removal commands rather than removed for you. Add `--yes` to remove the workspace and SDK without prompting, or `--dry-run` to preview.

## Command-Line Workflow

`seeed-zephyr` chooses the board, example, and validated metadata, then delegates the actual device work to Zephyr tooling.

### Build, flash, monitor, debug

```sh
seeed-zephyr build   xiao_esp32c6
seeed-zephyr flash   xiao_esp32c6
seeed-zephyr monitor xiao_esp32c6
seeed-zephyr debug   xiao_esp32c6
```

Flash, then jump straight into the serial monitor:

```sh
seeed-zephyr flash xiao_esp32c6 --monitor
```

### Choose an example

When a board has more than one example, the CLI lists them and lets you pick. Name the example to skip the prompt:

```sh
seeed-zephyr build xiao_esp32c6 blinky
```

### Build an external application

Point the CLI at any Zephyr app folder (one with `CMakeLists.txt` and `prj.conf`):

```sh
seeed-zephyr flash xiao_esp32c6 --app ~/my-zephyr-app --monitor
```

### Discover what's available

```sh
seeed-zephyr list boards
seeed-zephyr list examples
```

### Serial monitor, no board required

Interactive port and baud-rate selection:

```sh
seeed-zephyr monitor
```

### Maintainer commands

```sh
seeed-zephyr matrix                     # rebuild the full board build matrix
seeed-zephyr verify-hardware xiao_esp32c6  # record a hardware observation
```

For the complete walk-through, see the [Getting Started guide](docs/en/getting-started.md).

## Grove & Expansion Support

The capability catalog also tracks the Grove modules and expansion boards that pair with XIAO, including their interface, default address, power rail, and the Zephyr driver and Kconfig options they need.

**Grove modules:** AS5600 magnetic rotary encoder · GPS (Air530) · GSR sensor · Ultrasonic Ranger

**Expansion boards:** Grove Shield for XIAO · XIAO Expansion Board · XIAO Round Display

See [`metadata/`](metadata/) for the full, machine-readable catalog.

## Build From Source

Working on the examples, metadata, or the CLI itself? Clone the repository and run the setup script directly. This also unlocks the maintainer commands (`matrix`, `verify-hardware`) and the in-repo `scripts/seeed-zephyr` launcher.

```sh
git clone https://github.com/limengdu/Seeed-Zephyr-Project.git
cd Seeed-Zephyr-Project
bash scripts/setup-macos.sh        # or scripts/setup-linux.sh
```

Windows (WSL2):

```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup-windows.ps1
```

Setup prepares the Zephyr workspace, installs the Python venv and `west`, downloads Zephyr v4.4.0 and the SDK, fetches per-board flash tools, and offers to install the `seeed-zephyr` CLI. Pass `--board <target>` to limit board-specific downloads to one board.

## Repository Structure

```text
Seeed-Zephyr-Project/
├── examples/boards/      # Minimal, buildable demo per XIAO board
├── metadata/             # Board, Grove module, and expansion-board catalog
│   ├── boards/
│   ├── grove_modules/
│   └── expansion_boards/
├── scripts/              # Cross-platform setup + the seeed-zephyr launcher
├── tools/
│   ├── cli/              # seeed-zephyr CLI implementation
│   ├── build_matrix/     # Full board-demo build verification
│   └── validate_metadata/# Metadata schema checks (run in CI)
├── docs/                 # User-facing guides and per-board notes (EN + 中文)
└── .github/workflows/    # CI: metadata validation
```

## Roadmap

The project is being built in three layers, each enabling the next.

1. **Examples, metadata & validation base** *(in progress)* — minimal board examples, reusable XIAO + Grove project examples, the capability catalog, the build matrix, CI verification, and selected hardware-in-the-loop tests.
2. **Discovery & generation CLI** *(in progress)* — `seeed-zephyr` discovers boards, examples, Grove modules, and expansion boards (with `--json` output), shows asset details, validates metadata, and generates a project from any example with a reproducible `snapshot.json`. Scenario templates and west / PlatformIO output are next.
3. **VS Code product experience** *(MVP in progress)* — the [Seeed XIAO Zephyr Assistant extension](tools/vscode-extension/) browses boards, modules, and expansion boards with validation badges, previews example details, creates a project from an example, and offers PlatformIO-style status bar Build / Upload / Monitor actions that delegate execution to Zephyr tooling. Wiring diagrams and deeper official-extension integration are next.

The guiding principle: examples and projects are the product core; metadata, the CLI, generators, and editor tooling exist to make those examples easy to find, build, validate, and extend.

## Documentation

| English | 中文 |
| --- | --- |
| [Getting Started](docs/en/getting-started.md) | [入门指南](docs/zh/getting-started.md) |
| [Board Notes](docs/en/boards/README.md) | [开发板说明](docs/zh/boards/README.md) |

Per-board notes cover flashing, reset, bootloader, and serial specifics for SAMD21, nRF52840, MG24, RA4M1, RP2040, and RP2350.

## Contributing

Contributions of new board examples, Grove modules, project examples, and validation evidence are welcome. Metadata is validated automatically on every push and pull request via the [Metadata Validation workflow](.github/workflows/metadata.yml), so keep new catalog entries schema-valid and back build/hardware status with evidence rather than assumptions.

## Acknowledgements

Built on the [Zephyr Project](https://www.zephyrproject.org/) and the [Seeed Studio XIAO](https://www.seeedstudio.com/xiao-series-page) and [Grove](https://wiki.seeedstudio.com/Grove_System/) ecosystems.
