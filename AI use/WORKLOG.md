# AI Work Log / AI 工作记录

## Purpose / 用途

English: This file records meaningful AI work on this repository. It is not a
chat transcript. It is a factual handoff log so a future AI agent can understand
what changed, why it changed, how it was verified, and what remains.

中文: 本文件记录 AI 在本仓库中完成的重要工作。它不是聊天记录，而是事实性交接日志，
帮助未来 AI 明确改了什么、为什么改、如何验证、还剩什么。

## Required Entry Format / 必填记录格式

```text
## YYYY-MM-DD - short title

Scope:
- Files or directories changed.

Reason:
- Product or technical reason for the change.

Result:
- What changed in user-visible or maintainer-visible behavior.

Verification:
- Commands run and results.

Remaining:
- Follow-up work, known limits, or open questions.
```

## 2026-06-20 - Verify RP2040 UF2 flash and monitor flow

Scope:
- Updated `tools/cli/seeed_zephyr.py` so Raspberry Pi vendor UF2 flash failures
  include a BOOTSEL and UF2 mass-storage hint.
- Added `tools/cli/test_seeed_zephyr.py` regression coverage for the
  Raspberry Pi UF2 flash hint on `xiao_rp2040` and `xiao_rp2350`.
- Added USB CDC ACM console configuration to
  `examples/boards/xiao_rp2040/blinky`.
- Marked `examples/boards/xiao_rp2040/blinky/example.yaml` as
  `hardware-tested`.
- Added `docs/en/boards/xiao-rp2040.md` and
  `docs/zh/boards/xiao-rp2040.md`, then linked them from the board-note indexes
  and Getting Started docs.
- Added XIAO RP2040 hardware evidence to
  `AI use/HARDWARE_VERIFICATION.md`.

Reason:
- `seeed-zephyr flash xiao_rp2040 --monitor` built the firmware but Zephyr's
  UF2 runner failed with `No matching UF2 partitions found` when the board was
  not in UF2 bootloader mode.
- The repository example also needed a USB CDC ACM console so `--monitor` could
  show user-visible output after a successful UF2 flash.

Result:
- RP2040 UF2 flash failures now include a direct BOOTSEL/UF2 hint.
- The XIAO RP2040 blinky example now exposes monitor output through USB CDC ACM.
- `seeed-zephyr flash xiao_rp2040 --monitor` can build, copy `zephyr.uf2` to
  the mounted UF2 volume, and open pyserial miniterm.
- User-facing docs now state that RP2040 repeated flashing requires entering
  UF2 mode again before each flash.

Verification:
- `python3 tools/cli/test_seeed_zephyr.py`: passed.
- `PYTHONPYCACHEPREFIX=/private/tmp/seeed-zephyr-pycache python3 -m py_compile tools/cli/seeed_zephyr.py tools/cli/test_seeed_zephyr.py`:
  passed.
- `scripts/seeed-zephyr build xiao_rp2040`: passed.
- Generated `.config` contains `CONFIG_USB_DEVICE_STACK_NEXT=y`,
  `CONFIG_USBD_CDC_ACM_CLASS=y`,
  `CONFIG_CDC_ACM_SERIAL_INITIALIZE_AT_BOOT=y`,
  `CONFIG_CDC_ACM_SERIAL_PRODUCT_STRING="Seeed XIAO RP2040 blinky"`,
  `CONFIG_UART_CONSOLE=y`, and `CONFIG_STDOUT_CONSOLE=y`.
- Generated `zephyr.dts` contains `zephyr,console = &cdc_acm_uart0` and a
  `zephyr,cdc-acm-uart` compatible node.
- `seeed-zephyr flash xiao_rp2040 --monitor` without UF2 mode: build passed,
  `west flash` failed with `No matching UF2 partitions found`, and the CLI
  showed the BOOTSEL/UF2 hint.
- `seeed-zephyr flash xiao_rp2040 --monitor` with UF2 mode: build passed,
  Zephyr copied `zephyr.uf2` to `/Volumes/RPI-RP2`, pyserial miniterm opened
  `/dev/cu.usbmodem1101`, and repeated LED state output was observed.
- A second consecutive `seeed-zephyr flash xiao_rp2040 --monitor` without
  entering UF2 mode again failed with the expected UF2 error and CLI hint.

Remaining:
- None for RP2040 UF2 flash and monitor support. Requiring UF2 mode before each
  flash is the currently verified board behavior.

## 2026-06-20 - Document SAMD21 BOSSA auto-reset behavior

Scope:
- Added `docs/en/boards/README.md` and `docs/zh/boards/README.md` as the
  board-specific documentation indexes.
- Added `docs/en/boards/xiao-samd21.md` and
  `docs/zh/boards/xiao-samd21.md`.
- Linked the new board notes from the root README, `docs/README.md`, language
  README files, and Getting Started guides.

Reason:
- The XIAO SAMD21 verified example has meaningful board-specific flashing
  behavior. Users need to know when repeated flashing should not require manual
  bootloader entry, and when manual bootloader entry is still a valid recovery
  path.

Result:
- User-facing docs now explain the XIAO SAMD21 BOSSA-compatible bootloader,
  1200-baud reset flow, USB CDC ACM requirement, expected repeated flashing
  behavior, USB replug behavior, and recovery cases.
- The docs point to the existing hardware verification evidence.

Verification:
- Documentation links were checked for local file existence.
- `git diff --check`: passed.

Remaining:
- Add similar board-specific pages when other XIAO boards gain hardware-tested
  flashing or monitor behavior.

## 2026-06-20 - Fix SAMD21 repeated flash reset

Scope:
- Updated `examples/boards/xiao_samd21/blinky/app.overlay` to give the USB CDC
  ACM console node the `CDC_ACM_0` label used by Zephyr's SAMD21 BOSSA reset
  hook.
- Updated `examples/boards/xiao_samd21/blinky/prj.conf` to use Zephyr's legacy
  USB device stack for this example, enabling the CDC ACM DTE rate callback
  that Zephyr's SAMD21 BOSSA reset path depends on.
- Updated `examples/boards/xiao_samd21/blinky/src/main.c` to enable the USB
  device stack before printing the startup banner.
- Marked `examples/boards/xiao_samd21/blinky/example.yaml` as
  `hardware-tested`.
- Added XIAO SAMD21 hardware evidence to `AI use/HARDWARE_VERIFICATION.md`.
- Updated user-facing command examples and matrix notes to show the verified
  no-port default command.

Reason:
- `seeed-zephyr flash xiao_samd21 --monitor` worked once when the board was
  already in the bootloader, but a second run against the running application
  failed with `Device unsupported`. The running firmware exposed a monitor
  serial port but did not provide the Zephyr CDC ACM callback path that performs
  the 1200-baud BOSSA reset.

Result:
- The XIAO SAMD21 blinky example now exposes USB CDC serial output and supports
  Zephyr's BOSSA auto-reset path.
- `seeed-zephyr flash xiao_samd21 --monitor` can build, flash, verify, and open
  the monitor.
- A second consecutive flash and monitor run succeeds without manually entering
  bootloader mode.

Verification:
- `scripts/seeed-zephyr build xiao_samd21`: passed.
- Generated `.config` contains `CONFIG_USB_DEVICE_STACK=y`,
  `CONFIG_USB_CDC_ACM=y`, `CONFIG_CDC_ACM_DTE_RATE_CALLBACK_SUPPORT=y`,
  `CONFIG_BOOTLOADER_BOSSA_DEVICE_NAME="CDC_ACM_0"`, and no
  `CONFIG_USB_DEVICE_STACK_NEXT`.
- Generated `zephyr.dts` contains `label = "CDC_ACM_0"` under
  `cdc_acm_uart0`.
- First `seeed-zephyr flash xiao_samd21 --monitor`: build passed, BOSSA flash
  write and verify passed, pyserial miniterm opened `/dev/cu.usbmodem1101`, and
  Zephyr boot plus LED state toggles were observed.
- Second consecutive `seeed-zephyr flash xiao_samd21 --monitor` without manual
  reset: build passed, BOSSA flash write and verify passed, pyserial miniterm
  opened `/dev/cu.usbmodem1101`, and Zephyr boot plus LED state toggles were
  observed.

Remaining:
- None for the repeated XIAO SAMD21 flash and monitor issue.

## 2026-06-20 - Add BOSSA bossac checks for SAMD21 flashing

Scope:
- Added board-specific BOSSA installation to macOS setup: `bossa` is installed
  when `--board xiao_samd21` is selected, or when no board is selected for a
  full host dependency install.
- Added board-specific BOSSA installation to Linux setup: Debian/Ubuntu uses
  `bossa-cli`, Fedora uses `bossa`, and the packages are installed only for
  `xiao_samd21` or no-board full setup.
- Added shared setup checks for the `bossac` command when the selected board
  target is `seeeduino_xiao`.
- Added CLI preflight checking for `bossac` before `west flash` on
  `xiao_samd21`.
- Added `--delay 3` to the SAMD21 `west flash` call so Zephyr's bossac runner
  waits for bootloader re-enumeration.
- Updated the `xiao_samd21` blinky example to expose printk output through USB
  CDC ACM, so the repository demo can be monitored over the board USB port
  after the new firmware is flashed.
- Added CLI waiting for USB serial re-enumeration before opening the
  non-Espressif monitor path.
- Updated the Windows setup preparer to state that Linux flash tools are
  installed and checked inside WSL2 by `scripts/setup-linux.sh`.

Reason:
- `seeed-zephyr flash xiao_samd21 --monitor` reached Zephyr's `bossac` runner
  after a successful build, then failed because `bossac` was not installed or
  available in `PATH`.

Result:
- macOS setup installs the Homebrew `bossa` package only for SAMD21-specific or
  no-board full dependency setup.
- Linux setup installs the distro BOSSA package only for SAMD21-specific or
  no-board full dependency setup.
- `scripts/setup-*.sh --board xiao_samd21` checks for `bossac` after Zephyr
  setup.
- `seeed-zephyr flash xiao_samd21` fails early with a platform-specific install
  hint if `bossac` is missing.
- `seeed-zephyr flash xiao_samd21 --monitor` builds the repository USB CDC
  blinky example and uses Zephyr's bossac runner arguments for flashing.
- If no SAMD21 bootloader or USB CDC serial port is visible, the CLI reports a
  board-specific bootloader hint.

Verification:
- `brew install bossa`: passed on the active macOS host.
- `command -v bossac`: returned `/opt/homebrew/bin/bossac`.
- `bash -n scripts/setup-macos.sh`: passed.
- `bash -n scripts/setup-linux.sh`: passed.
- `bash -n scripts/lib/common.sh`: passed.
- `PYTHONPYCACHEPREFIX=/private/tmp/seeed-zephyr-pycache python3 -m py_compile tools/cli/seeed_zephyr.py`:
  passed.
- Stubbed macOS setup check: `xiao_samd21` installs `bossa`, `xiao_esp32c6`
  installs no board-specific Homebrew package, and no-board setup installs
  `bossa`.
- Stubbed Linux setup check: `xiao_samd21` installs `bossa-cli` on apt-get and
  `bossa` on dnf, `xiao_esp32c6` installs no board-specific package, and
  no-board setup installs the SAMD21 BOSSA package.
- `scripts/seeed-zephyr flash --help`: passed.
- Missing-tool preflight with `bossac` hidden from `PATH`: returned the expected
  `bossac was not found` install hint.
- CLI command-construction check: `xiao_samd21` produces
  `west flash --bossac-port <port> --delay 3`.
- CLI serial-wait check: waits until a single USB serial device appears.
- Direct Zephyr runner check:
  `/Users/mengdu/zephyrproject/.venv/bin/west flash --bossac-port /dev/cu.usbmodem1101 --delay 3`
  passed on the attached XIAO SAMD21 before the USB CDC example update.
- `scripts/seeed-zephyr build xiao_samd21`: passed with the repository USB CDC
  blinky example.
- `seeed-zephyr flash xiao_samd21 --monitor`: currently builds successfully,
  then reports no visible USB serial device with the SAMD21 bootloader hint.

Remaining:
- Put the attached XIAO SAMD21 into bootloader mode once, then rerun
  `seeed-zephyr flash xiao_samd21 --monitor` to flash the new USB CDC example
  and verify monitor output from the flashed firmware.

## 2026-06-20 - Fix monitor for non-Espressif boards

Scope:
- Updated `tools/cli/seeed_zephyr.py` so `monitor` and `flash --monitor`
  support `--port` and `--baud`.
- Removed the Espressif-only monitor preflight check that blocked
  non-Espressif boards before build or flash.
- Updated README, Getting Started docs, and CLI docs.
- Removed the completed `AI use/TODO-fix-monitor.md` handoff file.

Reason:
- Hardware testing for `xiao_samd21` was blocked because
  `seeed-zephyr flash xiao_samd21 --monitor` rejected non-Espressif boards
  before the board was built or flashed.

Result:
- Espressif boards still use Zephyr's `west espressif monitor`.
- Non-Espressif boards use pyserial miniterm from the Zephyr venv.
- `seeed-zephyr monitor <board_id>` can auto-detect one USB serial device when
  `--port` is omitted.
- `seeed-zephyr flash <board_id> --monitor [--port <device>] [--baud <rate>]`
  now builds and flashes first, then opens a serial monitor for the selected
  board. `--port` is optional when auto-detection finds one USB serial device.

Verification:
- `PYTHONPYCACHEPREFIX=/private/tmp/seeed-zephyr-pycache python3 -m py_compile tools/cli/seeed_zephyr.py`:
  passed.
- `scripts/seeed-zephyr monitor --help`: showed `--port` and `--baud`.
- `scripts/seeed-zephyr flash --help`: showed `--monitor`, `--port`, and
  `--baud`.
- `scripts/seeed-zephyr monitor xiao_esp32c5`: returned the expected
  unsupported board error.
- `scripts/seeed-zephyr flash xiao_esp32c5 --monitor --port /dev/null`:
  returned the expected unsupported board error.
- `scripts/seeed-zephyr monitor xiao_samd21`: reached the non-Espressif serial
  monitor path and returned the expected no-USB-device error in the current
  no-board environment.
- `scripts/seeed-zephyr monitor xiao_samd21 --port /dev/null`: invoked
  pyserial miniterm from the Zephyr venv and failed on the invalid port, proving
  the Espressif-only rejection was removed.
- `/Users/mengdu/zephyrproject/.venv/bin/python tools/validate_metadata/validate.py`:
  29 passed, 0 failed.
- `scripts/seeed-zephyr build xiao_samd21`: passed after clearing a stale
  generated Zephyr build directory.
- `git diff --check`: passed.
- Sensitive keyword scan over README, docs, scripts, tools, metadata, examples,
  `AI use/`, and `.github`: no matches.

Remaining:
- Resume physical-board testing for `xiao_samd21`, then continue with
  `xiao_nrf52840`, `xiao_nrf54l15`, `xiao_rp2040`, `xiao_rp2350`, `xiao_mg24`,
  and `xiao_ra4m1`.

## 2026-06-20 - Add CLI debug delegation

Scope:
- Updated `tools/cli/seeed_zephyr.py` with `seeed-zephyr debug <board_id>`.
- Updated `tools/cli/README.md` and root `README.md` CLI guidance.
- Appended this work log entry.

Reason:
- The CLI needed a debug command while staying a thin repository knowledge
  layer that selects the board/example and delegates execution to Zephyr.

Result:
- `seeed-zephyr debug <board_id>` resolves the same selected repository example
  as `build` and `flash`.
- Unsupported boards are rejected before build or debug execution.
- Supported boards are built through the existing `west build` path, then debug
  is delegated to `west debug`.
- If `west debug` fails, Zephyr's command output remains visible and the CLI
  appends a hint that debugging needs hardware debugger support.

Verification:
- `PYTHONPYCACHEPREFIX=/private/tmp/seeed-zephyr-pycache python3 -m py_compile tools/cli/seeed_zephyr.py`:
  passed.
- `scripts/seeed-zephyr --help`: showed `{list,build,flash,debug,monitor,matrix,verify-hardware}`.
- `scripts/seeed-zephyr debug --help`: showed `usage: seeed-zephyr debug [-h] board_id`.
- `scripts/seeed-zephyr debug xiao_esp32c5`: returned
  `Error: xiao_esp32c5 is unsupported in the selected Zephyr baseline.`
- `git diff --check`: passed.

Remaining:
- A real `west debug` session was not started because it requires attached
  hardware debugger support.

## 2026-06-20 - Add startup banners to board examples

Scope:
- Added a one-line startup banner to every `examples/boards/*/*/src/main.c`.

Reason:
- During batch hardware testing across XIAO boards, serial output should identify
  which board and demo is running. blinky printed only "LED state" and hello_world
  only "demo is running", with no board/demo identity in the output.

Result:
- Each example now prints, as the first line of `main()`:
  `*** Seeed XIAO Zephyr Base | board: <CONFIG_BOARD> | demo: <blinky|hello_world> ***`
- The banner line is identical across all 11 examples; only the demo name differs.
- Existing logic is unchanged (blinky LED loop, hello_world loop).

Verification:
- grep confirmed 11 identical banner lines (9 blinky, 2 hello_world).
- `scripts/seeed-zephyr build xiao_esp32c6`: build succeeded, ESP32-C6 image created;
  FLASH usage 133180 B (about 160 B more than before). The banner did not break the build.

Remaining:
- Confirm the banner appears on the serial monitor during real hardware testing of
  each board.

## 2026-06-20 - Delegate CLI execution to Zephyr tools

Scope:
- Refactored `tools/cli/seeed_zephyr.py` so `build`, `flash`, and
  `verify-hardware` select repository examples, then call Zephyr `west`
  commands directly.
- Updated README, Getting Started docs, script docs, CLI docs, Phase 1 and
  Phase 2 AI guidance, and validation evidence to state the CLI boundary.
- Added an AI constraint that CLI execution for build, flash, and monitor must
  stay delegated to Zephyr `west` commands or Zephyr module tools.

Reason:
- The CLI should be a repository knowledge layer for selecting boards,
  examples, and validated metadata. Zephyr should remain the execution layer for
  building, flashing, and monitoring firmware.

Result:
- `seeed-zephyr build <board_id>` now calls `west build` directly after
  resolving the repository example and Zephyr target.
- `seeed-zephyr flash <board_id>` now calls `west build`, then `west flash`.
- `seeed-zephyr flash <board_id> --monitor` now calls `west build`,
  `west flash`, and then Zephyr's Espressif monitor through
  `west espressif monitor`.
- CLI progress messages flush before Zephyr output, so logs appear in the
  expected order.

Verification:
- `bash -n scripts/setup-macos.sh`: passed.
- `bash -n scripts/seeed-zephyr`: passed.
- `PYTHONPYCACHEPREFIX=/tmp/seeed-zephyr-pycache python3 -m py_compile tools/cli/seeed_zephyr.py`:
  passed.
- `scripts/seeed-zephyr flash --help`: passed.
- `scripts/seeed-zephyr build xiao_esp32c5`: returned the expected unsupported
  board error.
- `scripts/seeed-zephyr flash xiao_nrf52840 --monitor`: returned the expected
  Espressif-only monitor error before build or flash.
- `/Users/mengdu/zephyrproject/.venv/bin/python tools/validate_metadata/validate.py`:
  29 passed, 0 failed.
- `scripts/seeed-zephyr build xiao_esp32c3`: passed through direct
  `west build` delegation.
- `seeed-zephyr flash xiao_esp32c6 --monitor` in a TTY session: build passed,
  flash wrote 144300 bytes, hash verification passed, monitor opened on
  `/dev/cu.usbmodem101`, Zephyr booted, and `LED state` toggles were observed
  in serial output.

Remaining:
- Keep `scripts/build-example.sh` only as a project-root helper unless a later
  workflow still needs it. The CLI should not depend on it for normal build or
  flash operations.

## 2026-06-20 - Fix Espressif flash environment

Scope:
- Updated `tools/cli/seeed_zephyr.py` so all `west` calls run with the Zephyr
  venv `bin` directory prepended to `PATH`.
- Added an Espressif flash dependency check for `esptool` before `west flash`.
- Updated `scripts/setup-macos.sh` to check Zephyr's `hal_espressif` flash and
  monitor tools when an Espressif board is selected.
- Added hardware validation evidence for `xiao_esp32c6` flash and monitor.

Reason:
- Espressif's Zephyr runner launches `esptool` by command name. The Espressif
  monitor is a `hal_espressif` west extension that launches ESP-IDF's
  `idf_monitor.py`. Calling `/Users/mengdu/zephyrproject/.venv/bin/west`
  directly is not enough if the venv `bin` directory is absent from `PATH`.

Result:
- `seeed-zephyr flash xiao_esp32c6 --monitor` no longer fails with
  `FileNotFoundError: esptool`.
- The command builds, flashes, verifies written data, opens the monitor, and
  shows Zephyr boot output plus `LED state` toggles on the physical XIAO
  ESP32C6.

Verification:
- `/Users/mengdu/zephyrproject/.venv/bin/python -m pip show esptool`: found
  esptool 5.3.0 in the Zephyr venv.
- `/Users/mengdu/zephyrproject/.venv/bin/esptool version`: returned 5.3.0.
- `bash -n scripts/setup-macos.sh`: passed.
- `bash -n scripts/seeed-zephyr`: passed.
- `PYTHONPYCACHEPREFIX=/tmp/seeed-zephyr-pycache python3 -m py_compile tools/cli/seeed_zephyr.py`:
  passed.
- `scripts/seeed-zephyr flash --help`: passed.
- `scripts/seeed-zephyr flash xiao_esp32c5 --monitor`: returned the expected
  unsupported board error.
- `scripts/seeed-zephyr flash xiao_nrf52840 --monitor`: returned the expected
  Espressif-only monitor error before build or flash.
- `source scripts/setup-macos.sh; check_espressif_zephyr_tools`: confirmed
  Zephyr's `hal_espressif` monitor file and venv `esptool` are available.
- `source scripts/setup-macos.sh; BOARD_VENDOR=espressif; check_board_host_tools`:
  confirmed Zephyr's Espressif tools are available.
- `source scripts/setup-macos.sh; BOARD_VENDOR=nordic; check_board_host_tools`:
  returned without checking Espressif tools.
- `seeed-zephyr flash xiao_esp32c6 --monitor` in a TTY session: build passed,
  flash wrote 144300 bytes, hash verification passed, monitor opened on
  `/dev/cu.usbmodem101`, Zephyr booted, and `LED state` toggles were observed
  in serial output.
- `/Users/mengdu/zephyrproject/.venv/bin/python tools/validate_metadata/validate.py`:
  29 passed, 0 failed.
- `git diff --check`: passed.
- Directory README coverage check: no project directory missing `README.md`.
- Sensitive keyword scan over README, docs, scripts, tools, metadata, examples,
  `AI use/`, and `.github`: no matches.

Remaining:
- Add equivalent real hardware flash/monitor evidence for other Espressif
  boards when hardware is available.

## 2026-06-20 - Add flash monitor option

Scope:
- Added `--monitor` to `seeed-zephyr flash <board_id>`.
- Reused the same monitor support check for `monitor` and `flash --monitor`.
- Updated README, Getting Started docs, CLI docs, and validation evidence.

Reason:
- Users need one command that performs build, flash, and monitor for supported
  boards.

Result:
- `seeed-zephyr flash <board_id>` still performs build and flash.
- `seeed-zephyr flash <board_id> --monitor` performs build, flash, and then
  opens the monitor after a successful flash.
- Non-Espressif boards are rejected before build or flash when `--monitor` is
  requested, because monitor support is currently Espressif-only.

Verification:
- `bash -n scripts/seeed-zephyr`: passed.
- `PYTHONPYCACHEPREFIX=/tmp/seeed-zephyr-pycache python3 -m py_compile tools/cli/seeed_zephyr.py`:
  passed.
- `scripts/seeed-zephyr flash --help`: showed `--monitor`.
- `scripts/seeed-zephyr flash xiao_esp32c5 --monitor`: returned the expected
  unsupported board error.
- `scripts/seeed-zephyr flash xiao_nrf52840 --monitor`: returned the expected
  Espressif-only monitor error before build or flash.
- `/Users/mengdu/zephyrproject/.venv/bin/python tools/validate_metadata/validate.py`:
  29 passed, 0 failed.
- `git diff --check`: passed.
- Directory README coverage check: no project directory missing `README.md`.
- Sensitive keyword scan over README, docs, scripts, tools, metadata, examples,
  `AI use/`, and `.github`: no matches.

Remaining:
- `seeed-zephyr flash <board_id> --monitor` still needs real hardware validation
  for each board because it requires flashing and opening a live monitor.

## 2026-06-20 - Install CLI as a global user command

Scope:
- Updated `scripts/setup-macos.sh` to ask whether to install the
  `seeed-zephyr` CLI, defaulting to installation.
- Updated `scripts/seeed-zephyr` so an installed symlink resolves back to the
  repository root.
- Updated `tools/cli/seeed_zephyr.py` to accept the repository root from the
  launcher environment.
- Updated README, Getting Started docs, script docs, CLI docs, and validation
  evidence to describe `seeed-zephyr` as the normal command.

Reason:
- The user-facing CLI should be available as `seeed-zephyr` from any directory
  after setup, not only as `scripts/seeed-zephyr` from the repository root.

Result:
- `setup-macos.sh` now prompts `Install seeed-zephyr CLI? [Y/n]`.
- Pressing Enter installs the command.
- If the selected install directory is in `PATH`, users can run
  `seeed-zephyr` from any directory.
- If the selected install directory is not in `PATH`, setup prints the exact
  `PATH` line and an absolute command fallback.
- If installation is skipped, setup prints the repository-local fallback.

Verification:
- `bash -n scripts/setup-macos.sh`: passed.
- `bash -n scripts/seeed-zephyr`: passed.
- `PYTHONPYCACHEPREFIX=/tmp/seeed-zephyr-pycache python3 -m py_compile tools/cli/seeed_zephyr.py`:
  passed.
- Temporary install to `/tmp/seeed-zephyr-cli-test-bin`: passed.
- From `/tmp`, `seeed-zephyr --help`: passed.
- From `/tmp`, `seeed-zephyr list boards`: passed.
- From `/tmp`, `seeed-zephyr list examples`: passed.
- From `/tmp`, `seeed-zephyr build xiao_esp32c5`: returned the expected
  unsupported board error.
- From `/tmp`, `seeed-zephyr build xiao_esp32c3`: passed.
- Non-interactive default install through `install_cli_if_requested`: installed
  and listed boards successfully.
- `/Users/mengdu/zephyrproject/.venv/bin/python tools/validate_metadata/validate.py`:
  29 passed, 0 failed.
- `git diff --check`: passed.
- Directory README coverage check: no project directory missing `README.md`.
- Sensitive keyword scan over README, docs, scripts, tools, metadata, examples,
  `AI use/`, and `.github`: no matches.

Remaining:
- Real user setup runs should confirm the final chosen install directory on
  machines where neither `~/.local/bin` nor `/opt/homebrew/bin` is in `PATH`.

## 2026-06-20 - Add repository CLI for examples and hardware checks

Scope:
- Added `tools/cli/seeed_zephyr.py` as the repository command-line interface.
- Added `scripts/seeed-zephyr` as the user-facing wrapper.
- Added `tools/cli/README.md`.
- Added `AI use/HARDWARE_VERIFICATION.md` as the destination for real hardware
  observations captured through the CLI.
- Updated README, Getting Started docs, script docs, tool docs, and the macOS
  setup script to point users to the CLI.

Reason:
- Users need one project-root command for listing boards, listing examples,
  building demos, flashing hardware, opening a monitor, running the build
  matrix, and recording hardware checks.
- The CLI should operate repository-owned examples before any project generator
  or editor extension becomes the primary workflow.

Result:
- `scripts/seeed-zephyr list boards` shows board ids, validation status, demo
  type, vendor, and Zephyr target.
- `scripts/seeed-zephyr list examples` shows each board's selected repository
  example.
- `scripts/seeed-zephyr build <board_id>` builds the board's selected
  repository example.
- `scripts/seeed-zephyr flash <board_id>` builds and flashes the selected
  example.
- `scripts/seeed-zephyr monitor <board_id>` opens the Espressif monitor for
  Espressif boards.
- `scripts/seeed-zephyr matrix` runs the full repository example build matrix.
- `scripts/seeed-zephyr verify-hardware <board_id>` builds, flashes, prompts
  for the observed board behavior, and appends the result under `AI use/`.

Verification:
- `python3 -m py_compile tools/cli/seeed_zephyr.py`: passed.
- `bash -n scripts/seeed-zephyr`: passed.
- `scripts/seeed-zephyr --help`: passed.
- `scripts/seeed-zephyr list boards`: passed.
- `scripts/seeed-zephyr list examples`: passed.
- `scripts/seeed-zephyr build xiao_esp32c5`: returned the expected unsupported
  board error.
- `scripts/seeed-zephyr build xiao_esp32c3`: passed.
- `scripts/seeed-zephyr matrix`: total=11, pass=10, fail=0, unsupported=1.
- `/Users/mengdu/zephyrproject/.venv/bin/python tools/validate_metadata/validate.py`:
  29 passed, 0 failed.
- `git diff --check`: passed.
- Directory README coverage check: no project directory missing `README.md`.
- Sensitive keyword scan over README, docs, scripts, tools, metadata, examples,
  `AI use/`, and `.github`: no matches.

Remaining:
- Run `scripts/seeed-zephyr verify-hardware <board_id>` on each physical board
  as hardware becomes available.
- Extend the CLI after Grove examples and project examples exist.
- Add project/example generation commands only after templates and validation
  rules are ready.

## 2026-06-20 - Add repository board demos and build scripts

Scope:
- Added `examples/boards/` repository-owned demos for all 11 tracked XIAO board
  metadata entries.
- Added `scripts/build-example.sh` for building one repository example from the
  project root.
- Updated `tools/build_matrix/run.sh` and `board-overrides.tsv` to build
  repository examples instead of upstream Zephyr sample paths.
- Extended `tools/validate_metadata/validate.py` to validate
  `examples/**/example.yaml` descriptors.
- Updated README, Getting Started docs, script docs, build matrix docs, and
  validation evidence.

Reason:
- The repository needs its own buildable example assets before generator or
  plugin work can be meaningful.
- Users should build XIAO demos from this repository instead of manually
  searching upstream Zephyr sample directories.

Result:
- 10 supported XIAO board targets now build repository-owned demos.
- XIAO ESP32C3 uses `hello_world` because it has no on-board LED.
- XIAO ESP32C5 is tracked with an unsupported demo record because Zephyr v4.4.0
  does not provide a `xiao_esp32c5` board target.

Verification:
- `bash -n scripts/build-example.sh`: passed.
- `bash -n scripts/setup-macos.sh`: passed.
- `bash -n tools/build_matrix/run.sh`: passed.
- `/Users/mengdu/zephyrproject/.venv/bin/python tools/validate_metadata/validate.py`:
  29 passed, 0 failed.
- `bash scripts/build-example.sh examples/boards/xiao_esp32c3/hello_world`:
  passed.
- `BUILD_MATRIX_GENERATED_ON=2026-06-20 bash tools/build_matrix/run.sh`:
  total=11, pass=10, fail=0, unsupported=1.

Remaining:
- Add hardware-tested evidence for the new repository demos.
- Add the first Grove module examples under `examples/grove/`.
- Enable XIAO ESP32C5 when the selected Zephyr baseline provides a real XIAO
  board target or a project-local board definition is intentionally added and
  validated.

## 2026-06-20 - Align AI charter with examples and projects mission

Scope:
- Reframed `AI use/` as the AI-facing project charter folder.
- Added the requirement that AI constraints, AI handoff notes, and AI work logs
  live under `AI use/`.
- Reoriented the strategic documents toward examples, projects, capability
  coverage, validation evidence, and community contributions as the primary
  product assets.
- Added bilingual README files to project directories.

Reason:
- Future AI agents need a clear mission without relying on private conversation context.
- The project direction should be stated as reusable examples, projects,
  validation evidence, and contribution workflow.

Result:
- The project direction now starts from user-facing examples and complete projects.
- CLI, VS Code plugin, setup scripts, and metadata are framed as support systems
  around the example/project catalog.

Verification:
- `bash -n scripts/setup-macos.sh`: passed.
- `bash -n tools/build_matrix/run.sh`: passed.
- `/Users/mengdu/zephyrproject/.venv/bin/python tools/validate_metadata/validate.py`:
  18 passed, 0 failed.
- `git diff --check`: passed.
- Sensitive keyword scan over README, docs, scripts, tools, metadata, `AI use/`,
  and `.github`: no matches.
- Directory README coverage check: no project directory missing `README.md`.
- Corrective negative-direction keyword scan: no matches outside factual
  validation/status wording.

Remaining:
- Create the first repository-owned examples under `examples/`.
- Add contribution rules for community examples and projects.

## 2026-06-20 - Add Linux setup entrypoint

Scope:
- Added `scripts/setup-linux.sh`.
- Updated `scripts/README.md` to list the Linux setup script.
- Appended this work log entry.

Reason:
- The cross-platform setup path needed a Linux phase that mirrors the macOS
  platform-entry pattern while keeping the Zephyr workspace flow centralized in
  `scripts/lib/common.sh`.

Result:
- `setup-linux.sh` sets the same platform variables as `setup-macos.sh`, then
  sources `scripts/lib/common.sh`.
- Linux-specific work is limited to host package installation, serial group
  membership, optional `plugdev` membership, and available Zephyr SDK/OpenOCD
  udev rule installation.
- The script keeps board selection, venv, west, SDK installation, package
  installation, blob fetching, CLI installation, and next-step output delegated
  to the shared common setup flow.
- The script header clearly states `NOT YET VERIFIED ON REAL LINUX`.

Verification:
- Written and bash-syntax-checked on macOS only.
- `bash -n scripts/setup-linux.sh`: passed.
- Structural checks confirmed that the script sources `scripts/lib/common.sh`,
  defines `install_system_dependencies`, sets the same platform variables as
  `setup-macos.sh`, and calls `run_setup_flow "$@"` only when executed directly.

Remaining:
- NOT YET VERIFIED ON REAL LINUX. Package installation, group changes, udev
  copying, and real flash/monitor/debug device access still need validation on
  Debian/Ubuntu and Fedora machines.

## 2026-06-20 - Add Windows WSL2 setup preparer

Scope:
- Added `scripts/setup-windows.ps1`.
- Updated `scripts/README.md` to list the Windows setup entrypoint.
- Appended this work log entry.

Reason:
- Phase 3 of cross-platform setup needs a Windows path that stays Zephyr-first:
  Windows only prepares WSL2 and USB forwarding, while the actual Zephyr setup
  remains delegated to the existing `scripts/setup-linux.sh` inside WSL2.

Result:
- `scripts/setup-windows.ps1` checks for WSL2, reports or starts `wsl --install`
  when no distro exists, and reports the detected default WSL distro when found.
- The script checks for `usbipd`, installs usbipd-win with
  `winget install --exact --id dorssel.usbipd-win` when possible, and prints an
  actionable message when winget or Administrator rights are missing.
- The script prints the interactive per-device USB forwarding flow:
  `usbipd list`, `usbipd bind --busid <BUSID>`, and
  `usbipd attach --wsl --busid <BUSID>`.
- The script prominently states `NOT YET VERIFIED ON REAL WINDOWS`.

Verification:
- NOT YET VERIFIED ON REAL WINDOWS.
- This was written on macOS, where no PowerShell runtime or Windows WSL/usbipd
  environment is available.
- macOS-side verification was limited to careful source review for PowerShell
  syntax, quoting, and the intended `wsl`, `winget`, and `usbipd` command lines.

Remaining:
- Run `powershell -ExecutionPolicy Bypass -File scripts/setup-windows.ps1` on a
  real Windows 10 2004+ or Windows 11 machine.
- Validate `wsl --status`, `wsl -l -v`, `winget install --exact --id dorssel.usbipd-win`,
  and the usbipd XIAO attach flow on real hardware.

## 2026-06-20 - Sync cross-platform setup and debug docs

Scope:
- Updated `README.md`, `docs/en/getting-started.md`, and `docs/zh/getting-started.md`.
- Appended this work log entry.

Result:
- Added macOS, Linux, and Windows setup entry points to the user-facing setup docs.
- Marked Linux and Windows setup as written but pending real-platform validation.
- Listed `build`, `flash`, `monitor`, and `debug` together in the CLI usage docs.

Verification:
- Grep checks confirmed `setup-linux.sh`, `setup-windows.ps1`, and `seeed-zephyr debug`
  appear in `README.md`, `docs/en/getting-started.md`, and `docs/zh/getting-started.md`.

## 2026-06-20 - Hardware blinky testing: c6/s3/c3 PASS, samd21 blocked

Scope:
- Real hardware testing of `seeed-zephyr flash <board> --monitor` on physical
  XIAO boards.

Result:
- xiao_esp32c6: PASS — LED blinks, serial output confirmed with banner.
- xiao_esp32s3: PASS — LED blinks, serial output confirmed.
- xiao_esp32c3: PASS — hello_world serial output confirmed (no on-board LED).
- xiao_samd21: BLOCKED — `seeed-zephyr flash xiao_samd21 --monitor` rejected
  with "Monitor is currently implemented for Espressif boards only" before
  flashing. The `flash --monitor` path checks monitor support BEFORE building,
  so non-Espressif boards never even start the build/flash sequence.

Remaining:
- Fix CLI monitor to support non-Espressif boards (see next entry).
- After fix: resume samd21 testing, then test nrf52840, nrf54l15, rp2040,
  rp2350, mg24, ra4m1.

## 2026-06-20 - Monitor investigation: Zephyr has no generic west monitor

Scope:
- Investigated whether Zephyr provides a built-in serial monitor for
  non-Espressif boards.

Result:
- `west --help` in the v4.4.0 workspace lists NO generic `west monitor`
  command. Only `west espressif monitor` exists (hal_espressif extension).
- Zephyr GitHub Issue #97954 (opened 2025-10-21) proposes adding
  `west monitor`, but as of 2026-06-20 it is still Open with no PR and no
  target release version.
- `west rtt` exists but requires a J-Link debugger (SEGGER RTT), not a
  standard serial connection.
- pyserial (`serial.tools.miniterm` and `serial.tools.list_ports`) is already
  installed in the Zephyr venv by `west packages pip --install`. It is a
  Zephyr dependency, not an externally introduced tool.

Decision:
- ESP32 boards: keep `west espressif monitor` (idf_monitor).
- Non-ESP32 boards: use pyserial miniterm from the Zephyr venv, invoked as
  a subprocess (`<venv>/bin/python -m serial.tools.miniterm <port> <baud>`).
  This keeps the CLI itself standard-library-only while using a tool Zephyr
  already installs.
- Add `--port` and `--baud` arguments to both `monitor` and `flash` commands.
- Auto-detect serial port via `serial.tools.list_ports` when `--port` is not
  given.

Remaining:
- Implement the above in `tools/cli/seeed_zephyr.py`.
- Update CLI docs, README, getting-started guides.
- Resume per-board hardware testing after implementation.
