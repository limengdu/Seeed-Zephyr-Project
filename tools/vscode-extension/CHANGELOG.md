# Changelog

## Unreleased

- Display every Zephyr project in a multi-root workspace and allow the active build, upload, and monitor target to be switched from the Projects view.

## 0.4.0

- Add hardware-tested Grove ultrasonic support across supported XIAO boards.
- Improve Grove project creation, pin configuration, flashing, and serial monitoring flows.
- Display board-specific chip pin labels in the pin configurator.

## 0.2.1

- Keep environment setup, CLI selection, CLI version selection, and repository selection actions available from the Catalog title bar More Actions menu after setup.

## 0.2.0

- Add a first-run environment screen with setup, CLI detection, managed CLI installation, CLI version selection, CLI path selection, and repository selection actions.
- Add extension-managed CLI installation so users can choose older published `seeed-zephyr` versions from the editor.

## 0.1.2

- Add an Update Repository action to refresh catalog examples and metadata from the editor.

## 0.1.1

- Add the marketplace icon shown on the extension listing.

## 0.1.0

Initial release.

- Catalog tree of XIAO boards, Grove modules, and expansion boards with validation badges, read directly from repository metadata (works offline).
- Detail preview panel for examples, boards, modules, and expansion boards: README, build command, validation status, and hardware notes.
- Create a project from a repository example through the `seeed-zephyr` CLI, with a `snapshot.json` receipt.
- Build, flash, monitor, and debug from the tree, delegated to Zephyr tooling in an integrated terminal.
- PlatformIO-style status bar quick actions (Build / Upload / Monitor) when a generated project or a Zephyr app is open in the workspace.
