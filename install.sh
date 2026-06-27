#!/usr/bin/env bash
# One-line installer for seeed-zephyr CLI + Zephyr development environment.
# Usage: curl -fsSL https://raw.githubusercontent.com/Seeed-Projects/seeed-zephyr-base/main/install.sh | bash
set -euo pipefail

INSTALL_DIR="${SEEED_ZEPHYR_DIR:-$HOME/.seeed-zephyr-base}"
REPO_URL="https://github.com/Seeed-Projects/seeed-zephyr-base.git"

echo "=== seeed-zephyr installer ==="
echo "Install directory: $INSTALL_DIR"
echo ""

# Clone or update the repository
if [[ -d "$INSTALL_DIR/.git" ]]; then
    echo "Updating existing installation..."
    git -C "$INSTALL_DIR" pull --no-ff
else
    echo "Cloning seeed-zephyr-base..."
    git clone "$REPO_URL" "$INSTALL_DIR"
fi

echo ""

# Run the platform-specific setup script
case "$(uname -s)" in
    Darwin)
        echo "Detected macOS. Running setup..."
        bash "$INSTALL_DIR/scripts/setup-macos.sh" "$@"
        ;;
    Linux)
        echo "Detected Linux. Running setup..."
        bash "$INSTALL_DIR/scripts/setup-linux.sh" "$@"
        ;;
    *)
        echo "Automatic setup is available for macOS and Linux."
        echo "For Windows, use WSL2 with the Linux setup script."
        echo "See: $INSTALL_DIR/scripts/setup-windows.ps1"
        exit 1
        ;;
esac
