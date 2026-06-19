# Phase 3: VS Code Plugin

## 1. Goal

Phase 3 turns the CLI and metadata foundation into a developer-facing product inside VS Code.

The plugin should focus on the part that is uniquely Seeed's: choosing a XIAO board, expansion board, and Grove modules, checking compatibility, previewing wiring, configuring options, and generating a correct project. The build, flash, monitor, and debug steps are deliberately not reimplemented here.

The official Zephyr VS Code extension, and vendor extensions such as nRF Connect for VS Code, already provide environment setup, build, flash, monitor, and debug for Zephyr projects, and they do it well. Rebuilding that layer would duplicate mature tooling and add maintenance with no unique value. The plugin instead generates a standard Zephyr project and hands off to those extensions for the toolchain steps.

The ideal experience combines three proven ideas, all on the pre-build side where the unique value lives:

- CubeMX-style hardware configuration
- ESPHome-style component selection and low-friction setup
- Wokwi-style wiring preview and project visualization

The plugin should not try to become a complete electronic design tool, a full hardware simulator, or a replacement for the official Zephyr toolchain extensions in its first version.

One-sentence summary: Phase 3 owns hardware selection, compatibility, wiring, and generation, and hands the build-and-flash toolchain to the official Zephyr extensions.

## 2. Product Position

Recommended product name:

```text
Seeed XIAO Project Assistant
```

The plugin should be positioned as:

```text
A VS Code assistant for choosing, configuring, and generating XIAO + Grove Zephyr projects, ready to build with the official Zephyr extension.
```

It should not be positioned as:

```text
A replacement for Zephyr
A replacement for VS Code
A replacement for the official Zephyr or vendor toolchain extensions
A complete simulator
A universal embedded IDE
```

One-sentence summary: the plugin is a focused project-creation assistant that stops at the door of the official build toolchain.

## 3. User Journey

### Step 1: Open The Plugin

The user opens the XIAO Project Assistant panel in VS Code.

The plugin shows:

- create new project
- open existing generated project
- check local environment
- view supported boards and modules

One-sentence summary: the first screen should help users choose a clear starting path.

### Step 2: Select XIAO Board

The user selects a board such as:

- XIAO ESP32C6
- XIAO ESP32S3
- XIAO nRF54L15
- XIAO MG24
- XIAO RP2350

The plugin shows:

- Zephyr board target
- supported interfaces
- wireless support status
- validation status
- known issues
- recommended toolchain

One-sentence summary: board selection decides what the rest of the project can support.

### Step 3: Select Expansion Board

The user selects:

- XIAO Grove Shield
- XIAO Expansion Board
- XIAO Round Display
- XIAO ePaper Driver Board
- custom wiring

The expansion board maps physical ports to XIAO interfaces.

One-sentence summary: expansion-board selection tells the plugin where modules can be connected.

### Step 4: Select Grove Modules

The user selects modules such as:

- Grove SHT40
- Grove Button
- Grove Relay
- Grove Light Sensor
- Grove OLED
- Grove IMU

The plugin checks:

- required interface
- default address
- driver availability
- power requirements
- port availability
- compatibility status

One-sentence summary: the user chooses product names, while the plugin handles technical constraints.

### Step 5: Configure Settings

The plugin shows a settings panel similar to a lightweight CubeMX experience.

Possible settings:

- GPIO pin
- I2C bus
- I2C address
- SPI bus
- SPI frequency
- UART baud rate
- ADC channel
- sampling interval
- logging level
- BLE device name
- MQTT host and topic
- low-power wake interval
- west or PlatformIO output

Defaults must work without manual changes.

One-sentence summary: advanced users can tune settings, but beginners should be able to use defaults.

### Step 6: View Wiring Preview

The plugin renders a wiring diagram.

First version should use SVG or a Webview-rendered diagram.

The diagram should show:

- selected XIAO board
- selected expansion board
- selected Grove modules
- port names
- signal mapping
- voltage requirements
- warnings

Example mapping:

```text
Grove SHT40
VCC -> 3V3
GND -> GND
SDA -> xiao_i2c.sda
SCL -> xiao_i2c.scl
```

One-sentence summary: the wiring preview should reduce the user's fear of connecting hardware incorrectly.

### Step 7: Generate Project

The user clicks Generate.

The plugin calls the CLI:

```bash
seeed-zephyr generate ...
```

The generated project includes:

- source code
- Zephyr configuration
- Devicetree overlay
- build files
- README
- wiring diagram
- metadata snapshot

One-sentence summary: project generation should remain deterministic and powered by the CLI.

### Step 8: Hand Off To The Official Toolchain

After generation, the plugin does not run the build itself. It opens the generated project in a way the official Zephyr VS Code extension recognizes, and points the user at that extension's existing Build, Flash, Monitor, and Debug actions.

The plugin provides only the actions that belong to its own scope:

- Open the generated project
- Open README
- Open wiring diagram
- Detect whether the official Zephyr extension is installed, and offer to install it if missing
- Start the recommended build with a single click that triggers the official extension's build action

This keeps a clean boundary: the plugin owns selection, compatibility, wiring, and generation; the official extension owns build, flash, monitor, and debug.

One-sentence summary: after generating a correct project, the plugin hands the user to the official Zephyr extension for build and flash instead of duplicating it.

## 4. Plugin Architecture

Recommended modules:

```text
Hardware Catalog
Compatibility Engine
Wiring Renderer
Config Panel
Project Generator Adapter
Toolchain Handoff
Grove Error Hints
```

The modules above are the plugin's own scope. Build, flash, monitor, debug, and full environment setup are intentionally not modules here; they are delegated to the official Zephyr extension through Toolchain Handoff.

### Hardware Catalog

Loads board, Grove, expansion-board, template, and compatibility metadata.

One-sentence summary: the catalog is the plugin's product database.

### Compatibility Engine

Checks whether the selected hardware and template can work together.

It should detect:

- missing interfaces
- pin conflicts
- duplicate I2C addresses
- unsupported board features
- build-only or experimental status

One-sentence summary: the compatibility engine prevents users from generating known-bad projects.

### Wiring Renderer

Creates visual wiring diagrams from metadata.

The first version should prioritize correctness over visual complexity.

One-sentence summary: the wiring renderer turns metadata into something users can physically follow.

### Config Panel

Displays editable options and validates them.

One-sentence summary: the config panel is where users customize the project without editing Zephyr files manually.

### Project Generator Adapter

Calls the CLI and reports progress.

One-sentence summary: the adapter connects the graphical plugin to the deterministic generator.

### Toolchain Handoff

Connects the generated project to the official Zephyr VS Code extension. It detects whether that extension is installed, offers to install it when missing, opens the project so the extension picks it up, and triggers the extension's own build action.

It does not run west, flash, monitor, or debug directly, and it does not re-check the toolchain environment; the official extension already owns environment setup and these commands.

One-sentence summary: the handoff module is a thin bridge to the official extension, not a second toolchain.

### Grove Error Hints

Maps a small set of Seeed-specific failure patterns to human-readable suggestions: a wrong I2C address for a known Grove module, a missing Kconfig for a selected driver, a module plugged into a port the shield does not expose.

General Zephyr, west, CMake, and Devicetree errors are left to the official extension and the wider Zephyr community, which already document them. This module stays narrow, covering only what is unique to XIAO and Grove. It starts as a rules-based lookup; AI can be added later but is not required.

One-sentence summary: error hints stay focused on XIAO and Grove mistakes, not on general Zephyr toolchain errors.

## 5. Technology Choices

Recommended implementation:

- VS Code extension in TypeScript
- Webview UI for the project configurator
- SVG for wiring diagrams
- CLI integration for generation
- official Zephyr VS Code extension as a dependency for build, flash, monitor, and debug
- VS Code extension API to detect, install, and trigger that extension

One-sentence summary: use normal VS Code extension technology, lean on the official Zephyr extension for the toolchain, and avoid unnecessary custom infrastructure.

## 6. MVP Scope

Recommended first plugin version:

### Boards

- XIAO ESP32C6
- XIAO nRF54L15
- XIAO MG24

### Expansion Boards

- XIAO Grove Shield
- XIAO Expansion Board

### Grove Modules

- Grove SHT40
- Grove Button
- Grove Relay
- Grove Light Sensor
- Grove OLED

### Templates

- Sensor to Serial
- Button to Serial
- Relay Control
- I2C Scan

### Toolchain

- generate standard west projects
- delegate build, flash, monitor, and debug to the official Zephyr extension
- PlatformIO output considered only in a later release, if there is real demand

### Core Features (plugin's own scope)

- hardware selection
- compatibility display
- parameter panel
- wiring diagram
- project generation
- one-click handoff to the official Zephyr extension's build action
- XIAO and Grove specific error hints

### Delegated To The Official Zephyr Extension

- build
- flash
- monitor
- debug
- toolchain environment setup and checks

One-sentence summary: the MVP owns selection-to-generation, hands off the toolchain, and stays small enough to finish while proving the unique workflow.

## 7. Features To Avoid In The First Version

Do not start with:

- a reimplementation of build, flash, monitor, or debug that the official Zephyr extension already provides
- a custom toolchain environment doctor that duplicates the official extension
- complete Wokwi-style simulation
- arbitrary drag-and-drop circuit editing
- all XIAO boards
- all Grove modules
- cloud accounts
- online build service
- AI-generated drivers
- full package manager

One-sentence summary: do not rebuild the official toolchain; first prove the unique selection-to-generation workflow, then add intelligence and scale.

## 8. Success Criteria

Phase 3 should be considered successful when:

- a user can create a project without manually writing Zephyr boilerplate
- selected combinations show clear compatibility status
- wiring diagrams match real hardware
- generated projects build through the official Zephyr extension without manual fixups
- the handoff to that extension is one click and works on a clean setup
- at least several combinations flash and run on real boards via the official toolchain
- XIAO and Grove specific mistakes produce clear hints
- early users complete their first project faster than with manual Zephyr setup

One-sentence summary: the plugin succeeds when users go from hardware choice to a generated project that builds cleanly in the official extension, without learning every Zephyr detail first.

## 9. Future Extensions

After MVP, possible extensions include:

- PlatformIO support
- more XIAO boards
- more Grove modules
- Home Assistant templates
- MQTT templates
- BLE templates
- low-power templates
- AI-assisted error explanation
- AI-assisted project selection
- web compatibility matrix generated from the same metadata
- online project preview

One-sentence summary: the plugin can grow from a generator into the main XIAO developer experience.
