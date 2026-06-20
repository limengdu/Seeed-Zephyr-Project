<#
Purpose:
  Prepare Windows for Seeed Zephyr Base by setting up WSL2 and usbipd-win.
  The actual Zephyr setup must run inside WSL2 with scripts/setup-linux.sh.

Usage:
  powershell -ExecutionPolicy Bypass -File scripts/setup-windows.ps1

Prerequisites:
  - Windows 10 2004+ or Windows 11.
  - Administrator rights for WSL and usbipd-win installation steps.
  - winget available when usbipd-win needs to be installed.

NOT YET VERIFIED ON REAL WINDOWS:
  This script was written on macOS and cannot be run or verified on Windows here.
  It still needs validation on a real Windows 10 2004+ or Windows 11 machine.

What this does NOT do:
  - It does not reimplement the Zephyr setup flow.
  - It does not install macOS or Linux native tooling directly on Windows.
  - It does not run scripts/setup-linux.sh for you.
  - It does not automatically choose or attach a XIAO USB device.
#>

Set-StrictMode -Version 2.0
$ErrorActionPreference = "Stop"

$script:NeedsFollowUp = $false

# Returns true when the current PowerShell host is running on Windows.
function Test-WindowsHost {
    $isWindowsVariable = Get-Variable -Name IsWindows -ErrorAction SilentlyContinue

    if ($null -ne $isWindowsVariable) {
        return [bool]$isWindowsVariable.Value
    }

    return $env:OS -eq "Windows_NT"
}

# Returns true when PowerShell is running with Administrator rights.
function Test-IsAdministrator {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal -ArgumentList $identity

    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Prints a command line before running or recommending it.
function Write-CommandLine {
    param(
        [Parameter(Mandatory = $true)]
        [string]$DisplayCommand
    )

    Write-Host ("  {0}" -f $DisplayCommand)
}

# Runs an external command and streams output to the console.
function Invoke-StreamingCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FilePath,

        [Parameter(Mandatory = $true)]
        [string]$DisplayCommand,

        [string[]]$Arguments = @()
    )

    Write-Host "Running:"
    Write-CommandLine -DisplayCommand $DisplayCommand

    & $FilePath @Arguments
    $exitCode = $LASTEXITCODE

    if ($exitCode -ne 0) {
        throw "Command failed with exit code ${exitCode}: ${DisplayCommand}"
    }
}

# Runs an external command and returns its exit code and captured output.
function Invoke-CapturedCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FilePath,

        [Parameter(Mandatory = $true)]
        [string]$DisplayCommand,

        [string[]]$Arguments = @()
    )

    Write-Host "Checking:"
    Write-CommandLine -DisplayCommand $DisplayCommand

    try {
        $output = & $FilePath @Arguments 2>&1
        $exitCode = $LASTEXITCODE
    }
    catch {
        $output = @($_.Exception.Message)
        $exitCode = 1
    }

    return [pscustomobject]@{
        ExitCode = $exitCode
        Output = @($output | ForEach-Object { $_.ToString() })
    }
}

# Parses wsl --status output for the default distro and default WSL version.
function Get-WslStatus {
    param(
        [Parameter(Mandatory = $true)]
        [string]$WslPath
    )

    $result = Invoke-CapturedCommand `
        -FilePath $WslPath `
        -DisplayCommand "wsl --status" `
        -Arguments @("--status")

    $defaultDistro = $null
    $defaultVersion = $null

    foreach ($rawLine in $result.Output) {
        $line = ($rawLine -replace "`0", "").Trim()

        if ($line -match "^Default Distribution:\s*(.+)$") {
            $defaultDistro = $Matches[1].Trim()
        }
        elseif ($line -match "^Default Version:\s*([0-9]+)$") {
            $defaultVersion = [int]$Matches[1]
        }
    }

    return [pscustomobject]@{
        ExitCode = $result.ExitCode
        Output = $result.Output
        DefaultDistro = $defaultDistro
        DefaultVersion = $defaultVersion
    }
}

# Parses wsl -l -v output into distro records.
function Get-WslDistros {
    param(
        [Parameter(Mandatory = $true)]
        [string]$WslPath
    )

    $result = Invoke-CapturedCommand `
        -FilePath $WslPath `
        -DisplayCommand "wsl -l -v" `
        -Arguments @("-l", "-v")

    $distros = @()

    foreach ($rawLine in $result.Output) {
        $line = ($rawLine -replace "`0", "").Trim()
        $isDefault = $line.StartsWith("*")
        $line = $line.TrimStart([char]"*").Trim()

        if ([string]::IsNullOrWhiteSpace($line)) {
            continue
        }

        if ($line -match "^NAME\s+STATE\s+VERSION$") {
            continue
        }

        if ($line -match "no installed distributions") {
            continue
        }

        if ($line -match "^(?<Name>.+?)\s+(?<State>Running|Stopped|Installing|Uninstalling)\s+(?<Version>[0-9]+)$") {
            $distros += [pscustomobject]@{
                Name = $Matches["Name"].Trim()
                State = $Matches["State"].Trim()
                Version = [int]$Matches["Version"]
                IsDefault = $isDefault
            }
        }
    }

    return $distros
}

# Ensures WSL exists and reports whether the default distro is already WSL2.
function Ensure-Wsl2 {
    param(
        [Parameter(Mandatory = $true)]
        [bool]$IsAdministrator
    )

    Write-Host ""
    Write-Host "WSL2 check"

    $wslCommand = Get-Command "wsl.exe" -ErrorAction SilentlyContinue

    if ($null -eq $wslCommand) {
        Write-Warning "wsl was not found. Install WSL from an Administrator PowerShell, then reboot if Windows asks for it:"
        Write-CommandLine -DisplayCommand "wsl --install"
        $script:NeedsFollowUp = $true
        return $false
    }

    $status = Get-WslStatus -WslPath $wslCommand.Source
    $distros = @(Get-WslDistros -WslPath $wslCommand.Source)

    if ($status.ExitCode -ne 0) {
        Write-Warning "wsl --status returned a non-zero exit code. The output above may explain the required Windows feature or reboot step."
    }

    if ($null -ne $status.DefaultVersion -and $status.DefaultVersion -ne 2) {
        Write-Warning "The default WSL version is $($status.DefaultVersion), not 2. New distros should default to WSL2."
        Invoke-StreamingCommand `
            -FilePath $wslCommand.Source `
            -DisplayCommand "wsl --set-default-version 2" `
            -Arguments @("--set-default-version", "2")
    }

    if ($distros.Count -eq 0) {
        if ($IsAdministrator) {
            Write-Warning "No WSL distro was found. Starting WSL installation. This may require a reboot."
            Invoke-StreamingCommand `
                -FilePath $wslCommand.Source `
                -DisplayCommand "wsl --install" `
                -Arguments @("--install")
        }
        else {
            Write-Warning "No WSL distro was found. Run this from an Administrator PowerShell, then reboot if Windows asks for it:"
            Write-CommandLine -DisplayCommand "wsl --install"
        }

        $script:NeedsFollowUp = $true
        return $false
    }

    $defaultDistro = $distros | Where-Object { $_.IsDefault } | Select-Object -First 1

    if ($null -eq $defaultDistro -and -not [string]::IsNullOrWhiteSpace($status.DefaultDistro)) {
        $defaultDistro = $distros | Where-Object { $_.Name -eq $status.DefaultDistro } | Select-Object -First 1
    }

    if ($null -eq $defaultDistro) {
        $defaultDistro = $distros[0]
    }

    Write-Host ("Detected default WSL distro: {0} (state: {1}, version: {2})" -f $defaultDistro.Name, $defaultDistro.State, $defaultDistro.Version)

    $wsl2Distros = @($distros | Where-Object { $_.Version -eq 2 })

    if ($wsl2Distros.Count -eq 0) {
        Write-Warning "A WSL distro exists, but none are WSL2. Convert the distro you want to use:"
        Write-CommandLine -DisplayCommand ("wsl --set-version `"{0}`" 2" -f $defaultDistro.Name)
        $script:NeedsFollowUp = $true
        return $false
    }

    if ($defaultDistro.Version -ne 2) {
        Write-Warning "The detected default distro is not WSL2. Use a WSL2 distro for this project or convert the default distro:"
        Write-CommandLine -DisplayCommand ("wsl --set-version `"{0}`" 2" -f $defaultDistro.Name)
        $script:NeedsFollowUp = $true
        return $false
    }

    Write-Host "WSL2 is available and the detected default distro uses WSL2."
    return $true
}

# Ensures usbipd-win is available for forwarding USB devices into WSL2.
function Ensure-Usbipd {
    param(
        [Parameter(Mandatory = $true)]
        [bool]$IsAdministrator
    )

    Write-Host ""
    Write-Host "usbipd-win check"

    $usbipdCommand = Get-Command "usbipd" -ErrorAction SilentlyContinue

    if ($null -ne $usbipdCommand) {
        Write-Host ("usbipd is available: {0}" -f $usbipdCommand.Source)
        return $true
    }

    Write-Warning "usbipd was not found. usbipd-win is required to forward XIAO USB devices into WSL2."

    $wingetCommand = Get-Command "winget" -ErrorAction SilentlyContinue

    if ($null -eq $wingetCommand) {
        Write-Warning "winget was not found. Install App Installer from Microsoft Store, or install usbipd-win manually, then rerun this script."
        Write-Host "Expected winget command:"
        Write-CommandLine -DisplayCommand "winget install --exact --id dorssel.usbipd-win"
        $script:NeedsFollowUp = $true
        return $false
    }

    if (-not $IsAdministrator) {
        Write-Warning "usbipd-win installation needs Administrator rights. Run this from an Administrator PowerShell, or run:"
        Write-CommandLine -DisplayCommand "winget install --exact --id dorssel.usbipd-win"
        $script:NeedsFollowUp = $true
        return $false
    }

    Invoke-StreamingCommand `
        -FilePath $wingetCommand.Source `
        -DisplayCommand "winget install --exact --id dorssel.usbipd-win" `
        -Arguments @("install", "--exact", "--id", "dorssel.usbipd-win")

    $usbipdCommand = Get-Command "usbipd" -ErrorAction SilentlyContinue

    if ($null -eq $usbipdCommand) {
        Write-Warning "usbipd-win installation finished, but usbipd is not visible in this PowerShell session. Open a new PowerShell window and rerun this script."
        $script:NeedsFollowUp = $true
        return $false
    }

    Write-Host ("usbipd is available: {0}" -f $usbipdCommand.Source)
    return $true
}

# Prints the manual WSL2 and USB forwarding steps that remain per user and per device.
function Write-FinalGuidance {
    Write-Host ""
    Write-Host "Next steps"
    Write-Host ""
    Write-Host "Run the Linux setup inside WSL2:"
    Write-Host "  1. Open your WSL2 distro."
    Write-Host "  2. From the cloned Seeed Zephyr Base repo, run:"
    Write-Host "     bash scripts/setup-linux.sh [--board <board_id>]"
    Write-Host ""
    Write-Host "Forward the XIAO USB device into WSL2 with usbipd:"
    Write-Host "  1. In Windows PowerShell, list USB devices and find the XIAO BUSID:"
    Write-Host "     usbipd list"
    Write-Host "  2. Once per device, in an Administrator PowerShell:"
    Write-Host "     usbipd bind --busid <BUSID>"
    Write-Host "  3. Each time the board is plugged in, attach it to WSL2:"
    Write-Host "     usbipd attach --wsl --busid <BUSID>"
    Write-Host ""
    Write-Host "Without usbipd attach, WSL2 cannot see the XIAO USB device. west flash, west espressif monitor, and west debug can fail because the board is still owned by Windows."
}

Write-Host "Seeed Zephyr Base Windows setup preparer"
Write-Warning "NOT YET VERIFIED ON REAL WINDOWS. This script was written on macOS and still needs real Windows validation."

if (-not (Test-WindowsHost)) {
    throw "This script is intended for Windows 10 2004+ or Windows 11."
}

$isAdministrator = Test-IsAdministrator

if ($isAdministrator) {
    Write-Host "PowerShell is running with Administrator rights."
}
else {
    Write-Warning "PowerShell is not running with Administrator rights. WSL or usbipd-win installation steps may be printed instead of executed."
}

try {
    [void](Ensure-Wsl2 -IsAdministrator $isAdministrator)
}
catch {
    Write-Warning $_.Exception.Message
    $script:NeedsFollowUp = $true
}

try {
    [void](Ensure-Usbipd -IsAdministrator $isAdministrator)
}
catch {
    Write-Warning $_.Exception.Message
    $script:NeedsFollowUp = $true
}

Write-FinalGuidance

if ($script:NeedsFollowUp) {
    Write-Host ""
    Write-Warning "Some setup steps still require manual completion, a new PowerShell session, or a reboot. After that, rerun this script."
}
