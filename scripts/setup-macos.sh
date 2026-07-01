#!/usr/bin/env bash
#
# Purpose:
#   Set up a macOS Apple Silicon machine for a buildable Seeed Zephyr Base
#   Zephyr workspace using the steps validated for this repository.
#
# Usage:
#   bash scripts/setup-macos.sh [--board <board_id>]
#
# Example:
#   bash scripts/setup-macos.sh --board xiao_esp32c6
#
# Board-specific binary blob fetching is derived from board metadata:
# `metadata/boards/<board_id>.yaml` -> `vendor:` -> Zephyr HAL module.
#
# Prerequisites:
#   - macOS Apple Silicon.
#   - Homebrew already installed and available as `brew`.
#
# What this does NOT do:
#   - It does not install Homebrew.
#   - It does not create or reference a project west.yml.
#   - It does not configure regional mirrors.
#   - It does not build every board.
#   - It does not install Windows or Linux tooling.

set -euo pipefail

ZEPHYR_VERSION="${ZEPHYR_VERSION:-v4.4.0}"
ZEPHYR_WORKSPACE="${ZEPHYR_WORKSPACE:-$HOME/zephyrproject}"
SETUP_SCRIPT_NAME="scripts/setup-macos.sh"
SETUP_PLATFORM_LABEL="macOS"
PYTHON_INSTALL_HINT="Install Homebrew python3, then rerun this script."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CLI_INSTALL_DIR_CANDIDATES=("$HOME/.local/bin" "/opt/homebrew/bin")

# shellcheck source=scripts/lib/common.sh
source "$SCRIPT_DIR/lib/common.sh"

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
)

# Installs the requested Homebrew packages if they are missing.
# 安装缺失的指定 Homebrew 软件包。
install_brew_packages() {
  local missing_packages=()
  local package

  if (($# == 0)); then
    return
  fi

  for package in "$@"; do
    if brew list --formula "$package" >/dev/null 2>&1; then
      printf '  - %s is already installed.\n' "$package"
    else
      missing_packages+=("$package")
    fi
  done

  if ((${#missing_packages[@]} == 0)); then
    printf 'All Homebrew build tools are already installed.\n'
    return
  fi

  printf 'Installing missing Homebrew packages: %s\n' "${missing_packages[*]}"
  brew install "${missing_packages[@]}"
}

# Installs Homebrew packages required by the selected board.
# 安装所选开发板需要的 Homebrew 软件包。
install_board_brew_packages() {
  case "$BOARD_BUILD_TARGET" in
    seeeduino_xiao)
      install_brew_packages bossa
      ;;
    xiao_ra4m1)
      install_brew_packages dfu-util
      ;;
    "")
      # No board selection means a full host dependency install.
      # 未选择开发板时执行完整主机依赖安装。
      install_brew_packages bossa dfu-util
      ;;
    *)
      printf 'No board-specific Homebrew packages required for %s.\n' "$BOARD_ID"
      ;;
  esac
}

# Loads Homebrew into the current shell session from its known install paths.
# 从已知安装路径把 Homebrew 载入当前 shell 会话。
load_brew_shellenv() {
  local brew_path
  for brew_path in /opt/homebrew/bin/brew /usr/local/bin/brew; do
    if [[ -x "$brew_path" ]]; then
      eval "$("$brew_path" shellenv)"
      return 0
    fi
  done
  return 1
}

# Installs Homebrew automatically after asking, or exits with guidance.
# 询问后自动安装 Homebrew，否则退出并给出指引。
ensure_homebrew() {
  if command_exists brew; then
    return
  fi

  printf 'Homebrew is required to install macOS build tools but was not found.\n'
  if prompt_yes_default "Install Homebrew automatically now?"; then
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    load_brew_shellenv || true
    command_exists brew || fail "Homebrew install did not finish. Open a new terminal and rerun this script."
    printf 'Homebrew is ready.\n'
  else
    fail "Homebrew is required. Install it from https://brew.sh/, then rerun this script."
  fi
}

# Installs macOS system dependencies before the shared Zephyr setup flow.
# 在共享 Zephyr 安装流程前，安装 macOS 系统依赖。
install_system_dependencies() {
  ensure_homebrew
  install_brew_packages "${BREW_PACKAGES[@]}"
  install_board_brew_packages
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  run_setup_flow "$@"
fi
