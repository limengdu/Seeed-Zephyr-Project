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

The single source of version truth is
`packages/seeed-zephyr/src/seeed_zephyr/__init__.py`. `pyproject.toml` declares
`dynamic = ["version"]` and reads that file through `[tool.hatch.version]`, so
the version is edited in exactly one place.

## Automated Releases (GitHub Actions)

Two workflows publish on a version tag or from a manual run:

| Workflow | Trigger | Publishes |
|----------|---------|-----------|
| `.github/workflows/release-pypi.yml` | tag `cli-v*` or manual run | PyPI |
| `.github/workflows/release-vscode.yml` | tag `ext-v*` or manual run | VS Code Marketplace + Open VSX |

Both workflows verify that the tag matches the version in the code
(`__init__.py` for the CLI, `package.json` for the extension) before
publishing.

The extension workflow packages one `.vsix` and publishes it to each registry
whose token secret is configured. A registry with no token is skipped, so the
run succeeds even when only one marketplace is set up.

**One-time setup:**

- **PyPI (Trusted Publishing):** on PyPI, open the `seeed-zephyr` project →
  Publishing → add a GitHub Actions trusted publisher with repository
  `Seeed-Projects/seeed-zephyr-base` and workflow `release-pypi.yml`. No token
  is stored in GitHub.
- **VS Code Marketplace:** create a Marketplace personal access token for the
  `seeed-studio` publisher, then add it to the GitHub repository as a secret
  named `VSCE_PAT`.
- **Open VSX (Cursor, Windsurf, VSCodium, Gitpod, Theia, etc.):** sign in at
  [open-vsx.org](https://open-vsx.org) with GitHub, sign the Eclipse publisher
  agreement, create the `seeed-studio` namespace, generate an access token, and
  add it to the GitHub repository as a secret named `OVSX_PAT`.

**Cutting a release:**

```sh
# CLI: bump packages/seeed-zephyr/src/seeed_zephyr/__init__.py, commit, then:
git tag cli-v0.2.0 && git push origin cli-v0.2.0

# Extension: bump tools/vscode-extension/package.json version, commit, then:
git tag ext-v0.1.1 && git push origin ext-v0.1.1
```

## Manual Build (fallback)

Build each artifact directly from the source tree so the force-included files
above the package directory resolve:

```sh
cd packages/seeed-zephyr
python -m build --wheel
python -m build --sdist
python -m twine upload dist/*
```

Homebrew stays manual: after a PyPI release, update `Formula/seeed-zephyr.rb`
with the new sdist URL and SHA256.

## Status

- [x] Plan documented
- [x] Path detection refactored in CLI
- [x] Package structure created (using hatch force-include)
- [x] install.sh created
- [x] Homebrew formula created (SHA256 placeholder)
- [x] README updated with three install methods
- [x] First PyPI publish (v0.1.0, 2026-06-27)
- [x] Version single-sourced via hatch dynamic versioning
- [x] Automated PyPI release workflow (`release-pypi.yml`)
- [x] Automated VS Code Marketplace release workflow (`release-vscode.yml`)
- [x] Open VSX publishing added to the extension workflow
- [x] First Open VSX publish (`seeed-studio.seeed-xiao-zephyr-assistant` v0.1.0)
