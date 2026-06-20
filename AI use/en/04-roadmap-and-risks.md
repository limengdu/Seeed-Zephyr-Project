# Roadmap And Quality Controls

## 1. Roadmap Overview

The roadmap has three phases:

```text
Phase 1: Examples, Projects, Metadata, And Validation Base
Phase 2: CLI For Discovery, Build, Validation, And Generation
Phase 3: VS Code Product Experience
```

Each phase must preserve the same product center: verified XIAO + Grove Zephyr
examples and projects.

One-sentence summary: the roadmap starts with content users can run, then adds
tools around that content.

## 2. Phase 1 Roadmap

Main work:

- create the first `examples/boards/` assets
- create the first `examples/grove/` assets
- create the first `examples/expansion_boards/` assets
- create the first complete `projects/`
- define metadata for examples and projects
- validate board/module metadata
- build examples from the repository root
- record build-only and hardware-tested evidence
- define contribution requirements

Gate to Phase 2:

- repository-owned examples exist
- at least one example builds through project tooling
- metadata validation passes
- build matrix covers first examples
- contribution shape is documented

One-sentence summary: Phase 1 earns Phase 2 by proving the repository is already
useful without a generator.

## 3. Phase 2 Roadmap

Main work:

- implement CLI skeleton
- list boards, modules, capabilities, examples, and projects
- build repository examples and projects
- validate contribution structure
- copy/create projects from known examples
- support generated project snapshots
- let CI call the same commands

Gate to Phase 3:

- CLI can operate real examples/projects
- generated projects come from known assets
- errors are specific and actionable
- CI can validate examples and projects

One-sentence summary: Phase 2 earns Phase 3 by making the catalog operable.

## 4. Phase 3 Roadmap

Main work:

- build VS Code extension skeleton
- browse examples and projects
- filter by board, Grove module, capability, and status
- preview wiring and validation evidence
- create projects through the CLI
- hand off build/flash/monitor/debug to official Zephyr tooling
- expose contribution checks

Gate to public beta:

- early users can find an example and run it
- generated/copied projects build through official tooling
- wiring diagrams are verified
- contribution checks are usable
- users complete a first XIAO + Grove Zephyr project without engineer hand-holding

One-sentence summary: Phase 3 succeeds when the UI makes the verified catalog
easier to use.

## 5. Quality Controls

### Control: Current Project Context

Because much work may be done by AI agents, future work needs a compact,
current, project-level brief before implementation.

Required practice:

- keep all AI-facing strategy under `AI use/`
- require `AI use/README.md` and `AI use/WORKLOG.md`
- write every phase around examples, projects, validation, and contributions
- record meaningful work in a factual work log

One-sentence summary: AI work should start from the project brief and leave a
clear handoff trail.

### Control: Setup-To-Content Path

Setup scripts prepare users for repository content.

Required practice:

- setup scripts must end by pointing to repository examples/projects
- getting-started docs must explain what to build from this repository
- success metrics must count examples and projects

One-sentence summary: setup is the doorway into repository examples and projects.

### Control: Content-Backed Metadata

Metadata is strongest when it leads to real examples or projects.

Required practice:

- each metadata expansion should be paired with an example plan
- Phase 1 success requires repository-owned examples
- build matrix should move from generic upstream samples to repository examples

One-sentence summary: metadata earns value by helping users reach usable content.

### Control: Verified Community Examples

Community examples increase value when they are structured and evidence-backed.

Required practice:

- define contribution requirements
- accept build-only status honestly
- promote to hardware-tested only with evidence
- require expected output and hardware notes

One-sentence summary: community content must be welcomed and verified.

### Control: Evidence-Driven Zephyr Support

XIAO chips have varied Zephyr support for wireless, low power, and advanced
peripherals.

Required practice:

- keep status honest
- compare selected cases against vendor SDKs
- document vendor SDK routes where better
- mark limitations clearly

One-sentence summary: Zephyr-first remains evidence-driven.

## 6. Metrics

Content metrics:

- number of board examples
- number of Grove examples
- number of expansion-board examples
- number of complete projects
- number of community contributions accepted

Evidence metrics:

- number of build-only examples
- number of hardware-tested examples
- number of hardware-tested projects
- number of documented known issues

Tooling metrics:

- examples buildable from repository root
- generated projects build successfully
- contribution validation catches structural errors
- users find and run a first example faster than manual Zephyr search

One-sentence summary: measure content usefulness first, tooling second.

## 7. Recommended Initial Scope

Initial examples:

- `xiao_esp32c3/hello_world`
- `xiao_esp32c6/blinky`
- `xiao_esp32c6/i2c_scan`
- one Grove sensor `basic_read`
- one expansion-board display or button example

Initial projects:

- one XIAO + Grove sensor-to-serial project
- one XIAO + display project
- one wireless or BLE project after board support is proven

One-sentence summary: start with a small catalog that users can actually run.
