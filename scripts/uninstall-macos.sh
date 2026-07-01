#!/usr/bin/env bash
#
# Purpose:
#   Uninstall Seeed Zephyr Base from macOS. Removes the seeed-zephyr CLI
#   symlink, optionally the Zephyr workspace and SDK, and lists the shared
#   Homebrew build tools that setup installed so you can remove them yourself.
#
# Usage:
#   bash scripts/uninstall-macos.sh [--yes] [--dry-run]

set -uo pipefail

SETUP_PLATFORM_LABEL="macOS"
UNINSTALL_SCRIPT_NAME="scripts/uninstall-macos.sh"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CLI_INSTALL_DIR_CANDIDATES=("$HOME/.local/bin" "/opt/homebrew/bin" "/usr/local/bin")

# shellcheck source=scripts/lib/uninstall-common.sh
source "$SCRIPT_DIR/lib/uninstall-common.sh"

BREW_PACKAGES=(
  git
  cmake
  ninja
  gperf
  python3
  python-tk
  ccache
  qemu
  dtc
  libmagic
  wget
  openocd
  bossa
  dfu-util
)

# Lists the Homebrew tools setup installed and how to remove them by hand.
# 列出 setup 安装的 Homebrew 工具，并说明如何手动删除。
print_system_tools_note() {
  printf 'Setup installed these shared Homebrew build tools:\n'
  printf '  %s\n' "${BREW_PACKAGES[*]}"
  printf '\nThey are shared with the rest of your system, so this uninstaller keeps them.\n'
  printf 'Remove any you no longer need yourself, for example:\n'
  printf '  brew uninstall <package>\n'
  printf '\nIf setup installed Homebrew itself and you want it gone, follow the official steps:\n'
  printf '  https://github.com/homebrew/install#uninstall-homebrew\n'
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  run_uninstall_flow "$@"
fi
