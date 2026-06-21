#!/usr/bin/env bash
#
# Purpose:
#   Shared setup flow for Seeed Zephyr Base platform setup scripts.
#   Platform entrypoints provide system dependency installation, then call
#   run_setup_flow to execute the shared Zephyr workspace steps.

COMMON_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ -z "${SCRIPT_DIR:-}" ]]; then
  SCRIPT_DIR="$(cd "$COMMON_SCRIPT_DIR/.." && pwd)"
fi

if [[ -z "${REPO_ROOT:-}" ]]; then
  REPO_ROOT="$(cd "$COMMON_SCRIPT_DIR/../.." && pwd)"
fi

ZEPHYR_VERSION="${ZEPHYR_VERSION:-v4.4.0}"
ZEPHYR_WORKSPACE="${ZEPHYR_WORKSPACE:-$HOME/zephyrproject}"
SETUP_SCRIPT_NAME="${SETUP_SCRIPT_NAME:-scripts/setup-macos.sh}"
SETUP_PLATFORM_LABEL="${SETUP_PLATFORM_LABEL:-platform}"
PYTHON_INSTALL_HINT="${PYTHON_INSTALL_HINT:-Install Python 3.12 or newer, then rerun this script.}"
BOARD_METADATA_DIR="$REPO_ROOT/metadata/boards"
BUILD_MATRIX_RESULTS="$REPO_ROOT/tools/build_matrix/results.md"
BOARD_OVERRIDES_FILE="$REPO_ROOT/tools/build_matrix/board-overrides.tsv"
VENV_DIR="$ZEPHYR_WORKSPACE/.venv"
WEST="$VENV_DIR/bin/west"
PYTHON_BIN="${PYTHON_BIN:-python3}"
CLI_INSTALL_DIR="${SEEED_ZEPHYR_CLI_INSTALL_DIR:-}"

if ! declare -p CLI_INSTALL_DIR_CANDIDATES >/dev/null 2>&1; then
  CLI_INSTALL_DIR_CANDIDATES=("$HOME/.local/bin")
fi

CURRENT_STEP="startup"
BOARD_ID=""
BOARD_VENDOR=""
BOARD_HAL_MODULE=""
BOARD_BUILD_TARGET=""
BOARD_EXAMPLE_PATH=""
BOARD_BUILD_STATUS=""
CLI_COMMAND_PATH=""
CLI_INSTALL_STATUS="pending"
MG24_BOARD_ID="xiao_mg24"
MG24_PYOCD_TARGET="EFR32MG24B220F1536IM48"
PYOCD="$VENV_DIR/bin/pyocd"

# Prints an error message and exits the script.
# 打印错误信息并退出脚本。
fail() {
  printf 'Error: %s\n' "$*" >&2
  exit 1
}

# Reports which setup step failed when any command exits with an error.
# 当任一命令失败时，报告失败发生在哪个安装步骤。
on_error() {
  local exit_code=$?
  printf '\nSetup failed during: %s\n' "$CURRENT_STEP" >&2
  printf 'The command exited with status %s. Fix the message above, then rerun this script.\n' "$exit_code" >&2
  exit "$exit_code"
}

trap on_error ERR

# Records and prints the current high-level setup step.
# 记录并打印当前的高层安装步骤。
step() {
  CURRENT_STEP="$2"
  printf '\n[%s] %s\n' "$1" "$2"
}

# Returns success when the named command is available in PATH.
# 当指定命令存在于 PATH 中时返回成功。
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Returns success when a directory is present in PATH.
# 当目录已经位于 PATH 中时返回成功。
path_contains_dir() {
  local path_dir=$1

  case ":${PATH:-}:" in
    *":$path_dir:"*)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

# Prompts for a yes/no answer where Enter means yes.
# 询问 yes/no，其中直接回车代表 yes。
prompt_yes_default() {
  local prompt=$1
  local answer

  if [[ ! -t 0 ]]; then
    return 0
  fi

  while true; do
    read -r -p "$prompt [Y/n] " answer
    case "$answer" in
      "" | [Yy] | [Yy][Ee][Ss])
        return 0
        ;;
      [Nn] | [Nn][Oo])
        return 1
        ;;
      *)
        printf 'Please answer y or n.\n'
        ;;
    esac
  done
}

# Selects a user-writable install directory for the global CLI command.
# 选择一个用户可写的全局 CLI 命令安装目录。
select_cli_install_dir() {
  local candidate

  if [[ -n "$CLI_INSTALL_DIR" ]]; then
    printf '%s\n' "$CLI_INSTALL_DIR"
    return
  fi

  for candidate in "${CLI_INSTALL_DIR_CANDIDATES[@]}"; do
    if path_contains_dir "$candidate"; then
      if [[ ! -e "$candidate" || ( -d "$candidate" && -w "$candidate" ) ]]; then
        printf '%s\n' "$candidate"
        return
      fi
    fi
  done

  printf '%s\n' "$HOME/.local/bin"
}

# Installs the seeed-zephyr command as a user-level symlink.
# 以用户级符号链接安装 seeed-zephyr 命令。
install_cli_command() {
  local install_dir
  local command_path
  local source_path="$REPO_ROOT/scripts/seeed-zephyr"

  install_dir="$(select_cli_install_dir)"
  command_path="$install_dir/seeed-zephyr"

  mkdir -p "$install_dir"

  if [[ -e "$command_path" && ! -L "$command_path" ]]; then
    fail "$command_path already exists and is not a symlink. Move it before installing the CLI."
  fi

  ln -sfn "$source_path" "$command_path"

  CLI_COMMAND_PATH="$command_path"
  CLI_INSTALL_STATUS="installed"

  printf 'Installed seeed-zephyr CLI at %s.\n' "$command_path"

  if path_contains_dir "$install_dir"; then
    printf 'You can run seeed-zephyr from any directory.\n'
  else
    printf 'Add this directory to PATH to run seeed-zephyr from any directory:\n'
    printf '  export PATH="%s:$PATH"\n' "$install_dir"
    printf 'Until PATH is updated, run the CLI with:\n'
    printf '  %s --help\n' "$command_path"
  fi
}

# Asks whether to install the CLI and defaults to installation.
# 询问是否安装 CLI，并默认执行安装。
install_cli_if_requested() {
  if prompt_yes_default "Install seeed-zephyr CLI?"; then
    install_cli_command
  else
    CLI_INSTALL_STATUS="skipped"
    printf 'Skipped seeed-zephyr CLI installation.\n'
  fi
}

# Returns the command users should run after setup completes.
# 返回安装完成后用户应运行的命令。
next_cli_command() {
  local install_dir

  if [[ "$CLI_INSTALL_STATUS" == "installed" && -n "$CLI_COMMAND_PATH" ]]; then
    install_dir="$(dirname "$CLI_COMMAND_PATH")"
    if path_contains_dir "$install_dir"; then
      printf 'seeed-zephyr\n'
    else
      printf '%s\n' "$CLI_COMMAND_PATH"
    fi
  else
    printf 'scripts/seeed-zephyr\n'
  fi
}

# Compares two dotted version strings using the configured Python binary.
# 使用配置的 Python 可执行文件比较两个点分版本号。
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

# Lists board ids from metadata/boards/*.yaml, one id per line.
# 从 metadata/boards/*.yaml 列出开发板 id，每行一个。
list_available_board_ids() {
  find "$BOARD_METADATA_DIR" -maxdepth 1 -type f -name '*.yaml' -exec basename {} .yaml \; | sort
}

# Prints the available board ids for help and validation errors.
# 打印可用开发板 id，用于帮助信息和校验错误。
print_available_board_ids() {
  printf 'Available board ids:\n'
  list_available_board_ids | sed 's/^/  - /'
}

# Parses command-line arguments into global setup options.
# 解析命令行参数并写入全局安装选项。
parse_args() {
  while (($# > 0)); do
    case "$1" in
      --board)
        (($# >= 2)) || fail "--board requires a board id."
        BOARD_ID="$2"
        shift 2
        ;;
      -h | --help)
        printf 'Usage: bash %s [--board <board_id>]\n\n' "$SETUP_SCRIPT_NAME"
        print_available_board_ids
        exit 0
        ;;
      *)
        fail "Unknown argument: $1"
        ;;
    esac
  done
}

# Reads a flat YAML scalar value from a board metadata file.
# 从开发板 metadata 文件读取一个扁平 YAML 标量值。
read_board_metadata_value() {
  local board_file=$1
  local key=$2

  sed -n "s/^[[:space:]]*$key:[[:space:]]*//p" "$board_file" | head -n 1
}

# Maps the board vendor name to the corresponding Zephyr HAL module.
# 将开发板厂商名称映射到对应的 Zephyr HAL 模块。
vendor_to_hal_module() {
  local vendor=$1

  case "$vendor" in
    espressif)
      printf 'hal_espressif\n'
      ;;
    nordic)
      printf 'hal_nordic\n'
      ;;
    renesas)
      printf 'hal_renesas\n'
      ;;
    silabs)
      printf 'hal_silabs\n'
      ;;
    raspberrypi)
      printf 'hal_rpi_pico\n'
      ;;
    microchip)
      printf 'hal_atmel\n'
      ;;
    *)
      return 1
      ;;
  esac
}

# Returns a Markdown table cell from the latest build matrix results.
# 从最新构建矩阵结果中读取一个 Markdown 表格单元格。
read_build_matrix_cell() {
  local board_id=$1
  local column_index=$2

  [[ -f "$BUILD_MATRIX_RESULTS" ]] || return 1

  awk -F'|' -v board_id="$board_id" -v column_index="$column_index" '
    $2 ~ "^[[:space:]]*" board_id "[[:space:]]*$" {
      value = $column_index
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", value)
      gsub(/`/, "", value)
      print value
      found = 1
      exit
    }
    END {
      if (!found) {
        exit 1
      }
    }
  ' "$BUILD_MATRIX_RESULTS"
}

# Returns the best known Zephyr build target for the selected board.
# 返回所选开发板目前最可靠的 Zephyr 构建 target。
resolve_build_target_hint() {
  local board_id=$1
  local fallback_target=$2
  local matrix_target

  if matrix_target="$(read_build_matrix_cell "$board_id" 5)" && [[ -n "$matrix_target" ]]; then
    printf '%s\n' "$matrix_target"
  else
    printf '%s\n' "$fallback_target"
  fi
}

# Returns the baseline repository example path for the selected board.
# 返回所选开发板的基线仓库示例路径。
resolve_example_path_hint() {
  local board_id=$1
  local fallback_example="examples/boards/$board_id/blinky"
  local override_example

  if [[ -f "$BOARD_OVERRIDES_FILE" ]]; then
    if override_example="$(
      awk -F '\t' -v board_id="$board_id" '
        $0 ~ /^[[:space:]]*#/ || $0 ~ /^[[:space:]]*$/ {
          next
        }
        $1 == board_id {
          print $3
          found = 1
          exit
        }
        END {
          if (!found) {
            exit 1
          }
        }
      ' "$BOARD_OVERRIDES_FILE"
    )" && [[ -n "$override_example" ]]; then
      printf '%s\n' "$override_example"
      return
    fi
  fi

  printf '%s\n' "$fallback_example"
}

# Returns the latest build status for the selected board when available.
# 在可用时返回所选开发板的最新构建状态。
resolve_build_status_hint() {
  local board_id=$1
  local matrix_status

  if matrix_status="$(read_build_matrix_cell "$board_id" 6)" && [[ -n "$matrix_status" ]]; then
    printf '%s\n' "$matrix_status"
  fi
}

# Resolves board metadata into vendor, HAL module, and build target globals.
# 将开发板 metadata 解析为厂商、HAL 模块和构建 target 全局变量。
resolve_board_metadata() {
  local board_id=$1
  local board_file="$BOARD_METADATA_DIR/$board_id.yaml"
  local metadata_target

  BOARD_ID="$board_id"

  if [[ ! -f "$board_file" ]]; then
    printf 'Error: board metadata was not found for "%s".\n' "$board_id" >&2
    print_available_board_ids >&2
    exit 1
  fi

  BOARD_VENDOR="$(read_board_metadata_value "$board_file" "vendor")"
  [[ -n "$BOARD_VENDOR" ]] || fail "Board $board_id does not define a vendor."

  metadata_target="$(read_board_metadata_value "$board_file" "zephyr_target")"
  [[ -n "$metadata_target" ]] || fail "Board $board_id does not define a zephyr_target."
  BOARD_BUILD_TARGET="$(resolve_build_target_hint "$board_id" "$metadata_target")"
  BOARD_EXAMPLE_PATH="$(resolve_example_path_hint "$board_id")"
  BOARD_BUILD_STATUS="$(resolve_build_status_hint "$board_id")"

  if BOARD_HAL_MODULE="$(vendor_to_hal_module "$BOARD_VENDOR")"; then
    return 0
  fi

  BOARD_HAL_MODULE=""
  return 0
}

# Checks whether a Zephyr HAL module reports any binary blobs.
# 检查 Zephyr HAL 模块是否报告了任何二进制 blobs。
module_has_blobs() {
  local module=$1
  local blobs_output

  blobs_output="$(
    cd "$ZEPHYR_WORKSPACE"
    "$WEST" blobs list "$module"
  )"

  [[ -n "$(printf '%s\n' "$blobs_output" | sed '/^[[:space:]]*$/d')" ]]
}

# Fetches board-specific blobs only when the resolved HAL module has blobs.
# 仅在解析出的 HAL 模块确实包含 blobs 时，获取开发板专属 blobs。
fetch_board_blobs() {
  if [[ -z "$BOARD_HAL_MODULE" ]]; then
    printf 'Board %s uses vendor %s, which has no mapped Zephyr HAL module; skipping blobs.\n' "$BOARD_ID" "$BOARD_VENDOR"
    return
  fi

  if module_has_blobs "$BOARD_HAL_MODULE"; then
    (
      cd "$ZEPHYR_WORKSPACE"
      "$WEST" blobs fetch "$BOARD_HAL_MODULE"
    )
  else
    printf 'Board %s (vendor %s, module %s) needs no blobs; skipping.\n' "$BOARD_ID" "$BOARD_VENDOR" "$BOARD_HAL_MODULE"
  fi
}

# Verifies that the configured Python binary meets Zephyr's minimum version.
# 确认配置的 Python 可执行文件满足 Zephyr 的最低版本要求。
ensure_python_version() {
  local python_version

  command_exists "$PYTHON_BIN" || fail "Python 3 was not found. $PYTHON_INSTALL_HINT"

  python_version="$("$PYTHON_BIN" -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')"
  version_at_least "$python_version" "3.12.0" || fail "Python >= 3.12 is required. Found $python_version from $PYTHON_BIN."

  printf 'Using Python %s from %s.\n' "$python_version" "$(command -v "$PYTHON_BIN")"
}

# Creates the Python venv when needed and ensures west is installed in it.
# 按需创建 Python 虚拟环境，并确保其中已安装 west。
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

# Initializes or updates the Zephyr west workspace at the configured version.
# 按配置版本初始化或更新 Zephyr west 工作区。
ensure_workspace() {
  # TODO(mirrors): Add optional regional mirror configuration after mirror policy is validated.
  # TODO(mirrors): 在镜像策略验证后，添加可选的区域镜像配置。
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

# Returns success when a Zephyr SDK installation is already visible locally.
# 当本机已经能找到 Zephyr SDK 安装目录时返回成功。
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

# Exports Zephyr CMake packages, installs Python packages, and installs the SDK.
# 导出 Zephyr CMake 包、安装 Python 包，并安装 SDK。
install_zephyr_tools() {
  (
    cd "$ZEPHYR_WORKSPACE"
    "$WEST" zephyr-export
    "$WEST" packages pip --install

    # Zephyr SDK ships OpenOCD in hosttools; west flash uses that SDK-provided OpenOCD.
    # Zephyr SDK 在 hosttools 内自带 OpenOCD；west flash 会使用 SDK 提供的 OpenOCD。
    if zephyr_sdk_present; then
      printf 'Zephyr SDK is already present; skipping west sdk install.\n'
    else
      "$WEST" sdk install
    fi
  )
}

# Confirms Zephyr's Espressif flash and monitor tools are available.
# 确认 Zephyr 自带的 Espressif 烧录和 monitor 工具可用。
check_espressif_zephyr_tools() {
  local monitor_file="$ZEPHYR_WORKSPACE/modules/hal/espressif/tools/idf_monitor/idf_monitor.py"

  [[ -f "$monitor_file" ]] || fail "Zephyr hal_espressif monitor was not found: $monitor_file"
  [[ -x "$VENV_DIR/bin/esptool" ]] || fail "esptool was not found in the Zephyr venv. Rerun this setup script so Zephyr Python packages are installed."

  printf 'Zephyr Espressif flash and monitor tools are available.\n'
}

# Prints the platform-specific BOSSA install hint.
# 打印当前平台对应的 BOSSA 安装提示。
bossac_install_hint() {
  case "$SETUP_PLATFORM_LABEL" in
    macOS)
      printf 'Install it with: brew install bossa'
      ;;
    Linux)
      printf 'Install it with: sudo apt-get install bossa-cli, or sudo dnf install bossa'
      ;;
    *)
      printf 'Install BOSSA/bossac for this platform, or run scripts/setup-linux.sh inside WSL2'
      ;;
  esac
}

# Confirms the BOSSA command used by the Seeeduino XIAO SAMD21 runner is available.
# 确认 Seeeduino XIAO SAMD21 runner 使用的 BOSSA 命令可用。
check_bossac_tool() {
  command_exists bossac || fail "bossac was not found. $(bossac_install_hint)."
  printf 'BOSSA bossac flash tool is available.\n'
}

# Prints the platform-specific dfu-util install hint.
# 打印当前平台对应的 dfu-util 安装提示。
dfu_util_install_hint() {
  case "$SETUP_PLATFORM_LABEL" in
    macOS)
      printf 'Install it with: brew install dfu-util'
      ;;
    Linux)
      printf 'Install it with: sudo apt-get install dfu-util, or sudo dnf install dfu-util'
      ;;
    *)
      printf 'Install dfu-util for this platform, or run scripts/setup-linux.sh inside WSL2'
      ;;
  esac
}

# Confirms the dfu-util command used by XIAO RA4M1 USB DFU flashing is available.
# 确认 XIAO RA4M1 USB DFU 烧录使用的 dfu-util 命令可用。
check_dfu_util_tool() {
  command_exists dfu-util || fail "dfu-util was not found. $(dfu_util_install_hint)."
  printf 'dfu-util flash tool is available.\n'
}

# Returns success when pyOCD can see the installed MG24 target.
# 当 pyOCD 能看到已安装的 MG24 target 时返回成功。
pyocd_target_available() {
  local target=$1

  [[ -x "$PYOCD" ]] || return 1
  "$PYOCD" list --targets | grep -Fiq "$target"
}

# Installs the CMSIS pack required by Zephyr's XIAO MG24 pyOCD runner.
# 安装 Zephyr XIAO MG24 pyOCD runner 需要的 CMSIS pack。
ensure_mg24_pyocd_pack() {
  [[ -x "$PYOCD" ]] || fail "pyocd was not found in the Zephyr venv. Rerun setup so Zephyr Python packages are installed."

  if pyocd_target_available "$MG24_PYOCD_TARGET"; then
    printf 'pyOCD target %s is available.\n' "$MG24_PYOCD_TARGET"
    return
  fi

  printf 'Installing pyOCD CMSIS pack for XIAO MG24 target: %s\n' "$MG24_PYOCD_TARGET"
  "$PYOCD" pack install "$MG24_PYOCD_TARGET"

  pyocd_target_available "$MG24_PYOCD_TARGET" || fail "pyOCD target $MG24_PYOCD_TARGET is still unavailable after installing its CMSIS pack."
}

# Checks board-specific host tools after the Zephyr workspace is ready.
# 在 Zephyr 工作区准备好后，检查开发板专属主机工具。
check_board_host_tools() {
  if [[ "$BOARD_VENDOR" == "espressif" ]]; then
    check_espressif_zephyr_tools
  fi

  if [[ "$BOARD_BUILD_TARGET" == "seeeduino_xiao" ]]; then
    check_bossac_tool
  fi

  if [[ "$BOARD_ID" == "$MG24_BOARD_ID" ]]; then
    ensure_mg24_pyocd_pack
  fi

  if [[ "$BOARD_ID" == "xiao_ra4m1" ]]; then
    check_dfu_util_tool
  fi
}

# Checks host tools needed when setup runs without a board filter.
# 在未指定开发板时，检查全量主机工具依赖。
check_full_host_tools() {
  check_espressif_zephyr_tools
  check_bossac_tool
  check_dfu_util_tool
  ensure_mg24_pyocd_pack
}

# Prints informational proprietary-runner guidance for selected boards.
# 为部分开发板打印专有 runner 工具提示，仅作信息说明。
print_vendor_flash_tool_note() {
  case "$BOARD_BUILD_TARGET" in
    xiao_ble)
      printf '\nFlash note: Zephyr provides openocd, pyocd, and esptool for most boards through the SDK and Python packages.\n'
      printf 'The default Zephyr runner for %s may require SEGGER J-Link plus nrfjprog.\n' "$BOARD_BUILD_TARGET"
      printf 'Some XIAO boards, including nRF52840, also support UF2.\n'
      ;;
    xiao_ra4m1)
      printf '\nFlash note: %s uses the board USB DFU bootloader through dfu-util in this repository.\n' "$BOARD_BUILD_TARGET"
      ;;
  esac
}

# Prints board ids and the next command to fetch chip-specific blobs later.
# 打印开发板 id，并提示之后如何获取芯片专属 blobs。
print_no_board_next_steps() {
  local cli_command

  cli_command="$(next_cli_command)"

  printf '\nSetup complete.\n'
  printf 'The common Zephyr environment is ready.\n'
  printf 'List repository boards with:\n'
  if [[ "$CLI_INSTALL_STATUS" == "skipped" ]]; then
    printf '  cd %s\n' "$REPO_ROOT"
  fi
  printf '  %s list boards\n' "$cli_command"
  printf '\n'
  printf 'To fetch chip-specific blobs later, rerun with:\n'
  printf '  bash %s --board <your_board_id>\n\n' "$SETUP_SCRIPT_NAME"
  print_available_board_ids
}

# Prints the build command for the selected board after setup succeeds.
# 安装成功后，打印所选开发板的构建命令。
print_board_next_steps() {
  local cli_command

  cli_command="$(next_cli_command)"

  printf '\nSetup complete.\n'

  if [[ "$BOARD_BUILD_STATUS" == "UNSUPPORTED" ]]; then
    printf 'Board %s is marked UNSUPPORTED in the pinned Zephyr baseline.\n' "$BOARD_ID"
    printf 'No verified build command is available yet.\n'
    printf 'Check tools/build_matrix/results.md before trying a development-branch target.\n'
    return
  fi

  printf 'Next step:\n'
  if [[ "$CLI_INSTALL_STATUS" == "skipped" ]]; then
    printf '  cd %s\n' "$REPO_ROOT"
  fi
  printf '  %s build %s\n' "$cli_command" "$BOARD_ID"
  printf '\nThe helper builds the repository example with target %s.\n' "$BOARD_BUILD_TARGET"
  print_vendor_flash_tool_note
}

# Runs the full setup flow in the required shared-step order.
# 按要求的共享步骤顺序执行完整安装流程。
run_setup_flow() {
  local total_steps=6

  declare -F install_system_dependencies >/dev/null || fail "install_system_dependencies is not defined by the $SETUP_PLATFORM_LABEL setup script."

  parse_args "$@"

  if [[ -n "$BOARD_ID" ]]; then
    resolve_board_metadata "$BOARD_ID"
  fi

  step "1/$total_steps" "Installing build tools..."
  install_system_dependencies

  step "2/$total_steps" "Creating Python venv and installing west..."
  ensure_python_version
  ensure_venv_and_west

  step "3/$total_steps" "Initializing and updating the Zephyr workspace..."
  ensure_workspace

  step "4/$total_steps" "Exporting Zephyr, installing Python packages, and checking the SDK..."
  install_zephyr_tools

  step "5/$total_steps" "Installing the seeed-zephyr CLI..."
  install_cli_if_requested

  if [[ -n "$BOARD_ID" ]]; then
    step "6/$total_steps" "Resolving and fetching board-specific blobs..."
    check_board_host_tools
    fetch_board_blobs
    print_board_next_steps
  else
    step "6/$total_steps" "Checking full board-specific host tools..."
    check_full_host_tools
    print_no_board_next_steps
  fi
}
