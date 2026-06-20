#!/usr/bin/env bash
#
# Purpose:
#   Build the baseline repository example for every board in metadata/boards and record
#   a pass/fail/unsupported matrix for Seeed Zephyr Base.
#
# Usage:
#   bash tools/build_matrix/run.sh
#
# Results:
#   tools/build_matrix/results.md
#
# Environment:
#   ZEPHYR_WORKSPACE defaults to ~/zephyrproject.
#   BUILD_MATRIX_GENERATED_ON defaults to YYYY-MM-DD so formal validation runs
#   can fill the date explicitly without depending on host date formatting.

set -uo pipefail

ZEPHYR_WORKSPACE="${ZEPHYR_WORKSPACE:-$HOME/zephyrproject}"
VENV_DIR="$ZEPHYR_WORKSPACE/.venv"
WEST="$VENV_DIR/bin/west"
DEFAULT_EXAMPLE_NAME="blinky"
BUILD_MATRIX_GENERATED_ON="${BUILD_MATRIX_GENERATED_ON:-YYYY-MM-DD}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BOARD_METADATA_DIR="$REPO_ROOT/metadata/boards"
BOARD_EXAMPLES_DIR="$REPO_ROOT/examples/boards"
RESULTS_FILE="$SCRIPT_DIR/results.md"
BOARD_OVERRIDES_FILE="$SCRIPT_DIR/board-overrides.tsv"
RP2_BOOTLOADER_SNIPPET="rp2-boot-mode-retention"

TOTAL_COUNT=0
PASS_COUNT=0
FAIL_COUNT=0
UNSUPPORTED_COUNT=0
SUMMARY_LINES=""

BUILD_OUTPUT=""
BLOB_OUTPUT=""

# Prints an error message and exits the script.
# 打印错误信息并退出脚本。
fail() {
  printf 'Error: %s\n' "$*" >&2
  exit 1
}

# Reads a flat YAML scalar value from a board metadata file.
# 从开发板 metadata 文件读取一个扁平 YAML 标量值。
read_board_metadata_value() {
  local board_file=$1
  local key=$2

  sed -n "s/^[[:space:]]*$key:[[:space:]]*//p" "$board_file" | head -n 1
}

# Reads a flat YAML scalar value from a repository example metadata file.
# 从仓库示例 metadata 文件读取一个扁平 YAML 标量值。
read_example_metadata_value() {
  local example_path=$1
  local key=$2
  local example_file="$REPO_ROOT/$example_path/example.yaml"

  [[ -f "$example_file" ]] || return 1

  sed -n "s/^[[:space:]]*$key:[[:space:]]*//p" "$example_file" | head -n 1
}

# Formats notes for a successful build matrix row.
# 格式化构建矩阵成功行的说明。
build_success_notes() {
  local override_note=$1
  local validation_status=$2
  local notes="Build succeeded."

  if [[ "$validation_status" == "hardware-tested" ]]; then
    notes="$notes Hardware-tested example; see AI use/HARDWARE_VERIFICATION.md."
  fi
  if [[ -n "$override_note" ]]; then
    notes="$notes $override_note"
  fi

  printf '%s\n' "$notes"
}

# Reads a board-specific build matrix override row.
# 读取单个开发板的构建矩阵覆盖配置行。
read_board_override_row() {
  local board_id=$1

  [[ -f "$BOARD_OVERRIDES_FILE" ]] || return 1

  awk -F '\t' -v board_id="$board_id" '
    $0 ~ /^[[:space:]]*#/ || $0 ~ /^[[:space:]]*$/ {
      next
    }
    $1 == board_id {
      print
      found = 1
      exit
    }
    END {
      if (!found) {
        exit 1
      }
    }
  ' "$BOARD_OVERRIDES_FILE"
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

# Escapes text so it is safe inside a Markdown table cell.
# 转义文本，使其可以安全放入 Markdown 表格单元格。
markdown_cell() {
  local text=$1

  text="${text//$'\r'/}"
  text="${text//|/\\|}"
  text="${text//$'\n'/<br>}"
  printf '%s' "$text"
}

# Returns the first and last useful lines from command output.
# 从命令输出中返回开头和结尾的有效行。
error_excerpt() {
  local output=$1
  local clean_output
  local line_count
  local head_lines
  local tail_lines

  clean_output="$(printf '%s\n' "$output" | sed -e 's/[[:space:]]*$//' -e '/^[[:space:]]*$/d')"

  if [[ -z "$clean_output" ]]; then
    printf 'No useful error output was captured.'
    return
  fi

  line_count="$(printf '%s\n' "$clean_output" | wc -l | tr -d '[:space:]')"

  if ((line_count <= 10)); then
    printf '%s\n' "$clean_output"
    return
  fi

  head_lines="$(printf '%s\n' "$clean_output" | sed -n '1,5p')"
  tail_lines="$(printf '%s\n' "$clean_output" | tail -n 5)"

  printf 'First useful lines:\n%s\nLast useful lines:\n%s\n' "$head_lines" "$tail_lines"
}

# Checks whether a build failure contains Zephyr board qualifier suggestions.
# 检查构建失败信息中是否包含 Zephyr 开发板 qualifier 建议。
has_board_qualifier_suggestions() {
  local output=$1

  [[ "$output" == *"Board qualifiers"* ]] &&
    [[ "$output" == *"not found"* ]] &&
    [[ "$output" == *"Valid board targets"* ]] &&
    [[ "$output" == *"are:"* ]]
}

# Checks whether Zephyr reports that the board target is unavailable.
# 检查 Zephyr 是否报告当前开发板 target 不可用。
is_missing_board_target_error() {
  local output=$1

  [[ "$output" == *"No board named"* ]] ||
    [[ "$output" == *"Invalid BOARD"* ]]
}

# Parses the best retry target from Zephyr's valid board target list.
# 从 Zephyr 的有效开发板 target 列表中解析最适合重试的 target。
parse_retry_target() {
  local output=$1

  printf '%s\n' "$output" | awk '
    /Valid board targets .* are:/ || /Valid board targets are:/ {
      capture = 1
      next
    }
    capture {
      line = $0
      gsub(/`/, "", line)
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", line)
      gsub(/^[-*][[:space:]]*/, "", line)

      if (line == "") {
        next
      }

      if (line ~ /^[A-Za-z0-9_][A-Za-z0-9_.\/-]*$/ && index(line, "/") > 0) {
        if (first == "") {
          first = line
        }
        if (index(line, "hpcore") > 0 && hpcore == "") {
          hpcore = line
        }
        next
      }

      if (first != "") {
        exit
      }
    }
    END {
      if (hpcore != "") {
        print hpcore
      } else if (first != "") {
        print first
      }
    }
  '
}

# Ensures the configured Zephyr workspace and venv west command are available.
# 确认配置的 Zephyr 工作区和虚拟环境 west 命令可用。
ensure_prerequisites() {
  [[ -d "$BOARD_METADATA_DIR" ]] || fail "Board metadata directory was not found: $BOARD_METADATA_DIR"
  [[ -d "$BOARD_EXAMPLES_DIR" ]] || fail "Board examples directory was not found: $BOARD_EXAMPLES_DIR"
  [[ -x "$WEST" ]] || fail "west was not found or is not executable: $WEST"
  [[ -d "$ZEPHYR_WORKSPACE" ]] || fail "Zephyr workspace directory was not found: $ZEPHYR_WORKSPACE"
}

# Fetches binary blobs for the board vendor when Zephyr reports any blobs.
# 当 Zephyr 报告该厂商 HAL 模块存在 blobs 时，获取对应二进制 blobs。
ensure_chip_blobs() {
  local vendor=$1
  local module
  local list_output
  local list_status
  local fetch_output
  local fetch_status

  BLOB_OUTPUT=""

  if ! module="$(vendor_to_hal_module "$vendor")"; then
    return 0
  fi

  list_output="$(
    (
      cd "$ZEPHYR_WORKSPACE" &&
        "$WEST" blobs list "$module"
    ) 2>&1
  )"
  list_status=$?

  if ((list_status != 0)); then
    # `west blobs list` fails for modules with no blob declaration (e.g. hal_atmel).
    # Treat that as "no blobs" and continue instead of failing the board.
    # 对没有 blob 声明的模块（如 hal_atmel），`west blobs list` 会失败；
    # 视为「无 blobs」并继续，而不是判定该开发板失败。
    return 0
  fi

  if [[ -z "$(printf '%s\n' "$list_output" | sed '/^[[:space:]]*$/d')" ]]; then
    return 0
  fi

  fetch_output="$(
    (
      cd "$ZEPHYR_WORKSPACE" &&
        "$WEST" blobs fetch "$module"
    ) 2>&1
  )"
  fetch_status=$?

  if ((fetch_status != 0)); then
    BLOB_OUTPUT="$fetch_output"
    return "$fetch_status"
  fi

  return 0
}

# Runs one west build for the selected repository example and stores combined output.
# 为选定仓库示例执行一次 west build，并把标准输出和错误输出一起保存。
run_build() {
  local target=$1
  local example_path=$2
  local vendor=$3
  local example_abs_path
  local build_status
  local build_args

  case "$example_path" in
    /*)
      example_abs_path="$example_path"
      ;;
    *)
      example_abs_path="$REPO_ROOT/$example_path"
      ;;
  esac

  BUILD_OUTPUT="$(
    (
      cd "$ZEPHYR_WORKSPACE" &&
        build_args=(-p always -b "$target") &&
        if [[ "$vendor" == "raspberrypi" ]]; then
          build_args+=("-S" "$RP2_BOOTLOADER_SNIPPET")
        fi &&
        build_args+=("$example_abs_path") &&
        "$WEST" build "${build_args[@]}"
    ) 2>&1
  )"
  build_status=$?

  return "$build_status"
}

# Writes the Markdown result table header.
# 写入 Markdown 结果表头。
write_results_header() {
  {
    printf '# Board Build Matrix Results\n\n'
    printf 'Generated on: %s\n\n' "$BUILD_MATRIX_GENERATED_ON"
    printf 'Values below come from real per-board repository example builds. The default example is `examples/boards/<board_id>/%s`; board-specific overrides are listed in `%s`. Replace the placeholder date when recording a formal validation pass.\n\n' "$DEFAULT_EXAMPLE_NAME" "$(basename "$BOARD_OVERRIDES_FILE")"
    printf '| board id | vendor | example | final target | result (PASS/FAIL/UNSUPPORTED) | notes |\n'
    printf '| --- | --- | --- | --- | --- | --- |\n'
  } >"$RESULTS_FILE"
}

# Appends one board result row to results.md.
# 向 results.md 追加一行开发板结果。
append_result_row() {
  local board_id=$1
  local vendor=$2
  local example_path=$3
  local final_target=$4
  local result=$5
  local notes=$6

  printf '| %s | %s | `%s` | `%s` | %s | %s |\n' \
    "$(markdown_cell "$board_id")" \
    "$(markdown_cell "$vendor")" \
    "$(markdown_cell "$example_path")" \
    "$(markdown_cell "$final_target")" \
    "$(markdown_cell "$result")" \
    "$(markdown_cell "$notes")" >>"$RESULTS_FILE"
}

# Records one board result in counters, Markdown, and stdout summary data.
# 将一个开发板结果记录到计数器、Markdown 和标准输出摘要数据中。
record_board_result() {
  local board_id=$1
  local vendor=$2
  local example_path=$3
  local final_target=$4
  local result=$5
  local notes=$6
  local summary_note=""

  TOTAL_COUNT=$((TOTAL_COUNT + 1))

  case "$result" in
    PASS)
      PASS_COUNT=$((PASS_COUNT + 1))
      ;;
    UNSUPPORTED)
      UNSUPPORTED_COUNT=$((UNSUPPORTED_COUNT + 1))
      summary_note=" - $(printf '%s\n' "$notes" | sed -n '1p')"
      ;;
    *)
      FAIL_COUNT=$((FAIL_COUNT + 1))
      summary_note=" - $(printf '%s\n' "$notes" | sed -n '1p')"
      ;;
  esac

  append_result_row "$board_id" "$vendor" "$example_path" "$final_target" "$result" "$notes"
  SUMMARY_LINES="${SUMMARY_LINES}${board_id}: ${result} (${final_target}, ${example_path})${summary_note}"$'\n'
}

# Builds one board, retrying once with a fully-qualified target when suggested.
# 构建单个开发板；当 Zephyr 给出完整 target 建议时，使用该 target 重试一次。
process_board() {
  local board_file=$1
  local board_id
  local vendor
  local metadata_target
  local final_target
  local example_path
  local support_status
  local override_row
  local override_status
  local override_example_path
  local override_note
  local result
  local notes
  local build_status
  local retry_target
  local first_output
  local validation_status

  board_id="$(basename "$board_file" .yaml)"
  vendor="$(read_board_metadata_value "$board_file" "vendor")"
  metadata_target="$(read_board_metadata_value "$board_file" "zephyr_target")"
  final_target="$metadata_target"
  example_path="examples/boards/$board_id/$DEFAULT_EXAMPLE_NAME"
  support_status="supported"
  override_note=""

  if override_row="$(read_board_override_row "$board_id")"; then
    IFS=$'\t' read -r _ override_status override_example_path override_note <<<"$override_row"

    [[ -n "$override_status" ]] && support_status="$override_status"
    [[ -n "$override_example_path" ]] && example_path="$override_example_path"
  fi

  printf 'Building %s...\n' "$board_id"

  if [[ -z "$vendor" || -z "$metadata_target" ]]; then
    record_board_result "$board_id" "$vendor" "$example_path" "$final_target" "FAIL" "Missing vendor or zephyr_target metadata."
    return
  fi

  if [[ "$support_status" == "unsupported" ]]; then
    notes="${override_note:-Board target is not supported by this Zephyr baseline.}"
    record_board_result "$board_id" "$vendor" "$example_path" "$final_target" "UNSUPPORTED" "$notes"
    return
  fi

  if [[ "$support_status" != "supported" ]]; then
    record_board_result "$board_id" "$vendor" "$example_path" "$final_target" "FAIL" "Unknown build matrix support status: $support_status."
    return
  fi

  if [[ ! -f "$REPO_ROOT/$example_path/CMakeLists.txt" ]]; then
    record_board_result "$board_id" "$vendor" "$example_path" "$final_target" "FAIL" "Repository example is missing CMakeLists.txt."
    return
  fi

  validation_status="$(read_example_metadata_value "$example_path" "validation_status")"

  if ! ensure_chip_blobs "$vendor"; then
    notes="$(error_excerpt "$BLOB_OUTPUT")"
    record_board_result "$board_id" "$vendor" "$example_path" "$final_target" "FAIL" "$notes"
    return
  fi

  run_build "$metadata_target" "$example_path" "$vendor"
  build_status=$?
  if ((build_status == 0)); then
    notes="$(build_success_notes "$override_note" "$validation_status")"
    record_board_result "$board_id" "$vendor" "$example_path" "$final_target" "PASS" "$notes"
    return
  fi

  first_output="$BUILD_OUTPUT"

  if has_board_qualifier_suggestions "$first_output"; then
    retry_target="$(parse_retry_target "$first_output")"

    if [[ -n "$retry_target" && "$retry_target" != "$metadata_target" ]]; then
      final_target="$retry_target"

      if run_build "$retry_target" "$example_path" "$vendor"; then
        notes="$(build_success_notes "$override_note" "$validation_status") Retried from $metadata_target after Zephyr board qualifier suggestion."
        record_board_result "$board_id" "$vendor" "$example_path" "$final_target" "PASS" "$notes"
        return
      fi

      notes="$(printf 'Retried from %s after Zephyr board qualifier suggestion.\n%s' "$metadata_target" "$(error_excerpt "$BUILD_OUTPUT")")"
      record_board_result "$board_id" "$vendor" "$example_path" "$final_target" "FAIL" "$notes"
      return
    fi
  fi

  if is_missing_board_target_error "$first_output"; then
    notes="$(printf 'Zephyr baseline does not provide this board target.\n%s' "$(error_excerpt "$first_output")")"
    record_board_result "$board_id" "$vendor" "$example_path" "$final_target" "UNSUPPORTED" "$notes"
    return
  fi

  notes="$(printf 'west build exited with status %s.\n%s' "$build_status" "$(error_excerpt "$first_output")")"
  result="FAIL"
  record_board_result "$board_id" "$vendor" "$example_path" "$final_target" "$result" "$notes"
}

# Runs the full board build matrix and prints a concise summary.
# 运行完整开发板构建矩阵，并打印简洁摘要。
main() {
  local board_file
  local board_files=("$BOARD_METADATA_DIR"/*.yaml)

  ensure_prerequisites

  # Activate the venv so build tools like esptool are on PATH (ESP32 needs it).
  # 激活虚拟环境，让 esptool 等构建工具位于 PATH 中（ESP32 构建需要它）。
  # shellcheck source=/dev/null
  source "$VENV_DIR/bin/activate"

  write_results_header

  for board_file in "${board_files[@]}"; do
    [[ -f "$board_file" ]] || continue
    process_board "$board_file"
  done

  printf '\nSummary: total=%s pass=%s fail=%s unsupported=%s\n' "$TOTAL_COUNT" "$PASS_COUNT" "$FAIL_COUNT" "$UNSUPPORTED_COUNT"
  printf '%s' "$SUMMARY_LINES"
  printf '\nResults written to %s\n' "$RESULTS_FILE"
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  main "$@"
fi
