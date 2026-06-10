# Glossary

This glossary explains important terms in plain language.

## Zephyr

Zephyr is an open-source real-time operating system for embedded devices.

Plain explanation: it is a shared software base that can run on many different microcontrollers.

One-sentence summary: Zephyr is a common operating layer for many small chips.

## RTOS

RTOS means real-time operating system.

Plain explanation: it is a small operating system designed for devices that need predictable timing, such as sensors, wireless devices, and industrial controllers.

One-sentence summary: an RTOS helps small devices run tasks at the right time.

## XIAO

XIAO is Seeed's compact development-board family.

Plain explanation: it is a small board that carries a microcontroller and exposes pins for sensors, communication, and expansion.

One-sentence summary: XIAO is the small main board that runs the user's firmware.

## Grove

Grove is Seeed's modular sensor and actuator ecosystem.

Plain explanation: Grove lets users connect sensors and modules with standardized cables instead of manual soldering.

One-sentence summary: Grove turns hardware modules into plug-and-play building blocks.

## Expansion Board

An expansion board is an add-on board that gives XIAO more convenient ports or features.

Plain explanation: it is like a power strip for XIAO, making it easier to connect Grove modules, displays, buttons, or batteries.

One-sentence summary: expansion boards make XIAO easier to connect to other hardware.

## Board Target

A board target is the name Zephyr uses to build firmware for a specific board.

Plain explanation: it tells Zephyr which board the project is meant to run on.

One-sentence summary: board target is Zephyr's internal name for the selected board.

## Devicetree

Devicetree is a hardware description system used by Zephyr.

Plain explanation: it is a machine-readable hardware map that tells software where LEDs, buttons, buses, and sensors are connected.

One-sentence summary: Devicetree is the wiring map that Zephyr can read.

## Overlay

An overlay is an extra Devicetree file that adds or changes hardware information.

Plain explanation: if a user plugs a Grove sensor into a board, the overlay tells Zephyr about that added sensor.

One-sentence summary: an overlay is a small extra wiring note for a specific project.

## Kconfig

Kconfig is Zephyr's configuration system.

Plain explanation: it controls which features are turned on or off, such as sensors, logging, Bluetooth, Wi-Fi, or drivers.

One-sentence summary: Kconfig is the feature switchboard for a Zephyr project.

## prj.conf

`prj.conf` is the project configuration file used by Zephyr.

Plain explanation: it stores the feature switches for one project.

One-sentence summary: `prj.conf` says which Zephyr features this project needs.

## west

west is Zephyr's command-line tool.

Plain explanation: it helps download Zephyr modules, build projects, flash firmware, and run debug commands.

One-sentence summary: west is the standard command tool for Zephyr projects.

## CMake

CMake is a build configuration tool.

Plain explanation: it tells the computer how to turn source code into firmware.

One-sentence summary: CMake prepares the build instructions.

## Ninja

Ninja is a build execution tool.

Plain explanation: after CMake prepares build instructions, Ninja runs them quickly.

One-sentence summary: Ninja does the actual build work after CMake prepares it.

## PlatformIO

PlatformIO is an embedded development platform that works inside editors such as VS Code.

Plain explanation: it organizes projects, dependencies, build commands, upload commands, and serial monitoring in a user-friendly way.

One-sentence summary: PlatformIO is a friendly project system for embedded development.

## Metadata

Metadata is structured information about something.

Plain explanation: board metadata describes a board; Grove metadata describes a module; template metadata describes what a project needs.

One-sentence summary: metadata is product information written in a way software can understand.

## CLI

CLI means command-line interface.

Plain explanation: it is a tool users run by typing commands in a terminal.

One-sentence summary: a CLI lets users and other tools run repeatable commands.

## CI

CI means continuous integration.

Plain explanation: it is an automatic check system that builds or tests code whenever changes are made.

One-sentence summary: CI is a robot that checks whether changes broke anything.

## Hardware-in-loop

Hardware-in-loop means testing software on real hardware automatically.

Plain explanation: instead of only compiling firmware, the test system flashes it to a real board and checks the result.

One-sentence summary: hardware-in-loop proves the code runs on real devices.

## VS Code Webview

A VS Code Webview is a small web-based panel inside a VS Code extension.

Plain explanation: it lets a plugin show custom screens, forms, diagrams, and controls.

One-sentence summary: Webview lets a VS Code plugin have its own visual interface.

## Wiring Diagram

A wiring diagram shows how hardware parts connect.

Plain explanation: it tells users which Grove port, pin, power line, and signal line should connect to which module.

One-sentence summary: a wiring diagram is the user's visual connection guide.

## Compatibility Matrix

A compatibility matrix shows which combinations work.

Plain explanation: it might show whether a XIAO board supports a Grove module under Zephyr, and whether that support is tested or experimental.

One-sentence summary: a compatibility matrix is a map of what works and what does not.

## Template

A template is a prepared project pattern.

Plain explanation: instead of writing every file from scratch, the generator fills in a known-good project structure.

One-sentence summary: a template is a reusable starter project.

## Vendor SDK

A vendor SDK is the official software development kit from a chip maker.

Plain explanation: Espressif, Nordic, Silicon Labs, Renesas, and other chip vendors provide their own software packages for their chips.

One-sentence summary: a vendor SDK is the chip maker's own development toolkit.

## Zephyr-first

Zephyr-first means Zephyr is the default recommended path when it is suitable.

Plain explanation: it does not mean Zephyr is the only supported path.

One-sentence summary: Zephyr-first means prefer Zephyr, but keep other paths where they are better.
