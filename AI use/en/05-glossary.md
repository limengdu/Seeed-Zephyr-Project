# Glossary

This glossary explains project terms in plain language.

## Zephyr

Zephyr is an open-source real-time operating system for embedded devices.

Plain explanation: it is a shared software base that can run on many different
microcontrollers.

One-sentence summary: Zephyr is the operating layer this repository builds on.

## XIAO

XIAO is Seeed's compact development-board family.

Plain explanation: it is the small main board that runs the user's firmware.

One-sentence summary: XIAO is the board at the center of this repository.

## Grove

Grove is Seeed's modular sensor and actuator ecosystem.

Plain explanation: Grove modules connect with standardized cables instead of
manual soldering.

One-sentence summary: Grove is the plug-in module system this repository teaches
and validates.

## Example

An example is a small, focused Zephyr application in this repository.

Plain explanation: it proves one board capability, one Grove module behavior, or
one expansion-board feature with the least extra code possible.

One-sentence summary: examples are the smallest useful learning and validation
units.

## Project

A project is a larger application that combines boards, Grove modules, expansion
boards, and a real scenario.

Plain explanation: it shows how multiple examples become a useful outcome.

One-sentence summary: projects are complete reference builds users can study and
adapt.

## Capability

A capability is something a board or module can do, such as I2C, UART, ADC, PWM,
BLE, Wi-Fi, display output, storage, or low power.

Plain explanation: capabilities are how users search for the feature they need.

One-sentence summary: capability is the bridge between hardware features and
examples.

## Board Target

A board target is the name Zephyr uses to build firmware for a specific board.

Plain explanation: it tells Zephyr which board the project should run on.

One-sentence summary: board target is Zephyr's internal board name.

## Devicetree

Devicetree is Zephyr's machine-readable hardware map.

Plain explanation: it tells software where devices, buses, pins, and modules are
connected.

One-sentence summary: Devicetree is the wiring truth that Zephyr reads.

## Overlay

An overlay is an extra Devicetree file that adds or changes project-specific
hardware information.

One-sentence summary: an overlay is a project-specific hardware note.

## Shield

A shield is Zephyr's reusable description of an add-on board.

Plain explanation: in this project, expansion boards should become Zephyr
shields when they own pin routing.

One-sentence summary: shield is the Zephyr-native way to describe expansion
boards.

## Metadata

Metadata is structured product information about boards, modules, examples,
projects, and validation status.

Plain explanation: it helps tools and users discover what exists and what is
known to work.

One-sentence summary: metadata makes the catalog searchable and testable.

## Validation Evidence

Validation evidence is the recorded proof behind a status.

Plain explanation: it includes build commands, Zephyr version, board target,
hardware used, result, date, and observed output.

One-sentence summary: validation evidence is why users can trust a support claim.

## Build-Only

Build-only means an example or project compiles, but has not been proven on real
hardware yet.

One-sentence summary: build-only is useful but not the same as hardware-tested.

## Hardware-Tested

Hardware-tested means the firmware was built, flashed, and observed on real
hardware.

One-sentence summary: hardware-tested is the strongest normal validation status.

## Community Contribution

A community contribution is an example, project, metadata improvement, or
validation report from outside the core maintainers.

Plain explanation: contributions are welcome when they follow structure and can
be validated.

One-sentence summary: community contributions grow the catalog without lowering
trust.

## CLI

CLI means command-line interface.

Plain explanation: it lets users and tools run repeatable commands.

One-sentence summary: the CLI operates the repository catalog.

## CI

CI means continuous integration.

Plain explanation: it automatically checks whether changes still build and pass
validation.

One-sentence summary: CI is the automated reviewer for examples and metadata.

## AI Project Charter

The AI project charter is the guidance under `AI use/`.

Plain explanation: it tells AI agents what this project is, how assets are
prioritized, and how to record work.

One-sentence summary: the AI charter gives future AI agents the project brief.

## AI Work Log

The AI work log is `AI use/WORKLOG.md`.

Plain explanation: it records meaningful AI work without becoming a private chat
transcript.

One-sentence summary: the work log is the handoff trail for future AI agents.

## Zephyr-First

Zephyr-first means Zephyr is the default path when it is suitable.

Plain explanation: it does not mean Zephyr is the only supported path.

One-sentence summary: Zephyr-first means prefer Zephyr while staying honest.
