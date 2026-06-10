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

## 5. Fetch ESP32 Binary Blobs

This step is required for the ESP32 XIAO boards. Six of this project's eleven boards are ESP32 boards in the C3, C5, C6, and S3 families, and they will not build without these binary blobs.

```sh
cd ~/zephyrproject/zephyr
west blobs fetch hal_espressif
```

One-sentence summary: fetch the required Espressif blobs before building ESP32-based XIAO targets.

## 6. Build This Project's XIAO Boards

First, list the authoritative XIAO board names known to the Zephyr checkout:

```sh
west boards | grep -i xiao
```

Then build a small `blinky` firmware for representative boards:

```sh
cd ~/zephyrproject/zephyr
west build -p always -b xiao_esp32c6 samples/basic/blinky
west build -p always -b xiao_rp2040 samples/basic/blinky
west build -p always -b xiao_ble/nrf52840 samples/basic/blinky
```

Some boards are multi-variant or multi-core. Using the bare name, such as `xiao_ble`, will error and print the valid fully-qualified names, such as `xiao_ble/nrf52840` and `xiao_ble/nrf52840/sense`. Use the full name printed by Zephyr.

Authoritative board targets:

| Board display name | Zephyr build target |
| --- | --- |
| XIAO SAMD21 | `seeeduino_xiao` |
| XIAO nRF52840 | `xiao_ble/nrf52840` |
| XIAO nRF52840 Sense | `xiao_ble/nrf52840/sense` |
| XIAO ESP32C3 | `xiao_esp32c3` |
| XIAO ESP32C5 | `xiao_esp32c5` |
| XIAO ESP32C6 | `xiao_esp32c6` |
| XIAO ESP32S3 | `xiao_esp32s3` |
| XIAO MG24 | `xiao_mg24` |
| XIAO nRF54L15 | `xiao_nrf54l15` |
| XIAO RA4M1 | `xiao_ra4m1` |
| XIAO RP2040 | `xiao_rp2040` |
| XIAO RP2350 | `xiao_rp2350` |

One-sentence summary: validate each XIAO board by building a small upstream sample with the exact Zephyr target name.

## 7. Build This Project's Expansion Boards

Zephyr uses shields to describe add-on boards. Build shield samples by passing `--shield` with the upstream shield name:

```sh
west build -p always -b xiao_esp32c6 --shield seeed_xiao_expansion_board samples/drivers/display
west build -p always -b xiao_esp32s3 --shield seeed_xiao_round_display samples/subsys/display/lvgl
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
Sample: samples/basic/blinky
Result: passed or failed
Error head: first useful error lines
Error tail: last useful error lines
Notes: manual bootloader, fully-qualified target, or shield behavior
```

One-sentence summary: report the exact build evidence needed to populate metadata status fields honestly.
