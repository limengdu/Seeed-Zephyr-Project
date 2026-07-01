<#
Purpose:
  Guide uninstalling Seeed Zephyr Base on Windows. The seeed-zephyr CLI and the
  Zephyr workspace live inside WSL2, so their removal runs there. WSL2 and
  usbipd-win are shared Windows components, so this script only lists how to
  remove them rather than removing them for you.

Usage:
  powershell -ExecutionPolicy Bypass -File scripts/uninstall-windows.ps1
#>

Set-StrictMode -Version 2.0
$ErrorActionPreference = "Stop"

Write-Host "Seeed Zephyr Base Windows uninstaller"
Write-Host ""
Write-Host "The seeed-zephyr CLI and the Zephyr workspace were installed inside WSL2."
Write-Host "Remove them from inside your WSL2 distro:"
Write-Host "  bash scripts/uninstall-linux.sh"
Write-Host ""
Write-Host "WSL2 and usbipd-win are shared Windows components, so this uninstaller keeps them."
Write-Host "If you no longer need them, remove them yourself:"
Write-Host ""
Write-Host "  Remove usbipd-win:"
Write-Host "    winget uninstall --exact --id dorssel.usbipd-win"
Write-Host ""
Write-Host "  Remove a specific WSL distro (this deletes that distro and its files):"
Write-Host "    wsl --list --verbose"
Write-Host "    wsl --unregister <DistroName>"
Write-Host ""
Write-Host "  Remove the WSL feature itself:"
Write-Host "    wsl --uninstall"
