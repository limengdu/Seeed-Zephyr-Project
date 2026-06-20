# Getting Started: What This Project Is Doing

Short version: this repository is not the Zephyr source tree. It is a support layer that makes Zephyr practical for Seeed XIAO boards, Grove modules, and expansion boards.

Think of the work in two folders:

| Path | What it is | What it is used for |
| --- | --- | --- |
| `~/seeed-zephyr-base` | This project | XIAO/Grove metadata, scripts, docs, and validation results |
| `~/zephyrproject` | Upstream Zephyr workspace | Zephyr source, SDK, west workspace, and real firmware builds |

Zephyr is an embedded operating system. This project does not replace it. This project records which XIAO boards map to which Zephyr targets, which samples build, which modules need extra files, and which results have been verified.

One-sentence summary: `seeed-zephyr-base` is the product support and validation layer; `~/zephyrproject` is where Zephyr itself is fetched and built.

## 1. What Problem This Project Solves

Zephyr already supports many boards, but it expects users to understand:

- board target: Zephyr's name for a board, such as `xiao_esp32c6/esp32c6/hpcore`
- sample: a small Zephyr example, such as `samples/basic/blinky`
- SDK: compiler tools that turn source code into firmware
- west: Zephyr's command-line tool for fetching, building, flashing, and monitoring
- blob: vendor-provided binary files required by some chip families
- shield: Zephyr's term for an add-on board

This repository turns those details into metadata, scripts, and documents that can be validated repeatedly.

One-sentence summary: the project translates Zephyr's low-level board information into a XIAO-focused workflow.

## 2. Two Ways To Use This Repository

If you only want to run one board, your flow is:

1. Set up the Zephyr environment.
2. Find the correct board target.
3. Build one baseline sample.
4. Flash it to the board.

If you maintain this repository, your flow also includes:

1. Check the YAML metadata.
2. Build every board baseline sample.
3. Update validation evidence.
4. Keep docs aligned with real results.

One-sentence summary: users build one board; maintainers validate the whole metadata set.

## 3. First-Time Environment Setup

To prepare the common Zephyr environment, run this from the project root:

```sh
cd ~/seeed-zephyr-base
bash scripts/setup-macos.sh
```

If you already know the board you want, pass `--board`:

```sh
cd ~/seeed-zephyr-base
bash scripts/setup-macos.sh --board xiao_esp32c6
```

The setup script:

| Step | Action | Writes to |
| --- | --- | --- |
| 1 | Installs Homebrew build tools | Homebrew |
| 2 | Creates a Python venv and installs `west` | `~/zephyrproject/.venv` |
| 3 | Fetches Zephyr v4.4.0 | `~/zephyrproject/zephyr` |
| 4 | Installs Zephyr Python packages and the SDK | `~/zephyrproject` and `~/zephyr-sdk-*` |
| 5 | Fetches board-specific blobs when a board is selected | `~/zephyrproject` |

At the end, the script prints the next build command. For XIAO ESP32C3 it prints `samples/hello_world`, because that board has no on-board LED and `blinky` is not a valid baseline sample for it.

One-sentence summary: `setup-macos.sh` is the environment setup script; run it from `~/seeed-zephyr-base`, and it prepares `~/zephyrproject`.

## 4. Build One XIAO Board

Firmware builds run from the Zephyr source directory:

```sh
cd ~/zephyrproject/zephyr
source ~/zephyrproject/.venv/bin/activate
```

The general command is:

```sh
west build -p always -b <board_target> <sample_path>
```

Example for XIAO ESP32C6:

```sh
west build -p always -b xiao_esp32c6/esp32c6/hpcore samples/basic/blinky
```

Example for XIAO ESP32C3:

```sh
west build -p always -b xiao_esp32c3 samples/hello_world
```

XIAO ESP32C3 uses `hello_world` because `blinky` needs a `led0` device, and this board has no on-board LED.

One-sentence summary: build commands run in `~/zephyrproject/zephyr`; use the sample that matches the board hardware.

## 5. Verified Board Baselines

The table below comes from `tools/build_matrix/results.md`.

| Board | board target | baseline sample | v4.4.0 status | Notes |
| --- | --- | --- | --- | --- |
| XIAO SAMD21 | `seeeduino_xiao` | `samples/basic/blinky` | PASS | Builds |
| XIAO nRF52840 | `xiao_ble` | `samples/basic/blinky` | PASS | Builds |
| XIAO ESP32C3 | `xiao_esp32c3` | `samples/hello_world` | PASS | No on-board LED |
| XIAO ESP32C5 | `xiao_esp32c5` | `samples/basic/blinky` | UNSUPPORTED | Zephyr v4.4.0 has no XIAO target |
| XIAO ESP32C6 | `xiao_esp32c6/esp32c6/hpcore` | `samples/basic/blinky` | PASS | Builds |
| XIAO ESP32S3 | `xiao_esp32s3/esp32s3/procpu` | `samples/basic/blinky` | PASS | Builds |
| XIAO MG24 | `xiao_mg24` | `samples/basic/blinky` | PASS | Builds |
| XIAO nRF54L15 | `xiao_nrf54l15/nrf54l15/cpuapp` | `samples/basic/blinky` | PASS | Builds |
| XIAO RA4M1 | `xiao_ra4m1` | `samples/basic/blinky` | PASS | Builds |
| XIAO RP2040 | `xiao_rp2040` | `samples/basic/blinky` | PASS | Builds |
| XIAO RP2350 | `xiao_rp2350/rp2350a/hazard3` | `samples/basic/blinky` | PASS | Builds |

`UNSUPPORTED` does not mean a local script failed. It means the pinned Zephyr v4.4.0 checkout does not provide that XIAO board target. Zephyr `main` has `esp32c5_devkitc`, but that is not the same board target as XIAO ESP32C5.

One-sentence summary: 10 current targets build; XIAO ESP32C5 is not available in the pinned stable Zephyr baseline.

## 6. Flash The Board

After a successful build, flash from the same Zephyr directory:

```sh
west flash
```

ESP32 boards may require manual bootloader entry before flashing. ESP32 logs can be monitored with:

```sh
west espressif monitor
```

One-sentence summary: `west build` creates firmware, and `west flash` writes it to the board.

## 7. Script Map

| Script | Run from | Intended user | Purpose | Result |
| --- | --- | --- | --- | --- |
| `scripts/setup-macos.sh` | `~/seeed-zephyr-base` | First-time setup | Installs tools, fetches Zephyr, installs SDK, fetches blobs | Prints next command |
| `tools/validate_metadata/validate.py` | `~/seeed-zephyr-base` | Maintainer | Checks YAML metadata | Terminal PASS/FAIL |
| `tools/build_matrix/run.sh` | `~/seeed-zephyr-base` | Maintainer | Builds every board baseline | `tools/build_matrix/results.md` |

Common maintainer commands:

```sh
cd ~/seeed-zephyr-base
/Users/mengdu/zephyrproject/.venv/bin/python tools/validate_metadata/validate.py
```

```sh
cd ~/seeed-zephyr-base
BUILD_MATRIX_GENERATED_ON=2026-06-20 bash tools/build_matrix/run.sh
```

One-sentence summary: normal users mainly need setup; maintainers run metadata validation and the build matrix.

## 8. Important Files

| Path | Purpose |
| --- | --- |
| `metadata/boards/*.yaml` | XIAO board data |
| `metadata/grove_modules/*.yaml` | Grove module data |
| `metadata/expansion_boards/*.yaml` | Expansion-board data |
| `tools/build_matrix/board-overrides.tsv` | Special baseline rules, such as C3 using `hello_world` |
| `tools/build_matrix/results.md` | Latest build matrix |
| `AI use/en/validation-log.md` | Detailed validation evidence |
| `docs/zh/getting-started.md` | Chinese getting-started guide |
| `docs/en/getting-started.md` | English getting-started guide |

One-sentence summary: `metadata` stores facts, `tools` validates facts, and `docs` explains how to use them.

## 9. Common Errors

### `west: command not found`

Activate the venv:

```sh
source ~/zephyrproject/.venv/bin/activate
```

One-sentence summary: if the shell cannot find `west`, activate the Zephyr venv.

### `no west workspace found`

You are likely in the wrong directory or the workspace has not been initialized. Check:

```sh
ls ~/zephyrproject/.west
```

One-sentence summary: Zephyr commands need a west workspace.

### `No board named ...`

Check the target spelling and the current Zephyr version:

```sh
cd ~/zephyrproject/zephyr
west boards | grep -i xiao
```

One-sentence summary: missing boards are usually typos or targets not available in the current Zephyr release.

### `blinky` cannot find `led0`

Use a non-LED sample for boards without an on-board LED:

```sh
west build -p always -b xiao_esp32c3 samples/hello_world
```

One-sentence summary: not every board is a valid `blinky` board.

### ESP32 build needs blobs

Run setup with the selected board:

```sh
cd ~/seeed-zephyr-base
bash scripts/setup-macos.sh --board xiao_esp32c6
```

One-sentence summary: ESP32 families may need vendor binary files before builds succeed.

## 10. Recommended Next Step

To run one board end to end, start with XIAO ESP32C6:

```sh
cd ~/seeed-zephyr-base
bash scripts/setup-macos.sh --board xiao_esp32c6
cd ~/zephyrproject/zephyr
source ~/zephyrproject/.venv/bin/activate
west build -p always -b xiao_esp32c6/esp32c6/hpcore samples/basic/blinky
west flash
```

To maintain this repository, run these after metadata changes:

```sh
cd ~/seeed-zephyr-base
/Users/mengdu/zephyrproject/.venv/bin/python tools/validate_metadata/validate.py
BUILD_MATRIX_GENERATED_ON=2026-06-20 bash tools/build_matrix/run.sh
```

One-sentence summary: build one known-good board first, then use the matrix to validate the whole metadata set.
