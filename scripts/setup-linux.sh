#!/usr/bin/env bash
#
# Purpose:
#   Set up a supported Linux machine for a buildable Seeed Zephyr Base Zephyr
#   workspace, then delegate the Zephyr workspace flow to scripts/lib/common.sh.
#
# Usage:
#   bash scripts/setup-linux.sh [--board <board_id>]
#
# Example:
#   bash scripts/setup-linux.sh --board xiao_esp32c6
#
# Prerequisites:
#   - A supported Linux distribution with sudo.
#   - apt-get on Debian/Ubuntu or dnf on Fedora.
#
# NOT YET VERIFIED ON REAL LINUX:
#   This script was written and bash-syntax-checked on macOS. It still needs
#   real Linux validation for package installation, udev rules, and device
#   access.
#
# What this does NOT do:
#   - It does not install or use Homebrew.
#   - It does not install Windows tooling.
#   - It does not configure regional mirrors.
#   - It does not duplicate the shared Zephyr workspace flow.
#   - It does not install a parallel flash-tool chain outside Zephyr.

set -euo pipefail

ZEPHYR_VERSION="${ZEPHYR_VERSION:-v4.4.0}"
ZEPHYR_WORKSPACE="${ZEPHYR_WORKSPACE:-$HOME/zephyrproject}"
SETUP_SCRIPT_NAME="scripts/setup-linux.sh"
SETUP_PLATFORM_LABEL="Linux"
PYTHON_INSTALL_HINT="Install Python 3.12 or newer with venv and pip support, then rerun this script."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CLI_INSTALL_DIR_CANDIDATES=("$HOME/.local/bin" "/usr/local/bin")

# shellcheck source=scripts/lib/common.sh
source "$SCRIPT_DIR/lib/common.sh"

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
)

UDEV_RULE_CANDIDATES=()

# Prints a shell command before executing it.
# 在执行 shell 命令前打印该命令。
print_shell_command() {
  printf 'Running:'
  printf ' %q' "$@"
  printf '\n'
}

# Detects the supported Linux package manager.
# 检测受支持的 Linux 包管理器。
detect_package_manager() {
  if command_exists apt-get; then
    printf 'apt-get\n'
    return
  fi

  if command_exists dnf; then
    printf 'dnf\n'
    return
  fi

  return 1
}

# Prints manual package installation guidance for unsupported distributions.
# 为不受支持的发行版打印手动安装软件包指引。
print_manual_dependency_error() {
  printf 'Error: apt-get or dnf was not found.\n' >&2
  printf 'Install the Zephyr Linux host dependencies manually, then rerun this script.\n' >&2
  printf '\nDebian/Ubuntu package set:\n  %s\n' "${APT_PACKAGES[*]}" >&2
  printf '\nFedora package set:\n  %s\n' "${DNF_PACKAGES[*]}" >&2
  printf '\nFedora note: gcc-multilib and g++-multilib have no direct dnf package equivalent.\n' >&2
}

# Installs Debian/Ubuntu Zephyr host dependencies.
# 安装 Debian/Ubuntu 的 Zephyr 主机依赖。
install_apt_packages() {
  print_shell_command sudo apt-get update
  sudo apt-get update

  print_shell_command sudo apt-get install -y "${APT_PACKAGES[@]}"
  sudo apt-get install -y "${APT_PACKAGES[@]}"
}

# Installs Fedora Zephyr host dependencies.
# 安装 Fedora 的 Zephyr 主机依赖。
install_dnf_packages() {
  printf 'Fedora note: gcc-multilib and g++-multilib have no direct dnf package equivalent; continuing with Fedora equivalents.\n'
  print_shell_command sudo dnf install -y "${DNF_PACKAGES[@]}"
  sudo dnf install -y "${DNF_PACKAGES[@]}"
}

# Installs Zephyr Linux host dependencies with the detected package manager.
# 使用检测到的包管理器安装 Zephyr Linux 主机依赖。
install_linux_packages() {
  local package_manager

  command_exists sudo || fail "sudo was not found. Install sudo or run on a supported Linux system with sudo available."

  if ! package_manager="$(detect_package_manager)"; then
    print_manual_dependency_error
    exit 1
  fi

  case "$package_manager" in
    apt-get)
      install_apt_packages
      ;;
    dnf)
      install_dnf_packages
      ;;
    *)
      fail "Unsupported package manager: $package_manager"
      ;;
  esac
}

# Returns success when the current user already belongs to a group.
# 当前用户已经属于指定用户组时返回成功。
current_user_in_group() {
  local group=$1
  local current_user="${USER:-$(id -un)}"

  id -nG "$current_user" | tr ' ' '\n' | grep -Fxq "$group"
}

# Adds the current user to a Linux device-access group when needed.
# 按需把当前用户加入 Linux 设备访问用户组。
ensure_user_group_membership() {
  local group=$1
  local required=$2
  local current_user="${USER:-$(id -un)}"

  if ! getent group "$group" >/dev/null 2>&1; then
    if [[ "$required" == "required" ]]; then
      fail "Linux group '$group' was not found; serial device access cannot be configured automatically."
    fi

    printf 'Linux group %s does not exist; skipping.\n' "$group"
    return
  fi

  if current_user_in_group "$group"; then
    printf 'User %s is already in group %s.\n' "$current_user" "$group"
    return
  fi

  print_shell_command sudo usermod -aG "$group" "$current_user"
  sudo usermod -aG "$group" "$current_user"
}

# Adds a udev rule candidate once.
# 添加一个不重复的 udev 规则候选文件。
add_udev_rule_candidate() {
  local candidate=$1
  local existing

  [[ -f "$candidate" ]] || return

  for existing in "${UDEV_RULE_CANDIDATES[@]}"; do
    [[ "$existing" == "$candidate" ]] && return
  done

  UDEV_RULE_CANDIDATES+=("$candidate")
}

# Collects Zephyr SDK and OpenOCD udev rule files when they are present.
# 在文件存在时收集 Zephyr SDK 和 OpenOCD 的 udev 规则文件。
collect_udev_rule_candidates() {
  local sdk_dir
  local rule_file

  UDEV_RULE_CANDIDATES=()

  for sdk_dir in "$HOME"/zephyr-sdk-*; do
    [[ -d "$sdk_dir" ]] || continue

    while IFS= read -r -d '' rule_file; do
      add_udev_rule_candidate "$rule_file"
    done < <(find "$sdk_dir" -type f -name '*.rules' -print0)
  done

  add_udev_rule_candidate "/usr/share/openocd/contrib/60-openocd.rules"
  add_udev_rule_candidate "/usr/local/share/openocd/contrib/60-openocd.rules"
  add_udev_rule_candidate "/opt/openocd/share/openocd/contrib/60-openocd.rules"
}

# Installs available udev rules for non-root USB flash and debug access.
# 安装可用的 udev 规则，让普通用户可以访问 USB 烧录和调试设备。
install_udev_rules() {
  local rule_file
  local rule_name
  local target_path
  local copied_rules=0

  collect_udev_rule_candidates

  if ((${#UDEV_RULE_CANDIDATES[@]} == 0)); then
    printf 'No Zephyr SDK or OpenOCD udev rule files were found yet.\n'
    printf 'If this is a fresh SDK install, rerun this script after the SDK is present to install udev rules.\n'
    return
  fi

  for rule_file in "${UDEV_RULE_CANDIDATES[@]}"; do
    rule_name="$(basename "$rule_file")"
    target_path="/etc/udev/rules.d/$rule_name"

    if [[ -e "$target_path" ]]; then
      printf 'udev rule %s is already installed; skipping.\n' "$target_path"
      continue
    fi

    print_shell_command sudo cp "$rule_file" "$target_path"
    sudo cp "$rule_file" "$target_path"
    copied_rules=1
  done

  if ((copied_rules == 0)); then
    printf 'All discovered udev rules are already installed; skipping udev reload.\n'
    return
  fi

  printf 'Running: sudo udevadm control --reload-rules && sudo udevadm trigger\n'
  sudo udevadm control --reload-rules
  sudo udevadm trigger
}

# Configures Linux groups and udev rules for serial, flash, and debug access.
# 配置 Linux 用户组和 udev 规则，用于串口、烧录和调试访问。
install_linux_device_access() {
  ensure_user_group_membership "dialout" "required"
  ensure_user_group_membership "plugdev" "optional"
  install_udev_rules

  printf '\nDevice access note: group changes require logging out and back in, or rebooting, before existing shells can access serial devices.\n'
}

# Installs Linux system dependencies before the shared Zephyr setup flow.
# 在共享 Zephyr 安装流程前，安装 Linux 系统依赖。
install_system_dependencies() {
  install_linux_packages
  install_linux_device_access
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  run_setup_flow "$@"
fi
