# Phase 3: VS Code Product Experience

## 1. Goal

Phase 3 turns the repository's examples, projects, metadata, and validation
evidence into a developer-facing VS Code experience.

The plugin is a discovery and project assistant for XIAO + Grove Zephyr work.

One-sentence summary: Phase 3 makes the repository's verified content visible,
searchable, configurable, and project-ready inside VS Code.

## 2. Product Position

Recommended product name:

```text
Seeed XIAO Zephyr Assistant
```

It should help users:

- browse supported XIAO boards
- browse Grove modules
- browse examples by board, module, capability, and validation status
- browse complete projects
- preview wiring and configuration
- create a new project from repository examples/templates
- build through official Zephyr tooling
- understand XIAO/Grove-specific errors
- prepare contribution-ready examples

Its responsibility is:

- XIAO and Grove content discovery
- example and project browsing
- validation status display
- wiring and configuration preview
- project creation from repository assets
- contribution checks
- handoff to official Zephyr tooling for build, flash, monitor, and debug

One-sentence summary: the plugin is a guided front door to the XIAO + Grove
Zephyr example/project ecosystem.

## 3. User Journey

### Step 1: Choose A Starting Point

The first screen should offer:

- browse examples
- browse projects
- create from board/module
- open existing generated project
- validate a contribution

One-sentence summary: users can start from examples, projects, hardware, or
contribution checks.

### Step 2: Browse Or Select Hardware

The plugin shows boards and modules with:

- validation status
- supported capabilities
- available examples
- known issues
- recommended Zephyr version

One-sentence summary: discovery is as important as generation.

### Step 3: Select Example Or Project

Users can filter by:

- board
- Grove module
- interface
- capability
- expansion board
- build-only or hardware-tested status

One-sentence summary: examples and projects are first-class UI objects.

### Step 4: Preview Details

The plugin shows:

- README summary
- build command
- board target
- required hardware
- wiring diagram
- expected serial output or behavior
- validation evidence

One-sentence summary: users should know what will happen before creating or
building anything.

### Step 5: Create Or Open Project

The plugin calls the CLI to copy/generate a standard Zephyr project from a known
example or template.

One-sentence summary: generated projects are derived from repository assets.

### Step 6: Handoff To Official Tooling

Build, flash, monitor, and debug should be handed to official Zephyr tooling
where possible. The plugin owns the XIAO/Grove-specific discovery, preview, and
project-creation flow.

One-sentence summary: the plugin owns Seeed-specific discovery and project
creation while official tools handle the generic Zephyr toolchain.

## 4. MVP Scope

MVP should include:

- example browser
- project browser
- board/module/capability filters
- validation badges
- wiring preview for selected examples
- project creation from a small set of examples
- CLI integration
- official Zephyr extension handoff

One-sentence summary: the MVP proves browsing, using, and creating from verified
repository content.

## 5. Success Criteria

Phase 3 succeeds when:

- users can find a relevant example faster than manual search
- users can create a project from a verified example
- generated projects build through official Zephyr tooling
- validation status is visible and understandable
- wiring diagrams match real hardware
- contribution checks are accessible
- early users finish a first XIAO + Grove Zephyr project with less friction than
  manual Zephyr setup

One-sentence summary: success means users can move from discovery to running
firmware with less friction and more confidence.

## 6. Future Extensions

After MVP:

- web compatibility matrix
- web example browser
- more complete project gallery
- AI-assisted example selection
- AI-assisted error explanation
- PlatformIO project output
- advanced low-power templates
- BLE, Wi-Fi, MQTT, Home Assistant projects

One-sentence summary: the plugin can grow because it stands on a verified
content catalog.
