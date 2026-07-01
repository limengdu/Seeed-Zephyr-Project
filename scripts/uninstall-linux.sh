#!/usr/bin/env bash
#
# Purpose:
#   Uninstall Seeed Zephyr Base from Linux. Removes the seeed-zephyr CLI
#   symlink, optionally the Zephyr workspace and SDK, and lists the shared
#   host packages, group membership, and udev rules that setup added so you
#   can remove them yourself.
#
# Usage:
#   bash scripts/uninstall-linux.sh [--yes] [--dry-run]

set -uo pipefail

SETUP_PLATFORM_LABEL="Linux"
UNINSTALL_SCRIPT_NAME="scripts/uninstall-linux.sh"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CLI_INSTALL_DIR_CANDIDATES=("$HOME/.local/bin" "/usr/local/bin")

# shellcheck source=scripts/lib/uninstall-common.sh
source "$SCRIPT_DIR/lib/uninstall-common.sh"

APT_PACKAGES=(
  git
  cmake
  ninja-build
  gperf
  ccache
  dfu-util
  device-tree-compiler
  wget
  python3-dev
  python3-venv
  python3-pip
  python3-setuptools
  python3-tk
  python3-wheel
  xz-utils
  file
  make
  gcc
  gcc-multilib
  g++-multilib
  libsdl2-dev
  libmagic1
  bossa-cli
)

DNF_PACKAGES=(
  git
  cmake
  ninja-build
  gperf
  ccache
  dfu-util
  dtc
  wget
  which
  xz
  file
  make
  gcc
  gcc-c++
  python3-pip
  python3-setuptools
  python3-wheel
  python3-devel
  python3-tkinter
  SDL2-devel
  bossa
)

# Lists the shared Linux packages, group, and udev rules setup added.
# 列出 setup 添加的共享 Linux 软件包、用户组和 udev 规则。
print_system_tools_note() {
  local current_user="${USER:-$(id -un)}"

  printf 'Setup installed shared host packages with your package manager.\n'
  printf 'They are shared with the rest of your system, so this uninstaller keeps them.\n'
  printf '\nDebian/Ubuntu packages:\n  %s\n' "${APT_PACKAGES[*]}"
  printf '\nFedora packages:\n  %s\n' "${DNF_PACKAGES[*]}"
  printf '\nRemove any you no longer need yourself, for example:\n'
  printf '  sudo apt-get remove <package>    # Debian/Ubuntu\n'
  printf '  sudo dnf remove <package>        # Fedora\n'
  printf '\nSetup may also have added device-access settings. To undo them yourself:\n'
  printf '  sudo gpasswd -d "%s" dialout\n' "$current_user"
  printf '  sudo gpasswd -d "%s" plugdev\n' "$current_user"
  printf '  sudo rm /etc/udev/rules.d/60-openocd.rules   # plus any Zephyr SDK *.rules you added\n'
  printf '  sudo udevadm control --reload-rules && sudo udevadm trigger\n'
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  run_uninstall_flow "$@"
fi
