# Getting Started

Zephyr setup is easiest to understand as three pieces working together:

- the Zephyr source tree, fetched and updated by `west`
- the compiler and Zephyr SDK that turn source code into firmware
- the `west` command-line tool that drives fetch, build, flash, and monitor workflows

The goal of this guide is to build firmware for this project's XIAO boards and shields. A successful build is the first local proof that the board and shield metadata can point to real Zephyr targets.

## 1. Install Prerequisites

On macOS Apple Silicon, install Homebrew first, load it into the shell, and then install the packages required by Zephyr.

```sh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
(echo; echo 'eval "$(/opt/homebrew/bin/brew shellenv)"') >> ~/.zprofile
source ~/.zprofile
brew install cmake ninja gperf python3 python-tk ccache qemu dtc libmagic wget openocd
(echo; echo 'export PATH="'$(brew --prefix)'/opt/python/libexec/bin:$PATH"') >> ~/.zprofile
source ~/.zprofile
```

One-sentence summary: install the macOS tools that Zephyr needs before fetching or building any firmware.

## 2. Create A Python Virtual Environment And Install West

A Python virtual environment keeps Zephyr's Python packages separate from the rest of the system. Every new terminal must re-activate this environment before running Zephyr commands.

```sh
python3 -m venv ~/zephyrproject/.venv
source ~/zephyrproject/.venv/bin/activate
pip install west
```

After opening a new terminal, re-activate this same virtual environment before building.

One-sentence summary: create an isolated Python environment and install `west`, then re-activate it in every new terminal.

## 3. Get The Zephyr Source

This project's baseline is the latest stable Zephyr release, version 4.4. Pin it explicitly so builds are reproducible.

```sh
west init ~/zephyrproject --mr v4.4.0
cd ~/zephyrproject
west update
```

Most of this project's boards are available in the latest stable release. A few of the newest boards may exist only on the development branch, `main`. If `west boards | grep -i xiao` on the stable checkout does not list a board you need, that board is pending the next stable release. For temporary validation of such a board only, run `west init ~/zephyrproject` with no `--mr` to fetch `main` instead.

One-sentence summary: pin the latest stable release `v4.4.0` for reproducible builds, and fall back to `main` only for boards not yet in a stable release.

## 4. Export CMake, Install Python Dependencies, And Install The SDK

Exporting Zephyr lets CMake find the Zephyr package. The Python dependency command installs the packages used by Zephyr's scripts. The SDK installation downloads and installs the toolchains used to compile firmware, and it is several GB.

```sh
west zephyr-export
west packages pip --install
cd ~/zephyrproject/zephyr
west sdk install
```

One-sentence summary: connect Zephyr to CMake, install Zephyr's Python packages, and install the compiler SDK.

## 5. Fetch Board-Specific Binary Blobs

Only some XIAO chip families need Zephyr binary blobs. The macOS setup script derives the correct HAL module from `metadata/boards/<board_id>.yaml` by reading the board's `vendor:` value, then skips the fetch when `west blobs list <module>` is empty.

```sh
cd ~/seeed-zephyr-base
bash scripts/setup-macos.sh --board xiao_esp32c6
```

For manual setup, first map the board vendor to the Zephyr HAL module, then check whether that module has blobs before fetching. The example below uses the module for `xiao_esp32c6`; replace it with the module for your board vendor.

```sh
cd ~/zephyrproject
MODULE=hal_espressif
west blobs list "$MODULE"
west blobs fetch "$MODULE"
```

If `west blobs list "$MODULE"` prints no blob entries, skip the fetch for that board.

One-sentence summary: fetch chip-specific blobs only when the selected XIAO board's HAL module actually reports blob entries.

## 6. Build This Project's XIAO Boards

First, list the authoritative XIAO board names known to the Zephyr checkout:

```sh
west boards | grep -i xiao
```

Then build a small baseline firmware for representative boards. Most boards can
use `samples/basic/blinky`; boards with no on-board LED should use a sample that
does not require `led0`, such as `samples/hello_world`.

```sh
cd ~/zephyrproject/zephyr
west build -p always -b xiao_esp32c6/esp32c6/hpcore samples/basic/blinky
west build -p always -b xiao_rp2040 samples/basic/blinky
west build -p always -b xiao_ble samples/basic/blinky
west build -p always -b xiao_esp32c3 samples/hello_world
```

Some boards are multi-variant or multi-core. Using the bare name, such as `xiao_esp32c6`, will error and print the valid fully-qualified names, such as `xiao_esp32c6/esp32c6/hpcore`. Use the full name printed by Zephyr.

The table below records the baseline build matrix from 2026-06-20 against
Zephyr v4.4.0. PASS means that the selected baseline sample compiled in this
environment. UNSUPPORTED means the current stable checkout does not provide that
specific XIAO board target.

Authoritative board targets:

| Board display name | Zephyr build target | Baseline sample | v4.4.0 result | Notes |
| --- | --- | --- | --- | --- |
| XIAO SAMD21 | `seeeduino_xiao` | `samples/basic/blinky` | PASS | Build succeeded. |
| XIAO nRF52840 | `xiao_ble` | `samples/basic/blinky` | PASS | Build succeeded. |
| XIAO ESP32C3 | `xiao_esp32c3` | `samples/hello_world` | PASS | XIAO ESP32C3 has no on-board LED, so `blinky` is not a valid baseline for this board. |
| XIAO ESP32C5 | `xiao_esp32c5` | `samples/basic/blinky` | UNSUPPORTED | Zephyr v4.4.0 does not provide this XIAO target. Zephyr `main` has `esp32c5_devkitc`, but that is not the same board target as XIAO ESP32C5. |
| XIAO ESP32C6 | `xiao_esp32c6/esp32c6/hpcore` | `samples/basic/blinky` | PASS | Build succeeded. |
| XIAO ESP32S3 | `xiao_esp32s3/esp32s3/procpu` | `samples/basic/blinky` | PASS | Build succeeded. |
| XIAO MG24 | `xiao_mg24` | `samples/basic/blinky` | PASS | Build succeeded. |
| XIAO nRF54L15 | `xiao_nrf54l15/nrf54l15/cpuapp` | `samples/basic/blinky` | PASS | Build succeeded. |
| XIAO RA4M1 | `xiao_ra4m1` | `samples/basic/blinky` | PASS | Build succeeded. |
| XIAO RP2040 | `xiao_rp2040` | `samples/basic/blinky` | PASS | Build succeeded. |
| XIAO RP2350 | `xiao_rp2350/rp2350a/hazard3` | `samples/basic/blinky` | PASS | Build succeeded. |

One-sentence summary: validate each XIAO board by building a small upstream sample with the exact Zephyr target name.

## 7. Build This Project's Expansion Boards

Zephyr uses shields to describe add-on boards. Build shield samples by passing `--shield` with the upstream shield name:

```sh
west build -p always -b xiao_esp32c6/esp32c6/hpcore --shield seeed_xiao_expansion_board samples/drivers/display
west build -p always -b xiao_esp32s3/esp32s3/procpu --shield seeed_xiao_round_display samples/subsys/display/lvgl
```

The Grove Shield for XIAO, SKU 103020312, has no upstream Zephyr shield. It is a passive breakout, so Grove modules connect to the XIAO's own I2C pins and no `--shield` flag is used.

One-sentence summary: use Zephyr shield names only for expansion boards that have upstream shield definitions.

## 8. Flash And Monitor

After a successful build, flash the generated firmware:

```sh
west flash
```

ESP32 boards may need manual bootloader entry, such as double-tapping RESET. ESP32 boards can be monitored with `west espressif monitor`.

One-sentence summary: use `west flash` to program the board, and use the Espressif monitor command when validating ESP32 boards.

## 9. Verify And Report Evidence

The purpose of this validation pass is to collect real evidence for derived metadata fields such as build status and validated Zephyr version. These fields should be based on observed results, not assumptions.

Record the following results:

- which boards need a fully-qualified target
- which boards build successfully
- which boards fail, including the first and last useful lines of the error output
- whether the AS5600 Kconfig symbol is actually `CONFIG_AS5600`
- whether the two shield samples build successfully

Recommended evidence format:

```text
Zephyr checkout: main or pinned version
Host: macOS Apple Silicon
Board target: xiao_esp32c6
Sample: samples/basic/blinky or samples/hello_world
Result: passed, failed, or unsupported
Error head: first useful error lines
Error tail: last useful error lines
Notes: manual bootloader, fully-qualified target, or shield behavior
```

One-sentence summary: report the exact build evidence needed to populate metadata status fields honestly.
