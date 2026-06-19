# Validation Log

This log records build and hardware validation evidence for the XIAO boards,
Grove modules, and expansion boards described under `metadata/`. It follows the
evidence format defined in `docs/getting-started.md` section 9.

Derived metadata fields under `metadata/status/` must be populated only from
evidence recorded here, never hand-authored. See `docs/01-phase-one-zephyr-base.md`,
section "Keeping Metadata Honest: Status Is Derived, Not Declared".

## Host Environment

| Field | Value |
| --- | --- |
| OS | macOS 26.3.1 (Darwin 25.3.0) |
| Architecture | Apple Silicon (arm64) |
| Homebrew | installed at `/opt/homebrew` |
| Python | 3.14.5 |
| git | 2.50.1 |
| Free disk | ~602 GiB |
| Baseline Zephyr | v4.4.0 (pinned, latest stable) |
| Log started | 2026-06-19 |

## Metadata Validation

Tool: `tools/validate_metadata/validate.py` (requires `pyyaml`).

| Date | Result | Notes |
| --- | --- | --- |
| 2026-06-19 | 18 passed, 0 failed, 18 total | 11 boards, 4 Grove modules, 3 expansion boards |

## Toolchain Setup

| # | Step | Command | Status |
| --- | --- | --- | --- |
| 1 | Install build tools | `brew install cmake ninja gperf python3 python-tk ccache qemu dtc libmagic wget openocd` | in progress |
| 2 | venv + west | `python3 -m venv ~/zephyrproject/.venv && pip install west` | pending |
| 3 | Fetch source | `west init ~/zephyrproject --mr v4.4.0 && west update` | pending |
| 4 | CMake export + SDK | `west zephyr-export && west packages pip --install && west sdk install` | pending |
| 5 | ESP32 blobs | `west blobs fetch hal_espressif` | pending |
| 6 | Build sample | `west build -p always -b xiao_esp32c6 samples/basic/blinky` | pending |
| 7 | Record evidence | populate the board evidence table below | pending |

## Board Build Evidence

Baseline sample for the first pass: `samples/basic/blinky`. First validation
target: `xiao_esp32c6`.

| Board metadata id | Zephyr target | ESP32 blob | Build result | Validated version | Notes |
| --- | --- | --- | --- | --- | --- |
| xiao_samd21 | `seeeduino_xiao` | no | pending | | |
| xiao_nrf52840 | `xiao_ble/nrf52840` | no | pending | | also `/sense` variant |
| xiao_esp32c3 | `xiao_esp32c3` | yes | pending | | |
| xiao_esp32c5 | `xiao_esp32c5` | yes | pending | | |
| xiao_esp32c6 | `xiao_esp32c6` | yes | pending | | first target |
| xiao_esp32s3 | `xiao_esp32s3` | yes | pending | | |
| xiao_mg24 | `xiao_mg24` | no | pending | | |
| xiao_nrf54l15 | `xiao_nrf54l15` | no | pending | | |
| xiao_ra4m1 | `xiao_ra4m1` | no | pending | | |
| xiao_rp2040 | `xiao_rp2040` | no | pending | | |
| xiao_rp2350 | `xiao_rp2350` | no | pending | | |

Per-board evidence detail (filled as each build completes):

```text
Zephyr checkout: v4.4.0
Host: macOS 26.3.1 Apple Silicon (arm64)
Board target: xiao_esp32c6
Sample: samples/basic/blinky
Result: pending
Error head:
Error tail:
Notes:
```

## Open Issues and Notes

- Python 3.14.5 is newer than the versions commonly validated with west. If
  `west packages pip --install` (step 4) fails to build a dependency, fall back
  to a Homebrew-provided Python 3.13 virtual environment and rebuild the venv.
- `docs/getting-started.md` section 5 states six of eleven boards are ESP32
  (C3/C5/C6/S3 families), but `metadata/boards/` currently holds four ESP32
  entries (c3, c5, c6, s3). Reconcile the count when populating evidence.
- Boards with multiple variants (for example `xiao_ble`) require the
  fully-qualified target name; record the exact name that builds.
