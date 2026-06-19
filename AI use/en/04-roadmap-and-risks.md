# Roadmap And Risks

## 1. Roadmap Overview

The recommended roadmap has three major phases:

```text
Phase 1: Zephyr Base
Phase 2: CLI Generator
Phase 3: VS Code Plugin
```

Each phase should create reusable assets for the next phase.

One-sentence summary: build the foundation first, then the generator, then the product interface.

## 2. Phase 1 Roadmap

### Duration

Recommended duration:

```text
8 to 12 weeks
```

### Main Work

- define metadata schema
- add representative XIAO board metadata
- add representative Grove metadata
- add expansion-board metadata
- add baseline samples
- configure CI build validation
- run selected hardware-in-loop tests
- compare selected Zephyr behavior with vendor SDKs

### Deliverables

- board metadata
- Grove metadata
- expansion-board metadata
- baseline samples
- compatibility matrix
- CI build workflow
- hardware validation report
- Zephyr version recommendation

### Gate To Phase 2

Move to Phase 2 only if:

- representative XIAO boards can build baseline samples
- high-frequency Grove modules can be described consistently
- generated or manual matrix data is trustworthy
- hardware validation shows enough real-world value

One-sentence summary: Phase 1 earns the right to build tools by proving the foundation is real.

## 3. Phase 2 Roadmap

### Duration

Recommended duration:

```text
8 to 10 weeks
```

### Main Work

- implement CLI skeleton
- implement list, check, generate, verify, build commands
- support west project output
- support initial templates
- generate README and wiring assets
- include project metadata snapshot
- add generated-project CI tests
- add PlatformIO output after west is stable

### Deliverables

- CLI package
- project generator
- west templates
- initial PlatformIO templates
- generated project examples
- CLI test suite
- build verification for generated projects

### Gate To Phase 3

Move to Phase 3 only if:

- generated projects are deterministic
- generated projects build reliably
- CLI errors are clear
- metadata and templates can support a graphical interface

One-sentence summary: Phase 2 earns the right to build a plugin by proving project generation is reliable.

## 4. Phase 3 Roadmap

### Duration

Recommended MVP duration:

```text
10 to 16 weeks
```

### Main Work

- create VS Code extension skeleton
- build Webview configurator
- load hardware catalog
- show compatibility results
- render wiring diagrams
- implement settings panel
- call CLI to generate projects
- integrate one-click handoff to the official Zephyr extension for build and flash
- add XIAO and Grove specific error hints

### Deliverables

- VS Code plugin MVP
- hardware selection UI
- Grove selection UI
- expansion-board selection UI
- wiring diagram view
- project generation flow
- one-click handoff to the official Zephyr extension's build and flash
- XIAO and Grove error hints
- early user testing report

### Gate To Public Beta

Move to public beta only if:

- the plugin works on at least macOS and Windows, or a clearly defined first OS
- generated projects build locally through the official Zephyr extension
- wiring diagrams are verified
- the handoff to the official extension works on a clean setup
- XIAO and Grove specific mistakes produce clear hints
- early testers can finish a project without engineer hand-holding

One-sentence summary: Phase 3 succeeds when the product workflow works for real users, not only internal engineers.

## 5. Technical Risks

### Risk: Zephyr Support Is Uneven Across Chips

Some chips may have strong Zephyr support. Others may depend heavily on vendor SDKs for advanced wireless, low power, or peripheral features.

Mitigation:

- keep status honest
- compare selected features against vendor SDKs
- use Zephyr-first, not Zephyr-only
- keep vendor SDK routes documented

One-sentence summary: do not assume Zephyr is equally strong on every chip.

### Risk: Low-Power Performance Is Not Good Enough

Low-power behavior often depends on chip-specific SDK details.

Mitigation:

- measure current, sleep, and wake behavior on representative boards
- clearly mark low-power templates as tested or experimental
- recommend vendor SDK where Zephyr is not competitive

One-sentence summary: power claims must be measured, not assumed.

### Risk: Metadata Becomes Incorrect

Incorrect metadata can generate wrong wiring, wrong overlays, or wrong configurations.

Mitigation:

- validate metadata schema
- require review for metadata changes
- connect metadata to CI builds
- connect selected metadata to hardware tests
- include generated project snapshots

One-sentence summary: metadata is the product's truth source, so it must be tested like code.

### Risk: CLI And Plugin Logic Diverge

If the plugin reimplements generation logic, bugs will multiply.

Mitigation:

- keep generation in the CLI
- let the plugin call the CLI
- share metadata and validation rules

One-sentence summary: one generator should serve every interface.

### Risk: The Plugin Scope Expands Too Fast

Trying to build CubeMX, Wokwi, PlatformIO, and an AI assistant all at once will delay real validation.

Mitigation:

- define a small MVP
- avoid full simulation in the first version
- support west before PlatformIO
- limit initial boards and modules

One-sentence summary: a smaller complete workflow is better than a large unfinished platform.

## 6. Business Risks

### Risk: Users Do Not Want Zephyr

Many beginner users may prefer Arduino, MicroPython, or CircuitPython.

Mitigation:

- hide Zephyr complexity behind generated projects
- keep Arduino support where it is valuable
- target professional and semi-professional users first
- measure actual adoption

One-sentence summary: users should not be forced to learn Zephyr before receiving value.

### Risk: The Project Does Not Reduce Internal Cost

If the system adds more maintenance work than it removes, it loses business value.

Mitigation:

- track repeated documentation work reduced by metadata
- track issue categories before and after plugin release
- use CI and generated docs to reduce manual work

One-sentence summary: the project must reduce repeated work, not create a new maintenance burden.

### Risk: It Duplicates Existing Tools Poorly

Users already have Zephyr, the official Zephyr VS Code extension, vendor extensions such as nRF Connect, PlatformIO, and other vendor tools. These already provide build, flash, monitor, debug, and environment setup, and they are mature.

The decision for this project is therefore explicit: do not reimplement the toolchain. Phase 3 owns only the unique pre-build value, hardware selection, compatibility, wiring, configuration, and generation, and hands off to the official extension for build and flash.

Mitigation:

- focus on XIAO + Grove product experience
- do not attempt to replace general-purpose embedded tools or the official Zephyr toolchain extensions
- integrate with existing tools instead of fighting them, and depend on the official Zephyr extension for build and flash

One-sentence summary: the project's unique value is Seeed hardware composition, so it builds on the official toolchain instead of rebuilding it.

## 7. Suggested Metrics

### Foundation Metrics

- number of XIAO boards with metadata
- number of Grove modules with metadata
- number of expansion boards with metadata
- number of CI-tested examples
- number of hardware-tested combinations
- number of known issues documented

### Generator Metrics

- number of templates
- generated project build success rate
- average generation time
- percentage of generated projects with README and wiring output
- number of reproducible bug reports using metadata snapshots

### Plugin Metrics

- first project completion time
- build success rate after generation, measured in the official Zephyr extension
- handoff success rate from generation to a started build
- number of users who complete build, flash, and monitor through the official extension
- number of support issues reduced

One-sentence summary: measure whether the system improves real workflows, not just whether more files exist.

## 8. Recommended Initial Scope

Initial boards:

- XIAO ESP32C6
- XIAO ESP32S3
- XIAO nRF54L15
- XIAO MG24
- XIAO RP2350 or XIAO RA4M1

Initial Grove modules:

- Grove SHT40
- Grove Button
- Grove Relay
- Grove Light Sensor
- Grove OLED
- Grove IMU

Initial templates:

- blinky
- i2c_scan
- sensor_to_serial
- button_to_serial
- relay_control

One-sentence summary: start with representative hardware and simple scenarios before expanding to advanced projects.

## 9. Final Recommendation

The strategy is worth pursuing only if it remains focused:

```text
Upstream Zephyr for core OS and board support.
Seeed Zephyr Base for XIAO and Grove product metadata.
CLI for deterministic project generation.
VS Code plugin for developer experience.
Vendor SDKs for advanced chip-specific scenarios.
```

One-sentence summary: the winning architecture is not one giant platform, but a layered system with clear responsibilities.
