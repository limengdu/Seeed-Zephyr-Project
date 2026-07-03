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

## 2026-06-20 - Clarify documentation scope

Scope:
- Updated `docs/README.md`.
- Updated `docs/zh/README.md` and `docs/en/README.md`.
- Updated `docs/zh/boards/README.md` and `docs/en/boards/README.md`.
- Reworked `docs/zh/boards/xiao-rp2040.md` and `docs/en/boards/xiao-rp2040.md`.
- Reworked `docs/zh/boards/xiao-samd21.md` and `docs/en/boards/xiao-samd21.md`.

Reason:
- User-facing documentation needs clear separation between complete process
  tutorials and board-specific development notes.

Result:
- Top-level docs now describe complete setup, CLI, build, flash, monitor, and
  validation flows.
- Board docs now focus on board-specific pitfalls and development tasks such as
  UF2, BOSSA, USB CDC serial, and bootloader entry.
- AI-facing work records remain under `AI use/`.

Verification:
- Checked that board pages no longer contain FAQ/checklist/validation-log
  headings.
- Checked local Markdown links.
- `git diff --check`: passed.

Remaining:
- None for this documentation scope update.

## 2026-06-20 - Add RP2350 USB CDC monitor support

Scope:
- Updated `examples/boards/xiao_rp2350/blinky`.
- Added XIAO RP2350 board development docs under `docs/en/boards/` and
  `docs/zh/boards/`.
- Updated board docs indexes.
- Added CLI regression coverage for RP2350 example requirements.

Reason:
- XIAO RP2350 UF2 flashing can succeed while `--monitor` fails if the running
  firmware does not expose a USB CDC serial device.

Result:
- The RP2350 baseline example now enables USB CDC serial output.
- The RP2350 baseline example now handles 1200-baud UF2 bootloader requests.
- The RP2350 example overlay provides the RP2350 boot-mode retention devicetree
  node required by Zephyr retention boot mode.
- The RP2350 repository default target is now `xiao_rp2350/rp2350a/m33`.

Verification:
- `xiao_rp2350/rp2350a/hazard3` built and copied by UF2, but did not enumerate
  a USB CDC serial device after flashing.
- `xiao_rp2350/rp2350a/m33` built, flashed through UF2, enumerated as
  `/dev/cu.usbmodem1101`, and printed repeated `LED state: ON/OFF` lines.
- `seeed-zephyr flash xiao_rp2350 --monitor` built the repository example,
  requested UF2 mode through USB CDC, copied `zephyr.uf2` to `/Volumes/RP2350`,
  opened pyserial miniterm, and printed repeated `LED state: ON/OFF` lines.

Remaining:
- None for the RP2350 M33 default target and monitor flow.

## 2026-06-20 - Route XIAO nRF52840 flashing through UF2

Scope:
- Updated `tools/cli/seeed_zephyr.py`.
- Updated `tools/cli/test_seeed_zephyr.py`.
- Added XIAO nRF52840 board development docs under `docs/en/boards/` and
  `docs/zh/boards/`.
- Updated CLI docs, Getting Started docs, and the nRF52840 example README.

Reason:
- The XIAO nRF52840 Zephyr board supports UF2 flashing through the Adafruit
  nRF52 Bootloader, but Zephyr's default runner selection used `nrfutil`.
  Ordinary XIAO nRF52840 boards do not have an onboard J-Link debugger, so the
  repository CLI should default to the UF2 path.

Result:
- `seeed-zephyr flash xiao_nrf52840 --monitor` now calls
  `west flash --runner uf2` after build.
- The CLI no longer treats missing `nrfutil` as the normal blocker for the
  repository nRF52840 UF2 flow.
- The CLI emits an nRF52840-specific double-tap RESET hint when no UF2 volume
  appears.

Verification:
- Added a failing regression test showing that `xiao_nrf52840` did not pass
  `--runner uf2`, then implemented the fix.
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/cli/test_seeed_zephyr.py`: passed,
  11 tests.
- `PYTHONPYCACHEPREFIX=/private/tmp/seeed-zephyr-pycache python3 -m py_compile tools/cli/seeed_zephyr.py tools/cli/test_seeed_zephyr.py`:
  passed.
- `/Users/mengdu/zephyrproject/.venv/bin/python tools/validate_metadata/validate.py`:
  passed, 29 total.
- `bash scripts/build-example.sh examples/boards/xiao_nrf52840/blinky`: passed.
- `seeed-zephyr flash xiao_nrf52840 --monitor`: built the repository example,
  attempted the UF2 path, and failed waiting for a UF2 mass-storage volume
  instead of failing on missing `nrfutil`.

Remaining:
- Put the physical XIAO nRF52840 into UF2 mode by double-tapping RESET, then
  rerun `seeed-zephyr flash xiao_nrf52840 --monitor` to complete hardware
  flash and monitor validation.

## 2026-06-20 - Refine RP2040 board guide

Scope:
- Rewrote `docs/zh/boards/xiao-rp2040.md`.
- Rewrote `docs/en/boards/xiao-rp2040.md`.

Reason:
- Board documentation should guide users through development tasks, not read
  like a validation log.

Result:
- The RP2040 board pages now focus on quick start, daily development, BOOTSEL
  usage, custom example requirements, and common issues.
- Hardware validation details remain in `AI use/HARDWARE_VERIFICATION.md`.

Verification:
- Checked that the RP2040 board pages no longer contain log-style validation
  wording.
- Checked local Markdown links.
- `git diff --check`: passed.

Remaining:
- None for the RP2040 board guide rewrite.

## 2026-06-20 - Fix RP2040 automatic UF2 repeated flashing

Scope:
- Updated `tools/cli/seeed_zephyr.py` so Raspberry Pi UF2 flashing detects UF2
  volumes before `west flash`, requests XIAO RP2040 UF2 mode through USB CDC at
  1200 baud when needed, waits for the UF2 volume, and then delegates flashing
  to Zephyr.
- Added `rp2-boot-mode-retention` to Raspberry Pi builds through
  `tools/cli/seeed_zephyr.py`, `scripts/build-example.sh`, and
  `tools/build_matrix/run.sh`.
- Updated `examples/boards/xiao_rp2040/blinky` so the firmware handles USB CDC
  1200-baud requests and reboots through Zephyr's RP2040 boot-mode retention
  path.
- Expanded `tools/cli/test_seeed_zephyr.py` coverage for UF2 volume detection,
  1200-baud requests, timeout hints, explicit ports, and RP2 build snippets.
- Updated RP2040 user docs, CLI docs, example docs, build matrix results, and
  hardware verification evidence.

Reason:
- Requiring manual BOOTSEL for every XIAO RP2040 flash is not acceptable after
  repository firmware is installed, because the board can expose USB CDC serial
  and use a 1200-baud request to enter UF2 mode automatically.

Result:
- A first install from older firmware may still use manual BOOTSEL.
- After the repository firmware is running, repeated
  `seeed-zephyr flash xiao_rp2040 --monitor` runs can request UF2 mode
  automatically, copy `zephyr.uf2`, and reopen the serial monitor.
- Manual BOOTSEL remains the recovery path when no compatible running firmware
  or USB CDC serial port is available.

Verification:
- Added a failing regression test first for the 1200-baud touch duration, then
  implemented the fix.
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/cli/test_seeed_zephyr.py`: passed,
  8 tests.
- `PYTHONPYCACHEPREFIX=/private/tmp/seeed-zephyr-pycache python3 -m py_compile tools/cli/seeed_zephyr.py tools/cli/test_seeed_zephyr.py`:
  passed.
- `bash -n scripts/build-example.sh tools/build_matrix/run.sh`: passed.
- `scripts/seeed-zephyr build xiao_rp2040`: passed; output included
  `Snippet(s): rp2-boot-mode-retention`.
- Hardware first install: `seeed-zephyr flash xiao_rp2040 --monitor` passed
  with `/Volumes/RPI-RP2` already mounted, copied `zephyr.uf2`, opened
  `/dev/cu.usbmodem1101`, and printed repeated LED state lines.
- Hardware repeated flash: second, third, and fourth consecutive
  `seeed-zephyr flash xiao_rp2040 --monitor` runs passed without manual
  BOOTSEL. Each run requested UF2 mode via `/dev/cu.usbmodem1101` at 1200 baud,
  detected `/Volumes/RPI-RP2`, copied `zephyr.uf2`, reopened pyserial miniterm,
  and printed repeated LED state lines.

Remaining:
- Normal unplug/replug after the repository firmware is installed should expose
  the same USB CDC serial interface, but a dedicated replug hardware record has
  not yet been captured.

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
- User-facing docs for RP2040 were later updated by the automatic UF2
  repeated-flashing verification entry.

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
- Before automatic UF2 request support was added to the repository firmware,
  the older firmware path produced the expected UF2 error and CLI hint.

Remaining:
- This earlier repeated-flash conclusion was replaced by the later automatic
  UF2 repeated-flashing verification entry.

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

## 2026-06-20 - Fix XIAO nRF52840 UF2 repeat flashing and monitor readiness

Scope:
- Updated `examples/boards/xiao_nrf52840/blinky` so the running firmware can
  respond to USB CDC 1200 baud bootloader requests.
- Updated `tools/cli/seeed_zephyr.py` so non-Espressif monitor startup waits
  until the serial port can actually be opened.
- Updated nRF52840 board docs and getting-started guides.

Result:
- nRF52840 repository firmware now checks `UART_LINE_CTRL_BAUD_RATE`; when it
  sees 1200 baud, it writes Adafruit nRF52 bootloader magic `0x57` to GPREGRET
  and reboots.
- `seeed-zephyr flash xiao_nrf52840 --monitor` still uses Zephyr's UF2 runner.
- The monitor path now retries while a newly re-enumerated serial port is still
  temporarily busy, which avoids opening miniterm too early after UF2 copy.
- The UF2 `flash --monitor` path now waits for the UF2 mass-storage volume to
  detach before opening monitor, so it does not reuse the bootloader serial
  device while the board is rebooting into the application.

Verification:
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/cli/test_seeed_zephyr.py`
- `PYTHONPYCACHEPREFIX=/private/tmp/seeed-zephyr-pycache python3 -m py_compile tools/cli/seeed_zephyr.py tools/cli/test_seeed_zephyr.py`
- `/Users/mengdu/zephyrproject/.venv/bin/python tools/validate_metadata/validate.py`
- `bash scripts/build-example.sh examples/boards/xiao_nrf52840/blinky`
- `seeed-zephyr flash xiao_nrf52840 --monitor` built successfully, then timed
  out waiting for the UF2 volume because the board was still running firmware
  without the 1200 baud bootloader request handler.
- After the updated firmware was installed, a consecutive
  `seeed-zephyr flash xiao_nrf52840 --monitor` run requested UF2 mode at 1200
  baud, detected `/Volumes/XIAO-SENSE`, copied `zephyr.uf2`, waited for UF2
  detach, opened pyserial miniterm, and observed repeated LED state output.

Remaining:
- Continue with the next board in the hardware verification sequence.

## 2026-06-21 - Route XIAO MG24 flashing through Zephyr PyOCD

Scope:
- Reverted the earlier MG24 OpenOCD-default implementation.
- Updated the CLI so only `xiao_mg24` uses Zephyr's official `pyocd` runner.
- Updated setup to install the MG24 CMSIS pack for `xiao_mg24`, and during
  full no-board setup.
- Added MG24 board notes and recorded the XIAO nRF54L15 hardware pass.

Result:
- MG24 flashing stays on Zephyr tooling and no longer defaults to an external
  OpenOCD package path.
- OpenOCD is documented only as a board-specific fallback path.

Verification:
- `pyocd pack install EFR32MG24` did not match the current pyOCD pack index.
- `pyocd pack install EFR32MG24B220F1536IM48` installed
  `SiliconLabs.GeckoPlatform_EFR32MG24_DFP.2025.12.1`.
- `seeed-zephyr flash xiao_mg24 --monitor` built the repository example,
  flashed through Zephyr's `pyocd` runner, opened pyserial miniterm, and
  observed repeated LED state output.

## 2026-06-21 - Switch XIAO RA4M1 flash path to USB DFU

Scope:
- Reverted the prior RA4M1 RFP CLI dependency handling.
- Investigated Seeed's XIAO RA4M1 Arduino package and confirmed the board
  upload path uses `dfu-util` with VID/PID `2886:8049`.
- Updated the repository RA4M1 example to start after the board USB DFU
  bootloader at `0x4000`.

Result:
- `seeed-zephyr flash xiao_ra4m1` no longer requires Renesas Flash Programmer
  CLI or `rfp-cli`.
- The CLI generates `zephyr.ra4m1.dfu.bin` from `zephyr.elf`, excluding the
  high-address `.option_setting_osis` section so the DFU image stays compact.
- The CLI uploads the compact image with
  `dfu-util --device 2886:0049,:8049 -D ... -a 0 -R`.
- setup now installs/checks `dfu-util` for `xiao_ra4m1` and full setup.
- The baseline RA4M1 example now starts at `0x4000` and routes console output
  through USB CDC serial.

Reasoning evidence:
- Seeed Arduino `boards.txt` sets `XIAO_RA4M1.upload.tool=dfu-util`,
  `XIAO_RA4M1.upload.pid=0x8049`, and `XIAO_RA4M1.upload.interface=0`.
- Seeed Arduino `memory_regions.ld` sets `FLASH_IMAGE_START = 0x4000`.
- Zephyr's default RA4M1 `zephyr.bin` includes a high-address option-setting
  section, producing a sparse 16 MB binary that is not suitable for direct DFU
  upload.

Verification:
- `brew install dfu-util` installed `dfu-util 0.11` for local hardware testing.
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/cli/test_seeed_zephyr.py`
- `PYTHONPYCACHEPREFIX=/private/tmp/seeed-zephyr-pycache python3 -m py_compile tools/cli/seeed_zephyr.py tools/cli/test_seeed_zephyr.py`
- `/Users/mengdu/zephyrproject/.venv/bin/python tools/validate_metadata/validate.py`
- `bash scripts/build-example.sh examples/boards/xiao_ra4m1/blinky`
- `seeed-zephyr flash xiao_ra4m1 --monitor` built the example and completed a
  DFU upload of 21256 bytes while the previous firmware exposed DFU runtime.
- Homebrew `dfu-util 0.11` rejected Arduino's `-Q` option; the CLI was changed
  to the supported `-R` reset option.
- After replacing the previous firmware with the Zephyr app, a later flash
  attempt found no DFU-capable USB device. This shows runtime DFU re-entry is
  not yet solved for Zephyr-generated RA4M1 firmware.

## 2026-06-21 - Add XIAO RA4M1 runtime DFU request path

Scope:
- Added a RA4M1 application-side bootloader request path to the baseline
  example.
- Updated the CLI to detect both Seeed DFU VID/PID values and the Renesas ROM
  bootloader serial state.
- Updated RA4M1 board development notes in Chinese and English.

Result:
- The RA4M1 baseline example watches USB CDC line-control baud rate. When the
  host requests 1200 baud, it writes `0x07738135` to `R_SYSTEM->VBTBKR[0]`,
  disconnects the USB D+ pull-up, and resets.
- `seeed-zephyr flash xiao_ra4m1` can request DFU automatically after firmware
  with this entry path is installed.
- If the host sees `RA USB Boot` / `045B:0261`, the CLI now reports that this is
  Renesas ROM bootloader state, not the Seeed DFU target used by `dfu-util`.

Verification:
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/cli/test_seeed_zephyr.py`
- `PYTHONPYCACHEPREFIX=/private/tmp/seeed-zephyr-pycache python3 -m py_compile tools/cli/seeed_zephyr.py tools/cli/test_seeed_zephyr.py`
- `scripts/seeed-zephyr build xiao_ra4m1`
- Non-invasive USB checks after build found no active XIAO RA4M1 DFU or USB CDC
  serial device on the host, so consecutive hardware flash verification is still
  pending.

## 2026-07-02 - Add board-agnostic Grove example framework

Scope:
- New directory `examples/grove/<module_id>/<demo>/` with a Grove `example.yaml`
  contract (kind/module_id/interface/connector/pin_policy/pins/excluded_boards).
- New pilot example `examples/grove/grove_scd41_co2_temperature_humidity_sensor/basic_read/`.
- New `metadata/form_factors/xiao.yaml` (XIAO 14-pin physical layout).
- New `metadata/status/` with the example x board status matrix and its README.
- Board metadata gained `reserved_pins`, `analog_pins`, `pin_map`, `pin_map_source`.
- CLI (`tools/cli/seeed_zephyr.py`): `grove/<module>/<demo>` references on
  build/flash/debug; `--pin` on build/flash/debug/create; `show pins --json`;
  `show example` grove support with per-board status; `list grove` with examples;
  `create` cross-board generation.
- `tools/validate_metadata/validate.py`: Grove example schema checks, form-factor
  schema, and a pinmap audit that parses the upstream connector dtsi gpio-map.
- New `tools/build_matrix/run_grove.py` (Grove example x board matrix writer).
- New `tools/pin_map/seed_from_dtsi.py` (seeds board pin_map from upstream dtsi).
- Docs: README.md, README.zh-CN.md, examples/README.md, examples/grove/README.md,
  docs/en/getting-started.md, docs/zh/getting-started.md, tools/build_matrix/README.md.

Reason:
- Board-bound examples (one copy per board) cannot show Zephyr's cross-chip reuse.
  Grove modules are board-agnostic: programming against the upstream
  `seeed_xiao_connector` labels (`xiao_i2c`, `xiao_spi`, `xiao_serial`, `xiao_d`)
  lets one source tree build for every XIAO board. The framework makes that a
  first-class workflow and prepares the data contract for the editor extension's
  interactive pinout.

Result:
- `seeed-zephyr build <board> grove/<module>/<demo>` builds one Grove example on any
  supported board; `show pins <board> <grove-ref> --json` returns per-pin state
  (selectable/reserved/bus/power/incompatible) plus roles and layout; `create --from
  grove/... --board <any>` generates a cross-board project with optional `--pin`
  baked into a per-board overlay.
- Validation status moved from a single field to an example x board matrix in
  `metadata/status/`, generated by `run_grove.py`.
- Each board's `pin_map` records Dn -> chip pin as a provisional baseline derived
  from the upstream connector dtsi, with `pin_map_source` pointing at that dtsi.

Verification:
- `python3 tools/validate_metadata/validate.py` -> 32 passed, 0 failed.
- `python3 tools/build_matrix/run_grove.py --example grove/grove_scd41_co2_temperature_humidity_sensor/basic_read --board xiao_esp32c6 --board xiao_nrf52840 --board xiao_rp2040` -> verified=3, failed=0, pending=7, excluded=1; wrote metadata/status/grove_scd41_basic_read.yaml.
- `seeed-zephyr build xiao_esp32c6|nrf52840|rp2040 grove/grove_scd41_co2_temperature_humidity_sensor/basic_read` -> Build succeeded on all three (single source tree).
- `seeed-zephyr show pins xiao_nrf52840 grove/.../basic_read` -> D4/D5 marked bus (i2c), D6/D7 reserved (console-uart), D0-D3/D8-D10 free, with chip_pin names.
- pinmap audit confirmed it detects the nRF54L15 extra D11-D15 and a bogus D11 entry.

Remaining:
- `pin_map` chip_pin values are upstream-dtsi-derived (form `controller.pin`) and
  pending official Seeed schematic cross-check; `pin_map_source` should be replaced
  with the official Wiki/schematic URL once verified. The pinmap audit currently
  compares Dn index coverage; per-pin chip_pin value comparison is deferred until
  pin_map comes from an independent schematic source.
- Selectable-pin Grove examples (GPIO/analog modules) and `--pin` free selection for
  analog modules are contracted but not yet piloted with a real example.
- nRF54L15 exposes D11-D15 beyond the standard 14-pin XIAO footprint in upstream
  Zephyr; its form-factor variant handling is an open question.

## 2026-07-03 - Add visual Grove pin configurator

Scope:
- Added `seeed-zephyr set-pins <board_id> --app <dir> --pin role=Dn [--json]`.
- Refactored Grove pin overlay baking so `create --pin` and `set-pins` share the
  same `pins/pin.overlay.in` rendering path.
- Added CLI tests for updating a generated Grove project overlay and `snapshot.json`,
  reserved-pin rejection, and fixed-bus rejection.
- Added an interactive VS Code webview panel for XIAO pin configuration:
  `tools/vscode-extension/src/panels/pinConfiguratorPanel.ts` and
  `tools/vscode-extension/src/panels/pinConfiguratorHtml.ts`.
- Added the existing-project entry point `seeedZephyr.configurePins`, surfaced as
  **Configure Pins** in the Projects tree for generated Grove projects.
- Updated the create-project wizard so selectable-pin Grove examples open the pin
  configurator before the project is generated.
- Updated README.md, README.zh-CN.md, docs/en/getting-started.md, and
  docs/zh/getting-started.md.

Reason:
- The CLI could already validate and apply Grove `--pin` selections, but editor users
  had to edit overlay code manually after generation. The extension now exposes a
  CubeMX-style workflow: pick a pin on the XIAO diagram, save, and let the CLI write
  the generated project's per-board overlay.

Result:
- Selectable GPIO Grove examples, such as Grove Ultrasonic, can be configured from the
  editor during project creation and after project creation.
- Saving a pin assignment writes `boards/<target>.overlay` in the generated project
  and updates `snapshot.json.pins`.
- Fixed-bus modules remain read-only in the pin configurator and show their bus pins
  as wiring guidance.

Verification:
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/cli/test_seeed_zephyr.py` -> 89 tests OK.
- `~/zephyrproject/.venv/bin/python tools/validate_metadata/validate.py` -> 35 passed, 0 failed.
- `cd tools/vscode-extension && npm run check-types` -> passed.
- `cd tools/vscode-extension && npm run build` -> passed.

Remaining:
- The first visual configurator version covers selectable GPIO roles only. Analog free
  selection and richer bus parameters remain future work.

## 2026-07-03 - Add project creation sources and blank template

Scope:
- CLI `create` gained `--blank` (with `--from` now optional) to scaffold a minimal
  board-agnostic Zephyr app (`CMakeLists.txt`, `prj.conf`, `src/main.c`, `snapshot.json`)
  from built-in templates.
- Added CLI tests for blank generation, `--from`/`--blank` mutual exclusion, and the
  missing-source error.
- Reworked the extension `createProject` wizard: when launched without a Catalog preset,
  it first asks for a source kind (Grove module example / board example / blank project)
  and routes accordingly.
- Fixed the extension dev-preview launch config so the Extension Development Host opens
  the repository root and builds first (`tools/vscode-extension/.vscode/launch.json`).
- Updated README.md, README.zh-CN.md, docs/en/getting-started.md, docs/zh/getting-started.md.

Reason:
- Creating a Grove project (such as Ultrasonic) from the editor previously required
  finding the inline Catalog button; the top-level Create Project only offered board
  examples. Users also wanted a way to start an empty project. The wizard now exposes all
  three sources from one entry point, and the Catalog keeps its expand-and-create flow.
- The dev preview read a stale default repository clone because the Extension Development
  Host opened no workspace folder, so Grove modules showed no examples.

Result:
- `seeed-zephyr create --blank --board <board> --output <dir>` scaffolds a blank project.
- The editor Create Project entry offers Grove module example, board example, and blank
  project, sharing one parent-folder/name/generate/open tail.
- Pressing Run Extension opens the repository root in the dev host, so the Catalog shows
  the workspace's Grove examples.

Verification:
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/cli/test_seeed_zephyr.py` -> 92 tests OK.
- `python3 tools/cli/seeed_zephyr.py create --blank --board xiao_esp32c6 --output /tmp/... ` -> wrote CMakeLists/prj.conf/src/main.c/snapshot.json.
- `cd tools/vscode-extension && npm run check-types && npm run build` -> passed.

Remaining:
- The blank template is intentionally minimal (printk heartbeat). Scenario templates
  (for example a GPIO or I2C starter) remain future work.

## 2026-07-03 - Match pin configurator to the real XIAO layout

Scope:
- Corrected `metadata/form_factors/xiao.yaml` layout to the real XIAO pad order
  (left: D0-D6; right: 5V, GND, 3V3, D10, D9, D8, D7 with USB-C at top).
- Added board front-render images under `tools/vscode-extension/media/boards/<board_id>.png`
  (resized from the official 2D visual assets).
- The pin configurator now renders the real board image in the center instead of a
  plain rectangle, falling back to the rectangle when an image is missing.
- Threaded `extensionUri` into `PinConfiguratorPanel` (localResourceRoots + asWebviewUri)
  and through the `createProject` and `configurePins` entry points.

Reason:
- The previous diagram mirrored the physical board (power pads and data pads were on
  the wrong sides) and used an abstract rectangle. Matching the official pinout makes
  wiring unambiguous.

Result:
- `show pins` reports left = D0-D6 and right = 5V/GND/3V3/D10-D7, so both the CLI text
  view and the editor pinout follow the real board.
- The configurator shows the actual XIAO board render per board id.

Verification:
- `~/zephyrproject/.venv/bin/python tools/validate_metadata/validate.py` -> 35 passed, 0 failed.
- `seeed-zephyr show pins xiao_samd21 grove/.../basic_read --json` -> left/right match the board.
- `cd tools/vscode-extension && npm run check-types && npm run build` -> passed.

## 2026-07-03 - Align pin rows to the board image pads

Scope:
- Added `tools/vscode-extension/media/boards/pads.json` with each board's pad band
  (top/bottom fractions of the image height), measured from the board images.
- Reworked the pin configurator into an overlay layout: the board image sits in the
  center with two absolutely-positioned pin rails whose seven rows are distributed
  across the measured pad band, so each row lines up with its physical pad. A dashed
  lead line connects each row toward the board.
- Kept a two-column fallback for when a board image or pad band is unavailable.
- The panel now loads the pad band for the board and passes it to the renderer.

Reason:
- The rows previously sat in plain side columns that did not line up with the pads on
  the board image. Distributing rows across the measured pad band makes the diagram
  read like the official XIAO pinout.

Result:
- For boards with an image and pad band, the seven pin rows align vertically with the
  board's seven pads on each side.

Verification:
- `cd tools/vscode-extension && npm run check-types && npm run build` -> passed.
- Pad bands derived from the bundled board images (top ~0.20, bottom ~0.86).

## 2026-07-03 - Fix baked pin overlay wiping the SAMD21 USB console

Scope:
- `bake_pin_overlay` now merges the selected pin into the overlay Zephyr actually
  applies: when `boards/<target>.overlay` exists it appends a marked pin block there
  (preserving a board console), otherwise it writes `app.overlay`. Re-baking is
  idempotent via the marker block.
- Ultrasonic example: `boards/seeeduino_xiao.overlay` now carries the USB CDC console
  only (no duplicate pin), and `boards/seeeduino_xiao.conf` adds `CONFIG_SERIAL=y`.
- Added CLI tests for the app.overlay path (nRF52840, no board overlay) and the
  board-overlay merge path (SAMD21, console preserved, idempotent re-bake).

Reason:
- On XIAO SAMD21 the serial port is USB CDC ACM provided by the firmware. Baking the
  pin previously overwrote `boards/seeeduino_xiao.overlay`, deleting the CDC console
  node, so after upload the board enumerated as USB with no CDC function and the serial
  port disappeared. Zephyr also ignores `app.overlay` when a board overlay exists, so
  baking into `app.overlay` did not apply the pin on such boards. The bootloader was
  never affected.

Result:
- Generated SAMD21 Grove projects keep the USB CDC console and gain the selected pin, so
  the serial port is present after flashing. Boards without a board overlay keep using
  `app.overlay` for the pin.

Verification:
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/cli/test_seeed_zephyr.py` -> 93 tests OK.
- `seeed-zephyr build xiao_samd21 grove/.../basic_read` and a generated project build ->
  `.config` has CONFIG_USB_CDC_ACM=y, CONFIG_SERIAL=y, zephyr,console = &cdc_acm_uart0.
- `~/zephyrproject/.venv/bin/python tools/validate_metadata/validate.py` -> 35 passed.

## 2026-07-03 - Reconnecting serial monitor for non-Espressif boards

Scope:
- Added `tools/cli/serial_monitor.py`, a pyserial-based monitor that waits and
  reconnects when the device drops off the USB bus, exiting only on Ctrl+].
- Routed `run_monitor` and interactive `cmd_monitor` (non-Espressif path) through it
  instead of `python -m serial.tools.miniterm`.
- Added the helper to the package force-include so installed CLIs ship it.
- Updated docs/en/getting-started.md and docs/zh/getting-started.md.

Reason:
- miniterm exits the moment the serial device disappears. On USB-CDC boards a reset or
  replug drops the port, which ended the monitor. It should stay open and reconnect.

Result:
- The monitor streams output, forwards stdin, and on disconnect prints a waiting notice
  and reconnects to the same port automatically. Ctrl+] quits and restores the terminal.

Verification:
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/cli/test_seeed_zephyr.py` -> 93 tests OK.
- pty-based check: the monitor streamed device bytes to stdout and, when the pty master
  closed (simulated disconnect), returned into its reconnect wait without hanging.

## 2026-07-03 - Fix Grove Ultrasonic echo always reading zero

Scope:
- Reworked `read_distance` in the Grove Ultrasonic example to mirror the Seeed
  Arduino `pulseIn` sequence: after the trigger, switch the shared SIG pin to
  `GPIO_INPUT | GPIO_PULL_DOWN`, wait for the line to settle LOW, then time the echo
  from its rising edge to its falling edge.
- Changed the distance formula to the Seeed ranger value (echo_us * 10 / 58 mm).

Reason:
- The old code went straight to "wait for HIGH", so the transient/floating HIGH on the
  pin right after releasing the trigger was mistaken for the echo start; the next read
  was LOW, giving a zero-width echo (Distance 0.0 cm, Echo 0 us) on every sample. The
  official pulseIn first waits for the line to settle before timing the pulse.

Result:
- The echo is measured from the real rising edge, so a connected Grove Ultrasonic Ranger
  reports live distances; a missing echo now yields a timeout rather than a false zero.

Verification:
- `seeed-zephyr build xiao_samd21 grove/grove_ultrasonic_distance_sensor/basic_read` ->
  Build succeeded. Hardware read-back pending user confirmation.
- Reference: Seeed_Arduino_UltrasonicRanger Ultrasonic.cpp (pulseIn, /29/2 cm).

## 2026-07-03 - Keep created/opened projects in the current window

Scope:
- `createProject` and `openGenerated` now add the project to the current window via
  `updateWorkspaceFolders` and drop the "Open in New Window" / "Open in This Window"
  prompt buttons.

Reason:
- Creating or opening a project kept offering "Open in New Window", which spawned a
  separate OS window and left the previous tabs behind. The desired PlatformIO-style
  behavior is to surface the project in the current window without a new window.

Result:
- Both actions add the folder in place (no new OS window, no reload for a window that
  already has a folder) and show a short "Added <name> to this window." notice.

Verification:
- `cd tools/vscode-extension && npm run check-types && npm run build` -> passed.
- `rg "Open in New Window|openFolder" dist/extension.js` -> no matches remain.

## 2026-07-03 - Prefer the repo CLI in a checkout and bump versions for release

Scope:
- `cliLocator` now prefers the repository's own CLI (scripts/seeed-zephyr) when the
  repository is the open workspace, so contributor edits to the CLI take effect instead
  of a separately installed/managed CLI selected in settings.
- Bumped versions for release: CLI 0.3.2 -> 0.4.0, extension 0.2.1 -> 0.3.0, and the
  extension's DEFAULT_MANAGED_CLI_VERSION to 0.4.0.

Reason:
- Creating projects through the editor kept invoking the previously installed managed
  CLI (older bake logic that wiped the SAMD21 USB console overlay), because the settings
  cliPath override won over the repo CLI. When the repo itself is the open workspace, the
  repo CLI is the intended source of truth.

Result:
- In a repository checkout opened as the workspace, all editor CLI actions run the repo's
  CLI. The version bump lets installed CLI/extension consumers pull the fixed release.

Verification:
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/cli/test_seeed_zephyr.py` -> 93 tests OK.
- `cd tools/vscode-extension && npm run check-types && npm run build` -> passed (0.3.0).
