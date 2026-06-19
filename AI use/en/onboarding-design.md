# Onboarding and Distribution Design

This document defines how external users install and use Seeed Zephyr Base. The
audience is every XIAO product user across macOS, Windows, and Linux, many of
whom are not embedded experts. The design goal is to reduce onboarding to the
fewest, fastest, most reliable steps possible, and to absorb setup complexity
into the project rather than expose it to each user.

## 1. The Friction Being Removed

A from-scratch manual setup (recorded in `validation-log.md`) exposes three
frictions that external users would otherwise hit:

- **Scattered steps.** Ten-plus commands across Homebrew, a Python venv, `west`,
  workspace init and update, and SDK install.
- **Large footprint.** A full `west update` fetches every vendor HAL, about
  5.4 GB, most of it unused by any single XIAO board.
- **Version coordination.** The Zephyr release, Python, SDK, and module
  revisions must all line up. A single missed venv activation already caused a
  failed first attempt during validation.

One-sentence summary: the manual path is long, heavy, and version-sensitive, and
every one of those costs should be paid by the project, not the user.

## 2. Design Principles

- **Absorb complexity once, centrally.** Version and dependency decisions are
  made and tested by the project, never re-derived by each user.
- **Simplest viable path per platform.** Cover macOS, Windows, and Linux; prefer
  one command over many.
- **Built on evidence.** Every automated path is frozen from a manually verified
  run, not assumed. Verification lives in `validation-log.md`.

One-sentence summary: pay the setup cost once at the center, on real evidence, so
users pay almost nothing.

## 3. Layered Onboarding Model

Onboarding is designed in four layers, each removing more friction than the last.

| Layer | What it is | Friction removed | User action |
| --- | --- | --- | --- |
| L1 | One-command setup script (per platform) | scattered steps | run one script |
| L2 | Project `west.yml` manifest | large footprint, version coordination | `west init -m <repo>` + `west update` |
| L3 | Container image (optional) | full local install | `docker run` / open dev container |
| L4 | VS Code plugin (Phase 2/3) | commands entirely | select and click in the IDE |

- **L1 — One-command setup script.** Per-platform scripts (shell for macOS and
  Linux, PowerShell or WSL2 for Windows) detect existing tools, install build
  dependencies and the SDK, and configure mirrors. Removes the scattered-steps
  friction.
- **L2 — Project west manifest.** The repository ships a `west.yml` (not yet
  present). Users run `west init -m <this repo>` then `west update` to fetch a
  pinned Zephyr, this project, and only the modules XIAO boards need. This is the
  primary, intended way to consume the project.
- **L3 — Container image (optional).** A prebuilt Docker / Dev Container with the
  toolchain preinstalled, for users who want zero local install or for CI.
  Flashing physical boards from a container is limited by USB passthrough, so
  this targets build and CI, not on-device debugging.
- **L4 — VS Code plugin.** The Phase 2/3 end state: board, module, and scenario
  selection in the IDE, with environment, generation, build, and flash handed off
  behind the UI. Users issue no commands at all.

One-sentence summary: the same product is reachable by a script, by a manifest,
by a container, or by clicks, with each layer hiding more of the machinery.

## 4. Version Management

The complexity of version coordination is carried once by the project, not by
each user. The `west.yml` manifest acts as a lockfile: it pins the Zephyr
revision and the exact commit of every module. The project maintains this single
file, tests the combination, and publishes it; every user's `west update`
reproduces the same tested set. Upgrading Zephyr is a project action — edit the
manifest, re-validate, release — after which users simply move forward with a
plain `west update`.

This mirrors the metadata model in `01-phase-one-zephyr-base.md`: the
authored `version_policy` (`latest_stable`) declares intent, and the derived
`validated_zephyr_version` records the exact release CI proved. The manifest is
the mechanism that makes that pinned version real on every user's machine.

One-sentence summary: a single project-maintained lockfile gives every user the
exact version set the project tested, with no version decisions of their own.

## 5. Footprint and Speed Reduction

- **Module scope.** The manifest imports upstream Zephyr with a name-allowlist so
  only XIAO-relevant HALs are fetched, cutting the ~5.4 GB baseline substantially.
- **SDK scope.** Install only the toolchain architectures XIAO uses (Xtensa,
  RISC-V, Arm) instead of the full set.
- **Mirrors.** Setup scripts offer regional mirrors for GitHub, pip, and the
  Zephyr SDK to shorten first-time downloads.

One-sentence summary: fetch only what XIAO needs, and fetch it from the fastest
available source.

## 6. Target User Experience

```text
Today (manual, validation phase):
  ten-plus steps, ~5.4 GB, user tracks versions          <- high barrier

L1 + L2 (scripted + manifest):
  1) run one setup script
  2) west init -m <this repo> && west update             <- two commands, versions pinned

L4 (plugin):
  select board, module, scenario, then click             <- no commands
```

One-sentence summary: the target is two commands for command-line users and zero
for plugin users.

## 7. Implementation Path

1. **Verify manually on macOS first.** Record real commands, timings, and
   pitfalls in `validation-log.md`. (in progress)
2. **Freeze the verified steps** into a macOS setup script, the project
   `west.yml`, and step-by-step docs (English and Simplified Chinese).
3. **Reproduce for Windows (WSL2) and Linux.** Mark each platform as unverified
   until tested on that platform or in CI.

Not yet present, tracked for implementation:

- `// TODO(manifest): add west.yml exposing this repo as the manifest repository`
- `// TODO(scripts): add per-platform setup scripts (macOS, Linux, Windows/WSL2)`
- `// TODO(samples): add baseline samples so the manifest has buildable targets`
- `// TODO(shields): add boards/shields for expansion boards`
- `// TODO(container): evaluate a Docker / dev container image for build and CI`

One-sentence summary: validate on macOS, freeze into script plus manifest plus
docs, then extend to the other platforms with honest verification status.

## 8. Open Questions

- **Windows baseline.** WSL2 (reuses the Linux path) versus native Windows
  support.
- **Manifest topology.** Confirm this repository as the manifest (T2 "star")
  repository that imports upstream Zephyr.
- **Mirror selection.** Which regional mirrors to default to, and how to let
  users opt in or out.

One-sentence summary: platform baseline, manifest topology, and mirror defaults
remain to be decided before the scripts and manifest are finalized.
