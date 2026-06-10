# Phase 3: VS Code Plugin

## 1. Goal

Phase 3 turns the CLI and metadata foundation into a developer-facing product inside VS Code.

The plugin should provide a XIAO-first hardware configuration, wiring preview, project generation, build, flash, monitor, and debug workflow.

The ideal experience combines three proven ideas:

- CubeMX-style hardware configuration
- ESPHome-style component selection and low-friction setup
- Wokwi-style wiring preview and project visualization

The plugin should not try to become a complete electronic design tool or a full hardware simulator in its first version.

One-sentence summary: Phase 3 makes the Zephyr base usable inside the editor where users actually build firmware.

## 2. Product Position

Recommended product name:

```text
Seeed XIAO Project Assistant
```

The plugin should be positioned as:

```text
A VS Code assistant for creating, configuring, building, flashing, and debugging XIAO + Grove projects.
```

It should not be positioned as:

```text
A replacement for Zephyr
A replacement for VS Code
A complete simulator
A universal embedded IDE
```

One-sentence summary: the plugin is a focused assistant, not a new full IDE.

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

### Step 8: Build, Flash, Monitor, Debug

After generation, the plugin provides actions:

- Build
- Flash
- Monitor
- Debug
- Clean
- Open README
- Open wiring diagram

For west projects, it should call:

```bash
west build
west flash
west debug
```

For PlatformIO projects, it should call:

```bash
pio run
pio run -t upload
pio device monitor
```

One-sentence summary: the plugin should guide users past generation and into running firmware.

## 4. Plugin Architecture

Recommended modules:

```text
Hardware Catalog
Compatibility Engine
Wiring Renderer
Config Panel
Project Generator Adapter
Toolchain Runner
Environment Doctor
Error Explainer
```

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

### Toolchain Runner

Runs west or PlatformIO commands through VS Code tasks or terminal integration.

One-sentence summary: the runner executes local build, flash, monitor, and debug commands.

### Environment Doctor

Checks:

- west availability
- PlatformIO availability
- Python availability
- Zephyr SDK availability
- CMake availability
- Ninja availability
- serial devices
- recommended Zephyr version

One-sentence summary: the environment doctor diagnoses setup problems before they become confusing build errors.

### Error Explainer

Maps common Zephyr, west, CMake, Devicetree, and flashing errors to human-readable suggestions.

This can start as a rules-based database. AI can be added later, but should not be required in the first version.

One-sentence summary: the error explainer turns scary logs into next steps.

## 5. Technology Choices

Recommended implementation:

- VS Code extension in TypeScript
- Webview UI for the project configurator
- SVG for wiring diagrams
- CLI integration for generation
- VS Code tasks for build and flash
- VS Code serial extension integration or built-in terminal command for monitor

One-sentence summary: use normal VS Code extension technology and avoid unnecessary custom infrastructure.

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

- west first
- PlatformIO in a later minor release

### Core Features

- hardware selection
- compatibility display
- parameter panel
- wiring diagram
- project generation
- build
- flash
- monitor
- environment check
- common error explanations

One-sentence summary: the MVP should be small enough to finish and complete enough to prove the workflow.

## 7. Features To Avoid In The First Version

Do not start with:

- complete Wokwi-style simulation
- arbitrary drag-and-drop circuit editing
- all XIAO boards
- all Grove modules
- cloud accounts
- online build service
- AI-generated drivers
- full debugger UI
- full package manager

One-sentence summary: first prove the core workflow, then add intelligence and scale.

## 8. Success Criteria

Phase 3 should be considered successful when:

- a user can create a project without manually writing Zephyr boilerplate
- selected combinations show clear compatibility status
- wiring diagrams match real hardware
- generated projects build through VS Code
- at least several combinations flash and run on real boards
- common environment errors are detected
- early users complete their first project faster than with manual Zephyr setup

One-sentence summary: the plugin succeeds when users can go from hardware choice to running firmware without learning every Zephyr detail first.

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
