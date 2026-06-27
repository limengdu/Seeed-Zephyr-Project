# CLI Distribution Plan

## Overview

The `seeed-zephyr` CLI supports three installation channels so users can
install it with a single command on any platform — no repository clone required.

| Channel | Command | Platforms |
|---------|---------|-----------|
| **PyPI** | `pip install seeed-zephyr` | macOS, Linux, Windows |
| **curl script** | `curl -fsSL .../install.sh \| bash` | macOS, Linux |
| **Homebrew** | `brew install seeed-studio/seeed/seeed-zephyr` | macOS, Linux |

## Architecture

```
seeed-zephyr-base/
├── packages/seeed-zephyr/          Python package (PyPI)
│   ├── pyproject.toml              hatchling build config
│   └── src/seeed_zephyr/           symlinks to source files
│       ├── cli.py                  → tools/cli/seeed_zephyr.py
│       ├── ra4m1_rom_flash.py      → tools/cli/ra4m1_rom_flash.py
│       ├── bootloaders/            → tools/cli/bootloaders/
│       └── data/
│           ├── boards/             → metadata/boards/
│           └── examples/           → examples/boards/
├── install.sh                      curl one-liner script
└── Formula/seeed-zephyr.rb         Homebrew formula template
```

The package uses hatchling's **force-include** to copy real files from their
original locations into the wheel and sdist at build time. This keeps a single
source of truth — all development happens in the original locations
(`tools/cli/`, `metadata/`, `examples/`). No symlinks are needed in the
package directory.

## Repo Mode vs Package Mode

The CLI detects whether it is running from a cloned repository or an installed
package. This detection uses a simple walk-up check for `metadata/boards/` from
the script's location.

| Feature | Package mode | Repo mode |
|---------|-------------|-----------|
| `list boards` | bundled YAML | repo YAML |
| `list examples` | bundled examples | repo examples |
| `build` / `flash` / `debug` | works | works |
| `monitor` | works | works |
| `matrix` | unavailable | works |
| `verify-hardware` | unavailable | works |

## Version Management

The single source of version truth is `packages/seeed-zephyr/src/seeed_zephyr/__init__.py`.
The `pyproject.toml` reads it via hatch's dynamic versioning.

## Publishing Checklist

1. Update version in `__init__.py`
2. Run `cd packages/seeed-zephyr && python -m build`
3. Test: `pip install dist/*.whl && seeed-zephyr list boards`
4. Publish: `python -m twine upload dist/*`
5. Update `Formula/seeed-zephyr.rb` with new URL and SHA256

## Status

- [x] Plan documented
- [x] Path detection refactored in CLI
- [x] Package structure created (using hatch force-include)
- [x] install.sh created
- [x] Homebrew formula created (SHA256 placeholder)
- [x] README updated with three install methods
- [ ] First PyPI publish
