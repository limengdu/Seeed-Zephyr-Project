# Changelog

## 0.1.0

Initial release.

- Catalog tree of XIAO boards, Grove modules, and expansion boards with validation badges, read directly from repository metadata (works offline).
- Detail preview panel for examples, boards, modules, and expansion boards: README, build command, validation status, and hardware notes.
- Create a project from a repository example through the `seeed-zephyr` CLI, with a `snapshot.json` receipt.
- Build, flash, monitor, and debug from the tree, delegated to Zephyr tooling in an integrated terminal.
- PlatformIO-style status bar quick actions (Build / Upload / Monitor) when a generated project or a Zephyr app is open in the workspace.
