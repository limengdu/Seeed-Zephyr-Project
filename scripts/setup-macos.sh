#!/usr/bin/env bash
#
# Purpose:
#   Set up a macOS Apple Silicon machine for a buildable Seeed Zephyr Base
#   Zephyr workspace using the steps validated for this repository.
#
# Usage:
#   bash scripts/setup-macos.sh
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

VENV_DIR="$ZEPHYR_WORKSPACE/.venv"
WEST="$VENV_DIR/bin/west"
PYTHON_BIN="${PYTHON_BIN:-python3}"
BREW_PACKAGES=(
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

CURRENT_STEP="startup"

fail() {
  printf 'Error: %s\n' "$*" >&2
  exit 1
}

on_error() {
  local exit_code=$?
  printf '\nSetup failed during: %s\n' "$CURRENT_STEP" >&2
  printf 'The command exited with status %s. Fix the message above, then rerun this script.\n' "$exit_code" >&2
  exit "$exit_code"
}

trap on_error ERR

step() {
  CURRENT_STEP="$2"
  printf '\n[%s] %s\n' "$1" "$2"
}

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

version_at_least() {
  local actual=$1
  local required=$2

  "$PYTHON_BIN" - "$actual" "$required" <<'PY'
import sys


def parse(version):
    return tuple(int(part) for part in version.split(".")[:3])


sys.exit(0 if parse(sys.argv[1]) >= parse(sys.argv[2]) else 1)
PY
}

install_brew_packages() {
  local missing_packages=()
  local package

  for package in "${BREW_PACKAGES[@]}"; do
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

ensure_python_version() {
  local python_version

  command_exists "$PYTHON_BIN" || fail "Python 3 was not found. Install Homebrew python3, then rerun this script."

  python_version="$("$PYTHON_BIN" -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')"
  version_at_least "$python_version" "3.12.0" || fail "Python >= 3.12 is required. Found $python_version from $PYTHON_BIN."

  printf 'Using Python %s from %s.\n' "$python_version" "$(command -v "$PYTHON_BIN")"
}

ensure_venv_and_west() {
  local python_version

  mkdir -p "$ZEPHYR_WORKSPACE"

  if [[ -d "$VENV_DIR" ]]; then
    printf 'Python venv already exists at %s.\n' "$VENV_DIR"
  else
    printf 'Creating Python venv at %s.\n' "$VENV_DIR"
    "$PYTHON_BIN" -m venv "$VENV_DIR"
  fi

  # Always activate the venv before west calls.
  # 在调用 west 之前，始终先激活虚拟环境。
  # shellcheck source=/dev/null
  source "$VENV_DIR/bin/activate"

  python_version="$(python -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')"
  version_at_least "$python_version" "3.12.0" || fail "The venv Python must be >= 3.12. Found $python_version in $VENV_DIR."

  python -m pip install --upgrade pip

  if "$WEST" --version >/dev/null 2>&1; then
    printf 'west is already installed in the venv: %s\n' "$("$WEST" --version)"
  else
    printf 'Installing west into the venv.\n'
    python -m pip install west
  fi
}

ensure_workspace() {
  # TODO(mirrors): Add optional regional mirror configuration after mirror policy is validated.
  if [[ -d "$ZEPHYR_WORKSPACE/.west" ]]; then
    printf 'West workspace is already initialized at %s.\n' "$ZEPHYR_WORKSPACE"
  else
    printf 'Initializing west workspace at %s with Zephyr %s.\n' "$ZEPHYR_WORKSPACE" "$ZEPHYR_VERSION"
    "$WEST" init "$ZEPHYR_WORKSPACE" --mr "$ZEPHYR_VERSION"
  fi

  (
    cd "$ZEPHYR_WORKSPACE"
    "$WEST" update
  )
}

zephyr_sdk_present() {
  local sdk_dir

  if [[ -n "${ZEPHYR_SDK_INSTALL_DIR:-}" && -d "$ZEPHYR_SDK_INSTALL_DIR" ]]; then
    return 0
  fi

  for sdk_dir in "$HOME"/zephyr-sdk-*; do
    [[ -d "$sdk_dir" ]] && return 0
  done

  return 1
}

install_zephyr_tools() {
  (
    cd "$ZEPHYR_WORKSPACE"
    "$WEST" zephyr-export
    "$WEST" packages pip --install

    if zephyr_sdk_present; then
      printf 'Zephyr SDK is already present; skipping west sdk install.\n'
    else
      "$WEST" sdk install
    fi
  )
}

fetch_espressif_blobs() {
  (
    cd "$ZEPHYR_WORKSPACE"
    "$WEST" blobs fetch hal_espressif
  )
}

main() {
  step "1/5" "Installing build tools..."
  command_exists brew || fail "Homebrew was not found. Install Homebrew from https://brew.sh/, then rerun this script."
  install_brew_packages

  step "2/5" "Creating Python venv and installing west..."
  ensure_python_version
  ensure_venv_and_west

  step "3/5" "Initializing and updating the Zephyr workspace..."
  ensure_workspace

  step "4/5" "Exporting Zephyr, installing Python packages, and checking the SDK..."
  install_zephyr_tools

  step "5/5" "Fetching Espressif blobs..."
  fetch_espressif_blobs

  printf '\nSetup complete.\n'
  printf 'Next step:\n'
  printf '  cd %s\n' "$ZEPHYR_WORKSPACE/zephyr"
  printf '  west build -p always -b xiao_esp32c6/esp32c6/hpcore samples/basic/blinky\n'
  printf '\nMulti-core boards require the fully-qualified target, such as xiao_esp32c6/esp32c6/hpcore.\n'
}

main "$@"
