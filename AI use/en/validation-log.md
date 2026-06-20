# Validation Log

This log records build and hardware validation evidence for the XIAO boards,
Grove modules, expansion boards, and repository examples described under
`metadata/` and `examples/`.

Derived metadata fields under `metadata/status/` must be populated only from
evidence recorded here, never hand-authored. See `AI use/en/01-phase-one-zephyr-base.md`,
section "Validation Strategy".

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
| 2026-06-20 | 18 passed, 0 failed, 18 total | Re-run through `~/zephyrproject/.venv/bin/python`; host `python3` lacks `pyyaml` |
| 2026-06-20 | 29 passed, 0 failed, 29 total | 18 metadata files plus 11 repository example descriptors |

## Toolchain Setup

| # | Step | Command | Status |
| --- | --- | --- | --- |
| 1 | Install build tools | `brew install cmake ninja gperf python3 python-tk ccache qemu dtc libmagic wget openocd` | done (2026-06-19) |
| 2 | venv + west | `python3 -m venv ~/zephyrproject/.venv && pip install west` | done (2026-06-19, west v1.5.0) |
| 3 | Fetch source | `west init ~/zephyrproject --mr v4.4.0 && west update` | done (2026-06-19, v4.4.0, ~5.4 GB) |
| 4 | CMake export + SDK | `west zephyr-export && west packages pip --install && west sdk install` | done (2026-06-19, SDK 1.0.1) |
| 5 | ESP32 blobs | `west blobs fetch hal_espressif` | done (2026-06-19, ~31 MB) |
| 6 | Build sample | `west build -p always -b xiao_esp32c6/esp32c6/hpcore samples/basic/blinky` | done (2026-06-19) |
| 7 | Record first board evidence | populate the board evidence table below | done (2026-06-19) |
| 8 | Flash sample on hardware | `west flash` | done (2026-06-19, xiao_esp32c6 LED blink verified) |
| 9 | Batch board build matrix | `bash tools/build_matrix/run.sh` | done (2026-06-19, 9 passed, 2 failed) |
| 10 | Board-specific baseline matrix | `BUILD_MATRIX_GENERATED_ON=2026-06-20 bash tools/build_matrix/run.sh` | done (2026-06-20, 10 passed, 0 failed, 1 unsupported) |
| 11 | Repository example build matrix | `BUILD_MATRIX_GENERATED_ON=2026-06-20 bash tools/build_matrix/run.sh` | done (2026-06-20, 10 passed, 0 failed, 1 unsupported) |
| 12 | Single repository example build | `bash scripts/build-example.sh examples/boards/xiao_esp32c3/hello_world` | done (2026-06-20) |
| 13 | CLI repository example build matrix | `scripts/seeed-zephyr matrix` | done (2026-06-20, 10 passed, 0 failed, 1 unsupported) |
| 14 | Installed CLI smoke test | `seeed-zephyr build xiao_esp32c3` from `/tmp` through a temporary PATH install | done (2026-06-20) |
| 15 | CLI flash monitor option check | `scripts/seeed-zephyr flash --help` plus validation error checks | done (2026-06-20, CLI behavior only) |
| 16 | Installed CLI flash and monitor on hardware | `seeed-zephyr flash xiao_esp32c6 --monitor` | done (2026-06-20, build passed, flash passed, monitor opened) |

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
Step 6 verified 2026-06-19: `samples/basic/blinky` built for
`xiao_esp32c6/esp32c6/hpcore` with Zephyr SDK 1.0.1 (riscv64-zephyr-elf 14.3.0).
The bare target `xiao_esp32c6` fails: ESP32-C6 is multi-core and needs the
`/esp32c6/hpcore` qualifier. Output: zephyr.elf 1.8 MB, zephyr.bin 141 KB;
FLASH 133020 B (3.17%), SRAM 50688 B (9.95%).
Step 8 verified 2026-06-19: `west flash` programmed the physical
xiao_esp32c6/esp32c6/hpcore board; on-board LED blink confirmed by direct
observation. First hardware-in-loop evidence for this project.
Step 9 verified 2026-06-19: `tools/build_matrix/run.sh` built
`samples/basic/blinky` for all 11 board metadata entries. The corrected run
finished with 9 passed and 2 failed. The two failures are `xiao_esp32c3`
(`led0` GPIO device resolution failure in the blinky sample) and `xiao_esp32c5`
(target not present in Zephyr v4.4.0).
Step 10 verified 2026-06-20: the build matrix now supports board-specific
baseline samples and an explicit `UNSUPPORTED` result. XIAO ESP32C3 uses
`samples/hello_world` because the board has no on-board LED, so `blinky` is not
a valid baseline. The run finished with 10 passed, 0 failed, and 1 unsupported.
`xiao_esp32c5` remains unsupported in the pinned Zephyr v4.4.0 checkout because
that specific XIAO target is absent. Upstream Zephyr `main` has
`boards/espressif/esp32c5_devkitc`, but that is an ESP32-C5 DevKitC target, not
evidence that XIAO ESP32C5 has a validated board target.
Step 11 verified 2026-06-20: `tools/build_matrix/run.sh` now builds
repository-owned examples under `examples/boards/` instead of upstream Zephyr
sample paths. The run finished with 10 passed, 0 failed, and 1 unsupported.
`xiao_esp32c5` remains unsupported because Zephyr v4.4.0 does not provide a
`xiao_esp32c5` target.
Step 12 verified 2026-06-20: the user-facing single-example command built
`examples/boards/xiao_esp32c3/hello_world` successfully through
`scripts/build-example.sh`.
Step 13 verified 2026-06-20: the repository CLI ran the same repository example
build matrix through `scripts/seeed-zephyr matrix`. The run finished with 10
passed, 0 failed, and 1 unsupported. The unsupported entry is `xiao_esp32c5`
because the selected Zephyr baseline does not provide a `xiao_esp32c5` target.
Step 14 verified 2026-06-20: the setup install function created a temporary
`seeed-zephyr` command under `/tmp/seeed-zephyr-cli-test-bin`. From `/tmp`, the
installed command rendered help, listed boards, listed examples, reported
`xiao_esp32c5` as unsupported, and built `xiao_esp32c3` successfully.
Step 15 verified 2026-06-20: the CLI exposes `--monitor` on `flash`. The
unsupported-board path and non-Espressif monitor path were validated without
flashing hardware.
Step 16 verified 2026-06-20: the installed CLI command
`seeed-zephyr flash xiao_esp32c6 --monitor` completed build and flash on the
physical XIAO ESP32C6. `esptool` ran from the Zephyr venv, detected the board
on `/dev/cu.usbmodem101`, wrote 144300 bytes, verified the hash, reset the
board, opened `idf_monitor`, and showed Zephyr boot plus `LED state` toggles.

## CLI Validation Evidence

Baseline CLI: `scripts/seeed-zephyr`, 2026-06-20.

| Command | Result | Notes |
| --- | --- | --- |
| `python3 -m py_compile tools/cli/seeed_zephyr.py` | passed | CLI Python syntax check |
| `bash -n scripts/seeed-zephyr` | passed | wrapper shell syntax check |
| `scripts/seeed-zephyr --help` | passed | top-level command help renders |
| `scripts/seeed-zephyr list boards` | passed | lists all 11 board metadata entries |
| `scripts/seeed-zephyr list examples` | passed | lists selected repository examples |
| `scripts/seeed-zephyr build xiao_esp32c5` | expected error | reports unsupported board in the selected Zephyr baseline |
| `scripts/seeed-zephyr build xiao_esp32c3` | passed | builds the ESP32C3 `hello_world` repository demo |
| `scripts/seeed-zephyr matrix` | passed | total=11, pass=10, fail=0, unsupported=1 |
| temporary `seeed-zephyr --help` from `/tmp` | passed | installed symlink resolves the repository root |
| temporary `seeed-zephyr list boards` from `/tmp` | passed | command works outside the repository |
| temporary `seeed-zephyr list examples` from `/tmp` | passed | command works outside the repository |
| temporary `seeed-zephyr build xiao_esp32c5` from `/tmp` | expected error | reports unsupported board |
| temporary `seeed-zephyr build xiao_esp32c3` from `/tmp` | passed | installed command builds a real repository demo outside the repository |
| non-interactive `install_cli_if_requested` | passed | defaults to installing the CLI |
| `scripts/seeed-zephyr flash --help` | passed | help includes `--monitor` |
| `scripts/seeed-zephyr flash xiao_esp32c5 --monitor` | expected error | unsupported board is rejected |
| `scripts/seeed-zephyr flash xiao_nrf52840 --monitor` | expected error | non-Espressif monitor request is rejected before build or flash |
| `/Users/mengdu/zephyrproject/.venv/bin/esptool version` | passed | esptool 5.3.0 is installed in the Zephyr venv |
| `source scripts/setup-macos.sh; check_espressif_zephyr_tools` | passed | setup confirms Zephyr's `hal_espressif` monitor and venv esptool availability |
| `source scripts/setup-macos.sh; BOARD_VENDOR=espressif; check_board_host_tools` | passed | board-specific setup checks Zephyr's Espressif tools |
| `source scripts/setup-macos.sh; BOARD_VENDOR=nordic; check_board_host_tools` | passed | non-Espressif board-specific setup does not check Espressif tools |
| `seeed-zephyr flash xiao_esp32c6 --monitor` in a TTY session | passed | build, flash, hash verification, monitor startup, and serial LED state output observed |
| direct `west build` delegation through `scripts/seeed-zephyr build xiao_esp32c3` | passed | CLI selected the repository example and called `west build`; output order was verified |
| direct `west flash` and monitor delegation through `seeed-zephyr flash xiao_esp32c6 --monitor` | passed | CLI called `west build`, `west flash`, and Zephyr's Espressif monitor; flash wrote 144300 bytes and serial output showed Zephyr boot plus `LED state` toggles |

## Repository Example Build Evidence

Baseline matrix: 2026-06-20, Zephyr v4.4.0, macOS Apple Silicon.
Default repository example: `examples/boards/<board_id>/blinky`; board-specific
overrides are recorded in `tools/build_matrix/board-overrides.tsv`.

| Board metadata id | Zephyr target | Repository example | ESP32 blob | Build result | Validated version | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| xiao_samd21 | `seeeduino_xiao` | `examples/boards/xiao_samd21/blinky` | no | passed | v4.4.0 | build succeeded |
| xiao_nrf52840 | `xiao_ble` | `examples/boards/xiao_nrf52840/blinky` | no | passed | v4.4.0 | build succeeded |
| xiao_esp32c3 | `xiao_esp32c3` | `examples/boards/xiao_esp32c3/hello_world` | yes | passed | v4.4.0 | no on-board LED; uses console heartbeat |
| xiao_esp32c5 | `xiao_esp32c5` | `examples/boards/xiao_esp32c5/hello_world` | yes | unsupported | n/a | Zephyr v4.4.0 has no `xiao_esp32c5` target |
| xiao_esp32c6 | `xiao_esp32c6/esp32c6/hpcore` | `examples/boards/xiao_esp32c6/blinky` | yes | passed | v4.4.0 | build succeeded |
| xiao_esp32s3 | `xiao_esp32s3/esp32s3/procpu` | `examples/boards/xiao_esp32s3/blinky` | yes | passed | v4.4.0 | build succeeded |
| xiao_mg24 | `xiao_mg24` | `examples/boards/xiao_mg24/blinky` | no | passed | v4.4.0 | build succeeded |
| xiao_nrf54l15 | `xiao_nrf54l15/nrf54l15/cpuapp` | `examples/boards/xiao_nrf54l15/blinky` | no | passed | v4.4.0 | build succeeded |
| xiao_ra4m1 | `xiao_ra4m1` | `examples/boards/xiao_ra4m1/blinky` | no | passed | v4.4.0 | build succeeded |
| xiao_rp2040 | `xiao_rp2040` | `examples/boards/xiao_rp2040/blinky` | no | passed | v4.4.0 | build succeeded |
| xiao_rp2350 | `xiao_rp2350/rp2350a/hazard3` | `examples/boards/xiao_rp2350/blinky` | no | passed | v4.4.0 | build succeeded |

## Historical Upstream Sample Build Evidence

This section records the earlier upstream Zephyr sample baseline before
repository-owned examples existed.

Baseline matrix: 2026-06-20, Zephyr v4.4.0, macOS Apple Silicon.
Default sample: `samples/basic/blinky`; board-specific overrides are recorded in
`tools/build_matrix/board-overrides.tsv`.

| Board metadata id | Zephyr target | Baseline sample | ESP32 blob | Build result | Validated version | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| xiao_samd21 | `seeeduino_xiao` | `samples/basic/blinky` | no | passed | v4.4.0 | build succeeded |
| xiao_nrf52840 | `xiao_ble` | `samples/basic/blinky` | no | passed | v4.4.0 | build succeeded |
| xiao_esp32c3 | `xiao_esp32c3` | `samples/hello_world` | yes | passed | v4.4.0 | XIAO ESP32C3 has no on-board LED, so `blinky` is not a valid baseline |
| xiao_esp32c5 | `xiao_esp32c5` | `samples/basic/blinky` | yes | unsupported | n/a | Zephyr v4.4.0 reports no board named `xiao_esp32c5`; upstream `esp32c5_devkitc` is not the same board target |
| xiao_esp32c6 | `xiao_esp32c6/esp32c6/hpcore` | `samples/basic/blinky` | yes | passed | v4.4.0 | FLASH 3.17%, SRAM 9.95%; HW: LED blink verified |
| xiao_esp32s3 | `xiao_esp32s3/esp32s3/procpu` | `samples/basic/blinky` | yes | passed | v4.4.0 | build succeeded |
| xiao_mg24 | `xiao_mg24` | `samples/basic/blinky` | no | passed | v4.4.0 | build succeeded |
| xiao_nrf54l15 | `xiao_nrf54l15/nrf54l15/cpuapp` | `samples/basic/blinky` | no | passed | v4.4.0 | build succeeded |
| xiao_ra4m1 | `xiao_ra4m1` | `samples/basic/blinky` | no | passed | v4.4.0 | build succeeded |
| xiao_rp2040 | `xiao_rp2040` | `samples/basic/blinky` | no | passed | v4.4.0 | build succeeded |
| xiao_rp2350 | `xiao_rp2350/rp2350a/hazard3` | `samples/basic/blinky` | no | passed | v4.4.0 | build succeeded |

Per-board evidence detail (filled as each build completes):

```text
Zephyr checkout: v4.4.0
Host: macOS 26.3.1 Apple Silicon (arm64)
Board target: xiao_esp32c6
Sample: samples/basic/blinky or samples/hello_world
Result: see table above
Error head: see tools/build_matrix/results.md and the follow-up notes below
Error tail: see tools/build_matrix/results.md and the follow-up notes below
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
- `xiao_esp32c3`: `samples/basic/blinky` is not a valid baseline because XIAO
  ESP32C3 has no on-board LED. Use `samples/hello_world` for build-only
  baseline validation.
RESOLVED 2026-06-20: `xiao_esp32c3` passed with `samples/hello_world`.
- `xiao_esp32c5`: Zephyr v4.4.0 reports no board named `xiao_esp32c5`.
  Zephyr `main` has `esp32c5_devkitc`, but that target is not XIAO ESP32C5.
  Keep this entry `unsupported` until a XIAO-specific target exists or a
  project-local board definition is intentionally added and validated.
- Boards with multiple CPU targets require the fully-qualified target name;
  `xiao_esp32c6`, `xiao_esp32s3`, `xiao_nrf54l15`, and `xiao_rp2350` have been
  reconciled in `metadata/boards/` and `docs/en/getting-started.md`.
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
RESOLVED 2026-06-20: Board target reconciliation was completed from the
2026-06-19 build matrix. The authoritative docs and board metadata now use the
validated fully-qualified targets where Zephyr requires them.
