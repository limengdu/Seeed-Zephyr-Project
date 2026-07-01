#!/usr/bin/env bash
# Uninstaller for the seeed-zephyr CLI and Zephyr development environment.
#
# Usage:
#   bash uninstall.sh [--yes] [--dry-run]
#
# Removes the seeed-zephyr CLI command, and asks before removing the Zephyr
# workspace and SDK. Shared system build tools are listed, not removed.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

case "$(uname -s)" in
    Darwin)
        bash "$SCRIPT_DIR/scripts/uninstall-macos.sh" "$@"
        ;;
    Linux)
        bash "$SCRIPT_DIR/scripts/uninstall-linux.sh" "$@"
        ;;
    MINGW* | MSYS* | CYGWIN*)
        echo "On Windows, run: powershell -ExecutionPolicy Bypass -File scripts/uninstall-windows.ps1"
        echo "It guides removal from inside WSL2."
        exit 1
        ;;
    *)
        echo "Automatic uninstall is available for macOS and Linux."
        echo "For Windows, see scripts/uninstall-windows.ps1."
        exit 1
        ;;
esac
