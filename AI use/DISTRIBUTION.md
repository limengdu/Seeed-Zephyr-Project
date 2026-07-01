# CLI Distribution Plan

## Overview

The `seeed-zephyr` CLI supports three installation channels so users can
install it with a single command on any platform — no repository clone required.

| Channel | Command | Platforms |
|---------|---------|-----------|
| **PyPI** | `pip install seeed-zephyr` | macOS, Linux, Windows |
| **curl script** | `curl -fsSL .../install.sh \| bash` | macOS, Linux |
| **Homebrew** | `brew install limengdu/seeed/seeed-zephyr` | macOS, Linux |

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

Releases are driven by the version number, not by tags. Each workflow runs on
every push to `main` (or from a manual run), reads the version in the code, and
publishes only when that version has not been released yet:

| Workflow | Trigger | Release condition | Publishes |
|----------|---------|-------------------|-----------|
| `.github/workflows/release-pypi.yml` | push to `main` or manual run | `__init__.py` version not on PyPI | PyPI, then the Homebrew tap |
| `.github/workflows/release-vscode.yml` | push to `main` or manual run | `package.json` version not on Open VSX | VS Code Marketplace + Open VSX |

Because PyPI, Open VSX, and the VS Code Marketplace all refuse to overwrite an
existing version, the version number is a safe release switch: bump it and the
new release goes out; leave it unchanged and the workflow finds the version
already published and exits without doing anything.

The extension workflow packages one `.vsix` and publishes it to each registry
whose token secret is configured. A registry with no token is skipped, so the
run succeeds even when only one marketplace is set up.

**One-time setup:**

- **PyPI (Trusted Publishing):** on PyPI, open the `seeed-zephyr` project →
  Publishing → add a GitHub Actions trusted publisher with repository
  `limengdu/Seeed-Zephyr-Project` and workflow `release-pypi.yml`. No token
  is stored in GitHub.
- **VS Code Marketplace:** create a Marketplace personal access token for the
  `seeed-studio` publisher, then add it to the GitHub repository as a secret
  named `VSCE_PAT`.
- **Open VSX (Cursor, Windsurf, VSCodium, Gitpod, Theia, etc.):** sign in at
  [open-vsx.org](https://open-vsx.org) with GitHub, sign the Eclipse publisher
  agreement, create the `seeed-studio` namespace, generate an access token, and
  add it to the GitHub repository as a secret named `OVSX_PAT`.
- **Homebrew tap (auto-update):** create a fine-grained GitHub token with
  contents write access to `limengdu/homebrew-seeed`, then add it to the GitHub
  repository as a secret named `HOMEBREW_TAP_TOKEN`. After a PyPI release, the
  workflow reads the new wheel's URL and SHA256 and commits them to the tap's
  `Formula/seeed-zephyr.rb`. Without this secret the step is skipped, and the
  formula can be updated by hand instead.

**Cutting a release:**

Bump the version, commit, and push to `main`. The matching workflow detects the
new version and publishes it automatically.

```sh
# CLI: bump the version in
# packages/seeed-zephyr/src/seeed_zephyr/__init__.py, then:
git commit -am "release: seeed-zephyr 0.2.0" && git push

# Extension: bump the version in tools/vscode-extension/package.json, then:
git commit -am "release: extension 0.1.1" && git push
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

## Homebrew Tap

The tap lives in a separate repository, `limengdu/homebrew-seeed`, so users
install with:

```sh
brew install limengdu/seeed/seeed-zephyr
```

The formula installs the published PyPI **wheel** into an isolated virtualenv
(the CLI is pure Python, so the universal `py3-none-any` wheel works on every
platform). The `release-pypi.yml` workflow keeps the tap current: after each
PyPI release it reads the new wheel's `url` and `sha256` (from
`https://pypi.org/pypi/seeed-zephyr/<version>/json`) and commits them to the
tap's `Formula/seeed-zephyr.rb`. This requires the `HOMEBREW_TAP_TOKEN` secret;
without it the tap can be updated by editing those two lines by hand. The
`Formula/seeed-zephyr.rb` kept in this repository is the reference copy.

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
- [x] Homebrew tap live (`limengdu/homebrew-seeed`, installs the PyPI wheel)
- [x] Homebrew tap auto-updated by `release-pypi.yml` after each PyPI release
