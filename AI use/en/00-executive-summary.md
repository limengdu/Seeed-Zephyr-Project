# Executive Summary

## 1. Mission

Seeed Zephyr Base exists to become the XIAO + Grove entry point for Zephyr.

Its mission is to build:

- a curated library of minimal XIAO board examples
- a curated library of Grove module examples
- a collection of complete XIAO + Grove projects
- a capability catalog that shows what each board/module can do
- validation evidence that proves what builds and what runs on real hardware
- a contribution path for community examples and projects
- future CLI and VS Code tooling built on the assets above

Tools in this repository should be judged by how well they help users discover,
build, validate, adapt, or contribute examples and projects.

One-sentence summary: the core product is a verified XIAO + Grove Zephyr
examples and projects hub, with tooling built around it.

## 2. Strategic Direction

The direction is:

```text
Zephyr-first, with the right ecosystem for each user path.
```

Zephyr is the shared foundation for examples, reusable project structure,
validation, and future tooling. Arduino, MicroPython, CircuitPython, vendor SDKs,
and PlatformIO remain valid where they serve users better.

The purpose is to let a XIAO user start from a board, Grove module, capability,
or project idea and quickly find a working Zephyr path.

One-sentence summary: Zephyr is the default foundation, but the product starts
from XIAO/Grove user needs.

## 3. What This Repository Owns

This repository owns the Seeed product layer around upstream Zephyr:

- examples for board capabilities such as GPIO, I2C, UART, ADC, PWM, USB, BLE,
  Wi-Fi, display, storage, and low power
- Grove module examples such as basic sensor reads, actuator control, display
  output, and communication modules
- complete projects that combine boards, Grove modules, expansion boards, and
  real user scenarios
- metadata for boards, Grove modules, expansion boards, templates, examples, and
  projects
- validation logs and machine-readable status derived from builds and hardware tests
- scripts and future CLI commands for listing, building, validating, generating,
  and contributing examples and projects
- AI-facing project guidance under `AI use/`

One-sentence summary: upstream Zephyr owns the OS; this repository owns the
verified Seeed XIAO + Grove product experience on top of it.

## 4. Product Quality Standard

Every major addition should strengthen at least one reusable project asset:

- a buildable example
- a complete project
- a documented capability
- validation evidence
- metadata that improves discovery
- a contribution path that keeps examples reviewable

One-sentence summary: the repository improves when it adds or strengthens
assets that users and contributors can reuse.

## 5. Roadmap

### Phase 1: Examples, Projects, Metadata, And Validation Base

Build the repository assets users and maintainers can trust:

- minimal XIAO board examples
- Grove module examples
- expansion-board examples
- first complete projects
- metadata for boards, modules, examples, projects, and templates
- validation matrix for build and selected hardware tests
- contribution rules for external examples

### Phase 2: CLI For Discovery, Build, Validation, And Generation

Build a deterministic CLI that can:

- list boards, modules, capabilities, examples, and projects
- build a repository example from the project root
- validate metadata and example structure
- create a new project from known examples and templates
- support CI and future AI workflows

### Phase 3: VS Code Product Experience

Build a VS Code assistant that can:

- browse supported boards, Grove modules, capabilities, examples, and projects
- filter examples by board, module, interface, and validation status
- preview wiring and configuration
- generate a project from repository assets
- hand off build, flash, monitor, and debug to official Zephyr tooling

One-sentence summary: examples and projects come first; generator and plugin
come after there is real content to generate and browse.

## 6. Business Value

The value is:

- lower cost to support new XIAO boards
- less repeated Grove documentation work
- clearer learning paths for Zephyr on XIAO
- more reusable examples across chips
- a place for community contributions that can be validated
- stronger evidence for professional users
- a path from minimal examples to full projects and generated projects

One-sentence summary: the value is a growing, verified knowledge and example
base that reduces repeated work and increases user confidence.

## 7. Decision Standard

The project is on track only if users can increasingly do these things inside
this repository:

1. Find an example for a supported XIAO board capability.
2. Find a Grove module example.
3. Build an example without manually hunting through upstream Zephyr samples.
4. Flash a known-good example.
5. Understand whether the result is build-only or hardware-tested.
6. Adapt an example into a project.
7. Contribute a new example or project that can be validated.

One-sentence summary: success is measured by useful, validated examples and
projects.
