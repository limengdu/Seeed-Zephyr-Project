#!/usr/bin/env bash
#
# Purpose:
#   Shared uninstall flow for Seeed Zephyr Base platform uninstall scripts.
#   Platform entrypoints define the system-tools note, then call
#   run_uninstall_flow to remove the CLI symlink and, on request, the Zephyr
#   workspace and SDK.

COMMON_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ -z "${SCRIPT_DIR:-}" ]]; then
  SCRIPT_DIR="$(cd "$COMMON_SCRIPT_DIR/.." && pwd)"
fi

if [[ -z "${REPO_ROOT:-}" ]]; then
  REPO_ROOT="$(cd "$COMMON_SCRIPT_DIR/../.." && pwd)"
fi

ZEPHYR_WORKSPACE="${ZEPHYR_WORKSPACE:-$HOME/zephyrproject}"
SETUP_PLATFORM_LABEL="${SETUP_PLATFORM_LABEL:-platform}"
CLI_SOURCE_PATH="$REPO_ROOT/scripts/seeed-zephyr"
CLI_INSTALL_DIR="${SEEED_ZEPHYR_CLI_INSTALL_DIR:-}"

DRY_RUN=0
ASSUME_YES=0

if ! declare -p CLI_INSTALL_DIR_CANDIDATES >/dev/null 2>&1; then
  CLI_INSTALL_DIR_CANDIDATES=("$HOME/.local/bin")
fi

# Prints an error message and exits the script.
# 打印错误信息并退出脚本。
fail() {
  printf 'Error: %s\n' "$*" >&2
  exit 1
}

# Records and prints the current high-level uninstall step.
# 记录并打印当前的高层卸载步骤。
step() {
  printf '\n[%s] %s\n' "$1" "$2"
}

# Parses command-line arguments into global uninstall options.
# 解析命令行参数并写入全局卸载选项。
parse_uninstall_args() {
  while (($# > 0)); do
    case "$1" in
      --yes | -y)
        ASSUME_YES=1
        shift
        ;;
      --dry-run)
        DRY_RUN=1
        shift
        ;;
      -h | --help)
        printf 'Usage: bash %s [--yes] [--dry-run]\n\n' "${UNINSTALL_SCRIPT_NAME:-scripts/uninstall.sh}"
        printf '  --yes      Remove the workspace and SDK without asking.\n'
        printf '  --dry-run  Show what would be removed without changing anything.\n'
        exit 0
        ;;
      *)
        fail "Unknown argument: $1"
        ;;
    esac
  done
}

# Asks a yes/no question where the default answer is no.
# 询问 yes/no，其中默认答案为 no。
prompt_yes_no() {
  local prompt=$1
  local answer

  # Non-interactive sessions keep data unless --yes is given.
  # 非交互会话下，除非传入 --yes，否则保留数据。
  if [[ ! -t 0 ]]; then
    return 1
  fi

  while true; do
    read -r -p "$prompt [y/N] " answer
    case "$answer" in
      [Yy] | [Yy][Ee][Ss])
        return 0
        ;;
      "" | [Nn] | [Nn][Oo])
        return 1
        ;;
      *)
        printf 'Please answer y or n.\n'
        ;;
    esac
  done
}

# Returns success when removal of the described target is confirmed.
# 当确认要删除所描述的目标时返回成功。
confirm_removal() {
  local description=$1

  if ((ASSUME_YES)); then
    return 0
  fi

  prompt_yes_no "Remove $description?"
}

# Moves a path to the trash, or aside as a backup when no trash tool exists.
# 把路径移入回收站；若没有回收站工具，则改名备份到一旁。
trash_path() {
  local target=$1

  [[ -e "$target" || -L "$target" ]] || return 0

  if command -v trash >/dev/null 2>&1; then
    trash "$target"
    return $?
  fi

  if [[ "$(uname -s)" == "Darwin" && -d "$HOME/.Trash" ]]; then
    mv "$target" "$HOME/.Trash/$(basename "$target").$(date +%Y%m%d%H%M%S)"
    return $?
  fi

  if command -v gio >/dev/null 2>&1; then
    gio trash "$target"
    return $?
  fi

  if command -v trash-put >/dev/null 2>&1; then
    trash-put "$target"
    return $?
  fi

  local backup="${target%/}.uninstall-backup-$(date +%Y%m%d%H%M%S)"
  mv "$target" "$backup"
  printf 'No trash tool found; moved to a backup instead of deleting:\n' >&2
  printf '  %s\n' "$backup" >&2
  printf 'Delete it manually when you are sure it is no longer needed.\n' >&2
}

# Returns success when a symlink target is the repository seeed-zephyr launcher.
# 当符号链接目标是仓库的 seeed-zephyr 启动器时返回成功。
symlink_is_ours() {
  local link=$1
  local target

  target="$(readlink "$link")" || return 1
  [[ "$target" == "$CLI_SOURCE_PATH" || "$target" == */scripts/seeed-zephyr ]]
}

# Removes the seeed-zephyr CLI symlink created by setup.
# 删除 setup 创建的 seeed-zephyr CLI 符号链接。
remove_cli_symlink() {
  local candidates=()
  local dir
  local link
  local seen=":"
  local found=0

  if [[ -n "$CLI_INSTALL_DIR" ]]; then
    candidates+=("$CLI_INSTALL_DIR/seeed-zephyr")
  fi

  for dir in "${CLI_INSTALL_DIR_CANDIDATES[@]}"; do
    candidates+=("$dir/seeed-zephyr")
  done

  if command -v seeed-zephyr >/dev/null 2>&1; then
    candidates+=("$(command -v seeed-zephyr)")
  fi

  for link in "${candidates[@]}"; do
    case "$seen" in
      *":$link:"*)
        continue
        ;;
    esac
    seen="$seen$link:"

    [[ -L "$link" || -e "$link" ]] || continue

    if [[ -L "$link" ]] && symlink_is_ours "$link"; then
      found=1
      if ((DRY_RUN)); then
        printf '[dry-run] would remove seeed-zephyr symlink: %s\n' "$link"
      else
        unlink "$link"
        printf 'Removed seeed-zephyr command: %s\n' "$link"
      fi
    elif [[ -L "$link" ]]; then
      printf 'Kept %s (symlink points elsewhere: %s).\n' "$link" "$(readlink "$link")"
    else
      printf 'Kept %s (not a symlink created by setup).\n' "$link"
    fi
  done

  ((found)) || printf 'No seeed-zephyr CLI command was found.\n'
}

# Removes the Zephyr west workspace after confirmation.
# 确认后删除 Zephyr west 工作区。
remove_workspace() {
  if [[ ! -d "$ZEPHYR_WORKSPACE" ]]; then
    printf 'No Zephyr workspace at %s.\n' "$ZEPHYR_WORKSPACE"
    return
  fi

  if confirm_removal "the Zephyr workspace at $ZEPHYR_WORKSPACE (Python venv, Zephyr source, and modules)"; then
    if ((DRY_RUN)); then
      printf '[dry-run] would move to trash: %s\n' "$ZEPHYR_WORKSPACE"
    else
      trash_path "$ZEPHYR_WORKSPACE" && printf 'Removed Zephyr workspace: %s\n' "$ZEPHYR_WORKSPACE"
    fi
  else
    printf 'Kept Zephyr workspace: %s\n' "$ZEPHYR_WORKSPACE"
  fi
}

# Removes any Zephyr SDK installations after confirmation.
# 确认后删除所有 Zephyr SDK 安装目录。
remove_sdk() {
  local sdks=()
  local sdk

  if [[ -n "${ZEPHYR_SDK_INSTALL_DIR:-}" && -d "$ZEPHYR_SDK_INSTALL_DIR" ]]; then
    sdks+=("$ZEPHYR_SDK_INSTALL_DIR")
  fi

  for sdk in "$HOME"/zephyr-sdk-*; do
    [[ -d "$sdk" ]] && sdks+=("$sdk")
  done

  if ((${#sdks[@]} == 0)); then
    printf 'No Zephyr SDK was found under %s.\n' "$HOME"
    return
  fi

  for sdk in "${sdks[@]}"; do
    if confirm_removal "the Zephyr SDK at $sdk"; then
      if ((DRY_RUN)); then
        printf '[dry-run] would move to trash: %s\n' "$sdk"
      else
        trash_path "$sdk" && printf 'Removed Zephyr SDK: %s\n' "$sdk"
      fi
    else
      printf 'Kept Zephyr SDK: %s\n' "$sdk"
    fi
  done
}

# Runs the full uninstall flow in order.
# 按顺序执行完整卸载流程。
run_uninstall_flow() {
  declare -F print_system_tools_note >/dev/null || fail "print_system_tools_note is not defined by the $SETUP_PLATFORM_LABEL uninstall script."

  parse_uninstall_args "$@"

  printf 'Seeed Zephyr Base uninstaller (%s)\n' "$SETUP_PLATFORM_LABEL"
  if ((DRY_RUN)); then
    printf 'Dry run: nothing will be changed.\n'
  fi

  step "1/4" "Removing the seeed-zephyr CLI command..."
  remove_cli_symlink

  step "2/4" "Zephyr workspace..."
  remove_workspace

  step "3/4" "Zephyr SDK..."
  remove_sdk

  step "4/4" "Shared system build tools..."
  print_system_tools_note

  printf '\nUninstall finished.\n'
}
