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
