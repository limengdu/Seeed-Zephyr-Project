# Version Selection Design

Status: design draft, pending review. This file describes a proposal and does
not describe implemented behavior.

## 1. Problem

Users want the CLI to work the way ESP-IDF does: pick a version and use the
examples that match it, instead of always following the newest state of the
repository.

A version in this repository is a pair:

```text
repository version (examples, metadata, CLI code) + the Zephyr version it pins
```

Both sides move together. Switching only one side produces builds that succeed
while the hardware behavior breaks.

## 2. Why the pair is required

Zephyr v4.5.0 rewrites the board target `xiao_rp2350/rp2350a/m33` to
`xiao_rp2350/rp2350a/m33_0` before it looks up board files. An older repository
checkout ships files named `xiao_rp2350_rp2350a_m33.*`, which the newer Zephyr
never applies, so the console falls back to `&uart0`. USB serial and the UF2
auto-entry stop working, and the build reports success.

That fact sets the baseline for this design: a successful build is not evidence
that a version combination is correct. The CLI reports whether the combination
is paired before it builds.

## 3. Current state

Foundations already in place:

- `seeed-zephyr update --version <version>` switches the repository checkout in
  repo mode. Candidates are tried as given, then `v<version>`, then
  `seeed-zephyr-<version>`, and the working tree must be clean.
- `snapshot.json` written by `create` carries a `zephyr_version` field taken
  from the `ZEPHYR_BASELINE` constant.
- `seeed-zephyr info` prints the baseline the CLI code believes it targets.

Gaps:

| Point | Today |
| --- | --- |
| Zephyr workspace | One `~/zephyrproject` per machine; the setup scripts move it in place to the version they pin |
| Version check | `build --app` never reads `snapshot.json` and never compares the installed Zephyr version |
| Baseline report | `info` prints the constant in the code, not the Zephyr version on disk |
| Release markers | The repository has no git tags, so `--version` has no published version to select |
| Mapping | No data file records which repository version pairs with which Zephyr version |
| Editor extension | Versions the CLI itself and knows nothing about the Zephyr workspace version |

## 4. Target experience

```text
seeed-zephyr versions                 lists version pairs and what is installed
seeed-zephyr install v1.1.0           installs that pair (repo checkout + matching Zephyr)
seeed-zephyr use v1.1.0               switches to that pair; about 10 s offline once installed
seeed-zephyr build <board> --app .    checks the project snapshot and stops on a mismatch
```

The `versions` output answers three questions at a glance: which pairs exist,
which Zephyr each one uses, and which ones are installed locally.

## 5. Version mapping

A new data file, for example `metadata/versions.yaml`, holds one row per pair:

```yaml
versions:
  - id: v1.1.0
    zephyr: v4.5.0
    sdk: "1.0.1"
  - id: v1.0.0
    zephyr: v4.4.0
    sdk: "1.0.1"
```

Conventions:

- `id` is a git tag of this repository and the name users type in commands.
- One repository tag maps to exactly one Zephyr version. Moving the Zephyr pin
  means cutting a new tag.
- The file is versioned with the repository. An older tag's mapping cannot know
  about newer releases, so the list of selectable versions comes from the
  remote tag list, and each tag's own file supplies its mapping.
- The metadata validator requires the repository's `ZEPHYR_BASELINE` constant to
  match the `zephyr` value of the newest row.

## 6. Storage: one workspace, several stored versions

The machine keeps a single Zephyr workspace, `~/zephyrproject`. Versions
coexist as stored git objects inside that workspace, and exactly one version's
source files are checked out at any time. Switching versions checks out a
different stored version locally.

All three mechanisms are built into west, so no new dependency is needed:

| Mechanism | Effect | Setting |
| --- | --- | --- |
| Module filter | Fetches only the modules this repository's boards use | `manifest.project-filter` |
| Offline switch | Checks out another stored version from local objects | `west update -n` |
| Blob cache | Caches blobs by sha256 and copies them locally on switch | `blobs.auto-cache` |

Modules kept by the filter: Zephyr itself plus cmsis, cmsis_6, hal_atmel,
hal_espressif, hal_nordic, hal_renesas, hal_rpi_pico, hal_silabs, mbedtls,
mcuboot, picolibc, segger, tf-psa-crypto, and zcbor. The list is derived from
board metadata and grows with new boards (hal_stm32 joins with STM32C5).

Each installed version keeps a local ref `refs/seeed/<version>` in every
module, so git garbage collection retains stored versions that are not checked
out.

The SDK stays shared at `~/zephyr-sdk-<version>`; pairs with the same `sdk`
value in the mapping reuse it. The Python environment (`.venv`) is shared too,
and setup installs the union of the requirement files of all installed
versions.

## 7. Measurements

Measured on 2026-11-09 in an isolated workspace, with v4.4.0 and v4.5.0 stored
side by side and repository content taken from the commits before and after the
baseline move:

| Item | Result |
| --- | --- |
| Full workspace (68 modules, the user's current one) | 6.3 GB |
| Filtered, one version | 2.2 GB |
| Stored objects: one / two versions | 228 MB / 261 MB, 244 MB after gc |
| Blob cache: two versions | 184 MB |
| First install of a second version | sources 8 s + modules 36 s + blobs 274 s |
| Switch between installed versions, no cache | sources ~10 s + blobs ~280 s |
| Switch between installed versions, with cache | sources ~10 s + blobs 0-1 s, fully offline |
| v4.4.0 build matrix | 10 pass, 1 unsupported, matching the v4.4.0-era record |
| v4.5.0 build matrix after a switch | 11 pass |
| RP2350 console, each version with its own repository | `&cdc_acm_uart0` for both |
| Stored versions after git gc | all retained |

Result: each extra stored version costs about 0.1-0.2 GB, and switching between
installed versions takes about 10 s with no network access.

## 8. Version check at build time

`seeed-zephyr build <board> --app <dir>` decides as follows:

1. Read `snapshot.json` in the directory and take `zephyr_version`.
2. When it matches the version checked out in the workspace, build.
3. When it differs and that version is installed, print both versions plus
   `seeed-zephyr use <version>`, then stop.
4. When it differs and that version is not installed, print
   `seeed-zephyr install <version>`, then stop.
5. A directory without `snapshot.json` (an example inside the repository, a
   hand-written project) builds against the current version.
6. `--allow-mismatch` skips the check for deliberate mismatched builds.
7. The `ZEPHYR_WORKSPACE` environment variable still wins, for the build matrix.

The build stops on a mismatch because the RP2350 case shows a mismatched pair
builds cleanly and fails on hardware. A switch takes about 10 s, so asking the
user to confirm costs little.

`info` gains two lines: the workspace path and the version checked out in it.
Both are read from disk (Zephyr's `VERSION` file), not from the code constant.

## 9. Relationship to existing mechanisms

- `use <version>` does three things in order: checks the repository out at
  that tag, moves Zephyr to the mapped version, and restores blobs from the
  cache. `update --version` stays and takes the same path.
- The existing `sync_manifest_revision` in the setup scripts is the first form
  of the Zephyr switch step and is extended with two steps: writing the local
  ref and restoring blobs from the cache.
- The user's existing `~/zephyrproject` is upgraded in place without moving:
  setup writes the module filter and cache settings and anchors the current
  version. Module directories outside the filter (about 4 GB) become inactive
  in west; setup lists them and moves them to the trash after the user
  confirms.
- In package mode (pip, pipx, Homebrew) examples and metadata travel with the
  package version, and `use` switches the Zephyr workspace and the active pair
  record. Homebrew installs still cannot roll the package back through the
  package manager.
- The VS Code extension follows once the CLI commands are stable: its version
  picker calls the same commands, and the environment view shows the active
  pair.

## 10. Phases

Phase 1, storage and version check (no new command):

1. Setup writes the module filter and blob cache settings and upgrades the
   existing workspace in place.
2. `build --app` checks the version from `snapshot.json` and stops with a
   command on a mismatch.
3. `info` prints the version checked out in the workspace.

Phase 2, user version selection:

1. Cut the first repository tag for the current baseline and add the mapping
   file.
2. Implement `versions`, `install`, and `use`.
3. Update the getting-started docs to explain pairs, disk use, and switching.
4. Point the extension at the same commands.

## 11. Verification

- Unit tests cover: matching versions build, an installed mismatch suggests
  `use`, a missing version suggests `install`, no snapshot builds against the
  current version, `--allow-mismatch` proceeds, and the environment variable
  wins.
- Switch script test: switch back and forth between two versions, every blob
  verifies after each switch, and both stored versions survive git gc.
- Real builds: each version with its own repository passes the build matrix,
  and the RP2350 console lands on USB.
- Still open: whether flash tools work across versions with the shared Python
  environment; only builds are verified so far.

## 12. Out of scope

- Example content and board coverage stay as they are. nRF54LM20A, nRF54LM20B,
  and STM32C5 continue on their own plans.
- No new third-party dependency. Switching uses only git and built-in west
  features.
- Installed versions and caches are never deleted automatically. Freeing disk
  space stays an explicit user action.
