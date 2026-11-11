# Changelog

## 0.5.7

- Upload XIAO nRF54LM20B signed images with a built-in SMP uploader, using a SHA-256 transfer digest and acknowledged 64-byte chunks with the factory USB loader.
- Add automatic 1200-baud loader entry and the application USB identity to the LM20B blinky example, and reconnect to its application serial port after upload.
- Document factory loader entry, signing, USB behavior, and hardware verification in the LM20B board notes. Create a fresh LM20B blinky project to include the updated firmware.
- Install seeed-zephyr 0.5.7 by default, paired with Zephyr v4.5.0 and SDK 1.0.1.

## 0.5.6

- Upload XIAO nRF54LM20B with the current `nrfutil mcu-manager` command names, and install that command on the first upload when `nrfutil` is already present.
- Install seeed-zephyr 0.5.6 by default, paired with Zephyr v4.5.0 and SDK 1.0.1.

## 0.5.5

- Rescan Projects after Open Project, including folders already in the workspace.
- Update the project list and active-project status bar when root-level `snapshot.json`, `CMakeLists.txt`, or `prj.conf` files change.
- Add **Refresh Projects** to the Projects title bar and command palette.
- Install seeed-zephyr 0.5.5 by default, paired with Zephyr v4.5.0 and SDK 1.0.1.

## 0.5.4

- Enable XIAO STM32C5 USB with the 48 MHz clock and PA11/PA12 pin settings in the `blinky` board overlay.
- Request the STM32C5 TinyUF2 bootloader through USB serial at 1200 baud for consecutive uploads, and recognize boot volumes by label or board identity.
- Mark the XIAO nRF54LM20A and STM32C5 `blinky` examples as hardware-tested.
- Install seeed-zephyr 0.5.4 by default. Create a fresh STM32C5 `blinky` project to include the updated overlay, configuration, and source.

## 0.5.3

- Show separate hardware-tested, build-verified, and pending board counts for each Grove example in the Catalog.
- Save the selected board's Grove verification status in each generated project's `snapshot.json`, using the example's board matrix.
- Install seeed-zephyr 0.5.3 by default.

## 0.5.2

- Install seeed-zephyr 0.5.2 by default, which adds baseline `blinky` examples for XIAO nRF54LM20A, XIAO nRF54LM20B, and XIAO STM32C5.
- Upload XIAO nRF54LM20B through its factory USB firmware loader (`nrfutil mcu-manager`) and XIAO STM32C5 by copying its UF2 image to the TinyUF2 boot volume.
- Mark the XIAO ESP32-C5 `blinky` example as hardware-tested.

## 0.5.1

- Install seeed-zephyr 0.5.1 by default, whose XIAO ESP32-C5 example is `blinky`: it toggles the user LED and prints the LED state.
- Close earlier Upload and Monitor terminals before a new upload or monitor starts, so the serial port is free for the new action.

## 0.5.0

- Add **Switch Version** to move the examples, Zephyr workspace, and managed CLI to one published release together, with the active version pair shown in the Environment view.
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
