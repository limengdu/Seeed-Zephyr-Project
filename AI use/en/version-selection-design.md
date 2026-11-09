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
seeed-zephyr use v1.1.0               makes that pair the active one
seeed-zephyr build <board> --app .    picks the workspace from the project snapshot
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

## 6. Directory layout

Zephyr workspaces sit side by side and share one SDK:

```text
~/zephyrproject/v4.4.0/      a complete west workspace
~/zephyrproject/v4.5.0/      another complete west workspace
~/zephyr-sdk-1.0.1/          shared; no reinstall while the SDK major matches
```

Repository checkouts sit side by side too:

```text
~/.seeed-zephyr/versions/v1.0.0/    full checkout of that tag
~/.seeed-zephyr/versions/v1.1.0/
~/.seeed-zephyr/current              points at the active checkout
```

Side-by-side storage replaces in-place switching because an in-place switch
removes the workspace an older project was built against. With both present,
every generated project can return to the pair it was created with.

Each Zephyr workspace costs multiple gigabytes, and west blobs are duplicated
per workspace. The maintained default is the latest version plus the previous
one; older versions are installed on request.

## 7. Workspace selection at build time

`seeed-zephyr build <board> --app <dir>` selects in this order:

1. Read `snapshot.json` in the directory and take `zephyr_version`.
2. When that version's workspace is installed, build with it.
3. A directory without `snapshot.json` (an example inside the repository, a
   hand-written project) uses the currently selected pair.
4. When the workspace is not installed, print the install command and stop
   instead of downloading gigabytes unprompted.
5. The `ZEPHYR_WORKSPACE` environment variable still wins, so the build matrix
   and investigations keep their override.

Mismatch notice: when the directory's `zephyr_version` differs from the
workspace actually used, print one line naming both versions before building.
The build continues after the notice, because investigations deliberately
build mismatched combinations.

`info` gains two lines: the path of the Zephyr workspace in use, and that
workspace's actual version. Both come from disk, not from the code constant.

## 8. Relationship to existing mechanisms

- `update --version` stays, and its meaning becomes "switch the active pair".
  Internally it takes the same path as `use`, so there is one implementation.
- The in-place migration in the setup scripts (`sync_manifest_revision`) runs
  once, for a workspace that has no version subdirectory yet: it moves the
  existing `~/zephyrproject` into `~/zephyrproject/v4.4.0/`. After that, version
  directories never move each other. The signal is whether `.west` already
  exists in the directory.
- In package mode (pip, pipx, Homebrew) the examples and metadata travel with
  the package version. `versions` and `use` operate on the side-by-side
  checkouts and leave the installed package untouched. Homebrew installs still
  cannot roll the package back through the package manager.
- The VS Code extension reads metadata directly and filters out `unsupported`.
  Its change is to drive version selection through the same CLI commands and to
  show the active pair in the environment view. That step follows once the CLI
  commands are stable.

## 9. Phases

Phase 1, so an existing project finds its own workspace:

1. Workspaces move to per-version subdirectories, with the setup scripts
   performing the one-time migration.
2. `build --app` selects the workspace from `snapshot.json` and prints the
   mismatch notice.
3. `info` prints the real workspace path and version.

Phase 1 adds no command and needs no git tag. It is verifiable on its own: a
project generated under v4.4.0 still builds against v4.4.0 when both workspaces
exist on the machine.

Phase 2, so users can choose a version:

1. Cut the first repository tag for the current baseline and add the mapping
   file.
2. Implement `versions`, `install`, `use`, and the side-by-side checkouts.
3. Update the getting-started docs to explain pairs and disk use.
4. Point the extension at the same commands.

## 10. Verification

- Unit tests cover: workspace chosen from a snapshot, current pair used when
  there is no snapshot, the install command printed when a workspace is
  missing, the environment variable override, and the one-time migration
  leaving an already migrated workspace in place.
- One real build: with v4.4.0 and v4.5.0 workspaces coexisting, build the
  RP2350 example against each and confirm the console node comes from that
  version's board file.
- Docs and command help stay in step: the new commands appear in
  `seeed-zephyr --help` and in the getting-started guide.

## 11. Out of scope

- Example content and board coverage stay as they are. nRF54LM20A, nRF54LM20B,
  and STM32C5 continue on their own plans.
- No new third-party dependency. Version switching uses git and west.
- No automatic cleanup of old workspaces. Removing multi-gigabyte directories
  stays an explicit user action.
