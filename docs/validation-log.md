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
| Python | 3.14.6 (Homebrew `python@3.14`) |
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
| 1 | Install build tools | `brew install cmake ninja gperf python3 python-tk ccache qemu dtc libmagic wget openocd` | done (2026-06-19) |
| 2 | venv + west | `python3 -m venv ~/zephyrproject/.venv && pip install west` | done (2026-06-19, west v1.5.0) |
| 3 | Fetch source | `west init ~/zephyrproject --mr v4.4.0 && west update` | done (2026-06-19, v4.4.0, ~5.4 GB) |
| 4 | CMake export + SDK | `west zephyr-export && west packages pip --install && west sdk install` | done (2026-06-19, SDK 1.0.1) |
| 5 | ESP32 blobs | `west blobs fetch hal_espressif` | done (2026-06-19, ~31 MB) |
| 6 | Build sample | `west build -p always -b xiao_esp32c6 samples/basic/blinky` | pending |
| 7 | Record evidence | populate the board evidence table below | pending |

Step 1 verified 2026-06-19: cmake 4.3.3, ninja 1.13.2, dtc 1.8.1, gperf 3.3,
ccache 4.13.6, openocd 0.12.0, qemu (all targets incl. xtensa and riscv32).
Step 2 verified 2026-06-19: west v1.5.0 installed cleanly in a Python 3.14.6
venv, confirming west itself runs on 3.14.
Step 3 verified 2026-06-19: workspace initialized at ~/zephyrproject, zephyr
checked out at v4.4.0, west update fetched all modules; total ~5.4 GB on disk.
A trimmed west.yml that fetches only XIAO-relevant modules is a future
size/time optimization for the outward-facing path.
Step 4 verified 2026-06-19: Zephyr SDK 1.0.1 installed (host tools + all GNU
toolchains, including riscv64-zephyr-elf and arm-zephyr-eabi); SDK toolchains
live under `sdk_gnu_toolchains/`, not the SDK root. `west packages pip --install`
succeeded on Python 3.14.6 (pyelftools, pykwalify, anytree, intelhex, etc.);
`west zephyr-export` registered the Zephyr and ZephyrUnittest CMake packages.
Step 5 verified 2026-06-19: `west blobs fetch hal_espressif` fetched all
Espressif blobs (~31 MB total); esp32c6 has its 8 `.a` blobs present.

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

- Python 3.14.6 (Homebrew `python@3.14`) is the host interpreter; Homebrew
  provides no 3.13 build. Zephyr's documented minimum is Python 3.12 with no
  upper bound, and community reports confirm 3.13/3.14 work (a 3.14 upgrade may
  require rebuilding the venv). Decision: proceed on 3.14.6. If a dependency
  fails to install on 3.14 at step 4, install `python@3.13` via Homebrew and
  rebuild the venv. Checked against Zephyr getting-started guidance 2026-06-19.
RESOLVED 2026-06-19: step 4 `west packages pip --install` succeeded on Python
3.14.6 with no fallback needed; 3.14 is confirmed usable for this project's setup.
- `docs/getting-started.md` section 5 states six of eleven boards are ESP32
  (C3/C5/C6/S3 families), but `metadata/boards/` currently holds four ESP32
  entries (c3, c5, c6, s3). Reconcile the count when populating evidence.
- Boards with multiple variants (for example `xiao_ble`) require the
  fully-qualified target name; record the exact name that builds.
- Step 3 first attempt failed with two errors sharing one root cause:
  `command not found: west` (the shell had not activated the venv) and
  `no west workspace found from ".../seeed-zephyr-base"` (`west init` had not
  completed, and the shell was outside the workspace). Confirmed
  `~/zephyrproject` held only `.venv` (no `.west`, no zephyr tree). Fix:
  activate the venv, run `west init ~/zephyrproject --mr v4.4.0` to completion,
  then `cd ~/zephyrproject && west update`. Note the two distinct directories:
  the product repo `~/seeed-zephyr-base` versus the Zephyr workspace
  `~/zephyrproject`. The one-command setup script must auto-activate the venv
  and confirm the workspace is initialized before calling `west update`; this
  is a high-frequency external-user trap.
