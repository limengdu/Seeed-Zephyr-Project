# Getting Started: Build Repository Examples

Short version: this repository now contains its own XIAO board demos under
`examples/boards/`. Users should build those repository examples first.

Think of the work in two folders:

| Path | What it is | What it is used for |
| --- | --- | --- |
| `~/seeed-zephyr-base` | This project | XIAO/Grove examples, metadata, scripts, docs, and validation results |
| `~/zephyrproject` | Upstream Zephyr workspace | Zephyr source, SDK, west workspace, and firmware build output |

One-sentence summary: run setup from `~/seeed-zephyr-base`; after the CLI is
installed, use `seeed-zephyr` from any directory.

## 1. What This Project Solves

Zephyr is an embedded operating system for microcontrollers. It already supports
many boards, but users still need to know board targets, Devicetree, Kconfig,
west, SDKs, and vendor blobs.

This repository adds the XIAO/Grove layer:

- `examples/boards/`: minimum demos for each tracked XIAO board
- `metadata/boards/`: board ids, names, vendors, and Zephyr targets
- `scripts/`: setup, CLI, and example build helpers
- `tools/build_matrix/`: full board-demo build verification
- `docs/`: user-facing instructions
- `AI use/`: AI-facing project charter and handoff logs

One-sentence summary: Zephyr is the engine; this repository gives XIAO users
organized examples and repeatable commands.

## 2. Install the CLI

Four ways to install. Pick the one that fits your workflow.

### Option A: pip (all platforms)

```sh
pip install seeed-zephyr
```

Or with [pipx](https://pipx.pypa.io/) for isolated installation:

```sh
pipx install seeed-zephyr
```

After installing the CLI via pip, you still need the Zephyr toolchain. See
[Section 2b](#2b-zephyr-environment-setup) below.

### Option B: One-line installer (macOS / Linux)

This installs the CLI **and** sets up the Zephyr environment in one step:

```sh
curl -fsSL https://raw.githubusercontent.com/limengdu/Seeed-Zephyr-Project/main/install.sh | bash
```

After this completes, skip to [Section 3](#3-build-one-board-demo).

### Option C: Homebrew (macOS / Linux)

```sh
brew tap limengdu/seeed
brew install limengdu/seeed/seeed-zephyr
```

After installing the CLI via Homebrew, you still need the Zephyr toolchain.
See [Section 2b](#2b-zephyr-environment-setup) below.

### Option D: From source (contributor workflow)

Clone the repository and run the setup script for your OS.

```sh
cd ~/seeed-zephyr-base
bash scripts/setup-macos.sh
```

If you already know the board, pass `--board`:

```sh
cd ~/seeed-zephyr-base
bash scripts/setup-macos.sh --board xiao_esp32c6
```

#### Other platforms

Linux:

```sh
cd ~/seeed-zephyr-base
bash scripts/setup-linux.sh
```

Windows (WSL2):

```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup-windows.ps1
```

Then run Linux setup inside WSL2:

```sh
cd ~/seeed-zephyr-base
bash scripts/setup-linux.sh
```

During setup, the script asks:

```text
Install seeed-zephyr CLI? [Y/n]
```

Press Enter to install the CLI. The setup script also prepares the full Zephyr
environment, so you can skip Section 2b.

## 2b. Zephyr Environment Setup

If you installed the CLI via pip or Homebrew (Options A or C), you still need
the Zephyr toolchain. The one-line installer (Option B) and from-source setup
(Option D) handle this automatically.

The Zephyr workspace at `~/zephyrproject` contains the Python venv, `west`,
Zephyr v4.4.0, Zephyr packages, the SDK, and board-specific blobs. Set it up
by cloning the repository and running the setup script for your OS:

```sh
git clone https://github.com/limengdu/Seeed-Zephyr-Project.git ~/.seeed-zephyr-base

# macOS
bash ~/.seeed-zephyr-base/scripts/setup-macos.sh

# Linux
bash ~/.seeed-zephyr-base/scripts/setup-linux.sh
```

The setup flow prepares the Zephyr workspace, installs the Python venv and
`west`, downloads Zephyr v4.4.0, installs Zephyr packages and the SDK, and
fetches board-specific blobs when needed. When an Espressif board is selected
with `--board`, setup also checks that Zephyr's `hal_espressif` flash and
monitor tools are available. For other boards, setup prepares the required
flash tools, such as `bossac` for SAMD21, the PyOCD CMSIS pack for MG24, and
`dfu-util` for RA4M1.

One-sentence summary: install the CLI first, then set up the Zephyr toolchain
if the installer did not handle it.

## 3. Build One Board Demo

Build a demo from any directory after CLI installation:

```sh
seeed-zephyr build xiao_esp32c6
```

For XIAO ESP32-C3, use `hello_world` because the board has no on-board LED:

```sh
seeed-zephyr build xiao_esp32c3
```

`seeed-zephyr build <board_id>` reads the board metadata, finds the repository
example, and calls Zephyr's `west build` with the validated target and example
path.

If you installed from source and skipped CLI installation, the project-root
fallback is `scripts/seeed-zephyr <command>`.

One-sentence summary: the installed command works outside the repository, while
Zephyr still performs the actual firmware build.

### Build a Grove example on any board

Grove module examples live under `examples/grove/` and are board-agnostic: one source
tree builds for every XIAO board through the upstream `seeed_xiao_connector` abstraction.
Pass the board, then the `grove/<module>/<demo>` reference:

```sh
seeed-zephyr build xiao_esp32c6  grove/grove_scd41_co2_temperature_humidity_sensor/basic_read
seeed-zephyr build xiao_nrf52840 grove/grove_scd41_co2_temperature_humidity_sensor/basic_read
```

The same source builds on both boards unchanged. Inspect the per-pin state exported for
editor tooling with:

```sh
seeed-zephyr show pins xiao_esp32c6 grove/grove_scd41_co2_temperature_humidity_sensor/basic_read
```

## 4. Useful CLI Commands

List boards and examples:

```sh
seeed-zephyr list boards
seeed-zephyr list examples
```

Build, flash, monitor, and debug:

```sh
seeed-zephyr build xiao_esp32c6
seeed-zephyr flash xiao_esp32c6
seeed-zephyr monitor xiao_esp32c6
seeed-zephyr debug xiao_esp32c6
```

Build, flash, and then open the monitor:

```sh
seeed-zephyr flash xiao_esp32c6 --monitor
seeed-zephyr flash xiao_samd21 --monitor
seeed-zephyr flash xiao_rp2040 --monitor
```

Run the full build matrix:

```sh
seeed-zephyr matrix
```

Record a hardware observation:

```sh
seeed-zephyr verify-hardware xiao_esp32c6
```

Refresh the CLI, examples, and metadata:

```sh
seeed-zephyr update
seeed-zephyr update --version 0.3.0
seeed-zephyr info
```

Bootstrap older installations with the original install channel once:

```sh
brew update && brew upgrade seeed-zephyr
python3 -m pip install --upgrade seeed-zephyr
pipx upgrade seeed-zephyr
curl -fsSL https://raw.githubusercontent.com/limengdu/Seeed-Zephyr-Project/main/install.sh | bash
```

One-sentence summary: the CLI is the normal entry point for operating repository
examples.

## 5. Board Demo Matrix

The table below is generated by `tools/build_matrix/run.sh`.

| Board | board target | repository example | v4.4.0 status | Notes |
| --- | --- | --- | --- | --- |
| XIAO SAMD21 | `seeeduino_xiao` | `examples/boards/xiao_samd21/blinky` | PASS | Hardware-tested |
| XIAO nRF52840 | `xiao_ble` | `examples/boards/xiao_nrf52840/blinky` | PASS | Hardware-tested; repeated flash auto-requests UF2 |
| XIAO ESP32-C3 | `xiao_esp32c3` | `examples/boards/xiao_esp32c3/hello_world` | PASS | Hardware-tested; no on-board LED |
| XIAO ESP32-C5 | `xiao_esp32c5` | `examples/boards/xiao_esp32c5/hello_world` | UNSUPPORTED | Zephyr v4.4.0 has no XIAO target |
| XIAO ESP32-C6 | `xiao_esp32c6/esp32c6/hpcore` | `examples/boards/xiao_esp32c6/blinky` | PASS | Hardware-tested |
| XIAO ESP32-S3 | `xiao_esp32s3/esp32s3/procpu` | `examples/boards/xiao_esp32s3/blinky` | PASS | Hardware-tested |
| XIAO MG24 | `xiao_mg24` | `examples/boards/xiao_mg24/blinky` | PASS | Hardware-tested; uses Zephyr's PyOCD runner by default |
| XIAO nRF54L15 | `xiao_nrf54l15/nrf54l15/cpuapp` | `examples/boards/xiao_nrf54l15/blinky` | PASS | Hardware-tested |
| XIAO RA4M1 | `xiao_ra4m1` | `examples/boards/xiao_ra4m1/blinky` | PASS | Hardware-tested; uses USB DFU bootloader |
| XIAO RP2040 | `xiao_rp2040` | `examples/boards/xiao_rp2040/blinky` | PASS | Hardware-tested; repeated flash auto-requests UF2 |
| XIAO RP2350 | `xiao_rp2350/rp2350a/m33` | `examples/boards/xiao_rp2350/blinky` | PASS | Hardware-tested; M33 target |

`UNSUPPORTED` means the selected Zephyr v4.4.0 baseline does not provide that
XIAO board target. XIAO ESP32-C5 has a repository demo record, but it cannot be
built until the selected Zephyr baseline provides a real `xiao_esp32c5` target.

One-sentence summary: 10 current targets build repository demos; XIAO ESP32-C5
is tracked but unsupported in the selected baseline.

## 6. Flash The Board

After a successful build, flash through the CLI:

```sh
seeed-zephyr flash xiao_esp32c6
```

`flash` always builds before flashing. To open the monitor after a successful
flash, use:

```sh
seeed-zephyr flash xiao_esp32c6 --monitor
```

ESP32 boards may require manual bootloader entry before flashing. ESP32 logs can
be monitored with:

```sh
seeed-zephyr monitor xiao_esp32c6
```

For non-Espressif boards, the CLI opens pyserial miniterm from the Zephyr venv:

```sh
seeed-zephyr monitor xiao_samd21
```

If `--port` is omitted, the CLI tries to auto-detect one USB serial device.

For XIAO SAMD21 repeated flashing and BOSSA auto-reset behavior, see
[XIAO SAMD21 Board Notes](boards/xiao-samd21.md).

For XIAO RP2040 UF2 flashing and USB CDC monitor behavior, see
[XIAO RP2040 Board Notes](boards/xiao-rp2040.md).

For XIAO nRF52840 UF2 flashing and 1200 baud bootloader-entry behavior, see
[XIAO nRF52840 Board Notes](boards/xiao-nrf52840.md).

For XIAO MG24 PyOCD flashing and CMSIS pack requirements, see
[XIAO MG24 Board Notes](boards/xiao-mg24.md).

For XIAO RA4M1 USB DFU flashing and application start address, see
[XIAO RA4M1 Board Notes](boards/xiao-ra4m1.md).

To start a Zephyr debug session when suitable hardware debugger support is
connected, run:

```sh
seeed-zephyr debug xiao_esp32c6
```

One-sentence summary: the CLI chooses the repository example, then Zephyr's
`west build`, `west flash`, `west debug`, module tools, and Zephyr venv serial
tools do the actual device work.

## 7. Maintainer Commands

Validate metadata:

```sh
cd ~/seeed-zephyr-base
/Users/mengdu/zephyrproject/.venv/bin/python tools/validate_metadata/validate.py
```

Rebuild the full board demo matrix:

```sh
seeed-zephyr matrix
```

One-sentence summary: maintainers use metadata validation and the build matrix
to keep the example catalog honest.

## 8. Common Errors

### `west: command not found`

Run the setup script or activate the Zephyr venv:

```sh
source ~/zephyrproject/.venv/bin/activate
```

One-sentence summary: if the shell cannot find `west`, the Zephyr venv is not
active.

### `No board named ...`

Check whether the selected Zephyr baseline provides the board target:

```sh
cd ~/zephyrproject
source .venv/bin/activate
west boards | grep -i xiao
```

One-sentence summary: missing boards are usually spelling issues or board
targets that are not in the selected Zephyr release.

### `blinky` cannot find `led0`

Use a non-LED demo for boards without an on-board LED:

```sh
seeed-zephyr build xiao_esp32c3
```

One-sentence summary: not every XIAO board is a valid LED blink board.

### `esptool` cannot be found during ESP32 flashing

Rerun setup so the Zephyr venv and CLI environment are refreshed:

```sh
cd ~/seeed-zephyr-base
bash scripts/setup-macos.sh --board xiao_esp32c6
```

One-sentence summary: ESP32 flashing and monitor use Zephyr's `hal_espressif`
tools, and the CLI exposes the Zephyr venv to those tools.

### UF2 Storage Volume Not Found

For RP2040, RP2350, or nRF52840 boards, make sure a UF2 mass-storage volume is
visible, then rerun the flash command:

```sh
seeed-zephyr flash xiao_nrf52840 --monitor
```

For XIAO RP2040, XIAO RP2350, or XIAO nRF52840 running a repository example
that supports automatic UF2 entry, the CLI normally requests UF2 mode through
USB CDC at 1200 baud.

If the current firmware does not support that request, or no USB CDC serial
port is visible:

- XIAO RP2040 / XIAO RP2350: hold BOOTSEL while plugging in USB, or hold BOOTSEL
  and press RESET.
- XIAO nRF52840: double-tap `RESET`, then wait for the UF2 storage volume.

The repository CLI uses Zephyr's `uf2` runner, so normal nRF52840 UF2 flashing
does not require installing `nrfutil`.

One-sentence summary: UF2 boards still flash by copying to a bootloader storage
drive; after running a repository example, the CLI first tries to request that
mode automatically through 1200 baud.
