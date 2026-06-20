#!/usr/bin/env bash
#
# Purpose:
#   Build one repository-owned Zephyr example from the project root.
#
# Usage:
#   bash scripts/build-example.sh examples/boards/xiao_esp32c6/blinky
#
# Environment:
#   ZEPHYR_WORKSPACE defaults to ~/zephyrproject.

set -euo pipefail

ZEPHYR_WORKSPACE="${ZEPHYR_WORKSPACE:-$HOME/zephyrproject}"
VENV_DIR="$ZEPHYR_WORKSPACE/.venv"
WEST="$VENV_DIR/bin/west"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BOARD_METADATA_DIR="$REPO_ROOT/metadata/boards"

# Prints an error message and exits the script.
# 打印错误信息并退出脚本。
fail() {
	printf 'Error: %s\n' "$*" >&2
	exit 1
}

# Reads a flat YAML scalar value from a file.
# 从文件读取一个扁平 YAML 标量值。
read_yaml_value() {
	local file_path=$1
	local key=$2

	sed -n "s/^[[:space:]]*$key:[[:space:]]*//p" "$file_path" | head -n 1
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

# Fetches vendor blobs when the selected Zephyr HAL module declares any.
# 当 Zephyr HAL 模块声明 blobs 时，获取对应厂商二进制文件。
ensure_chip_blobs() {
	local vendor=$1
	local module
	local list_output

	if ! module="$(vendor_to_hal_module "$vendor")"; then
		return 0
	fi

	if ! list_output="$(
		(
			cd "$ZEPHYR_WORKSPACE" &&
				"$WEST" blobs list "$module"
		) 2>&1
	)"; then
		return 0
	fi

	if [[ -z "$(printf '%s\n' "$list_output" | sed '/^[[:space:]]*$/d')" ]]; then
		return 0
	fi

	(cd "$ZEPHYR_WORKSPACE" && "$WEST" blobs fetch "$module")
}

# Resolves a user-provided example path to an absolute directory.
# 将用户输入的示例路径解析为绝对目录。
resolve_example_dir() {
	local example_input=$1
	local candidate

	case "$example_input" in
		/*)
			candidate="$example_input"
			;;
		*)
			candidate="$REPO_ROOT/$example_input"
			;;
	esac

	[[ -d "$candidate" ]] || fail "Example directory was not found: $example_input"
	(cd "$candidate" && pwd)
}

main() {
	local example_input="${1:-}"
	local example_dir
	local example_file
	local board_id
	local target
	local validation_status
	local board_file
	local vendor
	local display_path

	[[ -n "$example_input" ]] || fail "Usage: bash scripts/build-example.sh <example-directory>"
	[[ -x "$WEST" ]] || fail "west was not found or is not executable: $WEST"
	[[ -d "$ZEPHYR_WORKSPACE" ]] || fail "Zephyr workspace was not found: $ZEPHYR_WORKSPACE"

	example_dir="$(resolve_example_dir "$example_input")"
	example_file="$example_dir/example.yaml"
	[[ -f "$example_file" ]] || fail "example.yaml was not found in: $example_dir"

	board_id="$(read_yaml_value "$example_file" "board_id")"
	target="$(read_yaml_value "$example_file" "zephyr_target")"
	validation_status="$(read_yaml_value "$example_file" "validation_status")"
	board_file="$BOARD_METADATA_DIR/$board_id.yaml"
	display_path="${example_dir#$REPO_ROOT/}"

	[[ -n "$board_id" ]] || fail "example.yaml is missing board_id."
	[[ -n "$target" ]] || fail "example.yaml is missing zephyr_target."
	[[ -f "$board_file" ]] || fail "Board metadata was not found: $board_file"

	if [[ "$validation_status" == "unsupported" ]]; then
		printf 'UNSUPPORTED: %s uses board target %s, which is not available in the selected Zephyr baseline.\n' "$display_path" "$target"
		exit 3
	fi

	vendor="$(read_yaml_value "$board_file" "vendor")"
	[[ -n "$vendor" ]] || fail "Board metadata is missing vendor: $board_file"

	# Activate the venv so build helpers such as esptool are available on PATH.
	# 激活虚拟环境，让 esptool 等构建辅助工具位于 PATH 中。
	# shellcheck source=/dev/null
	source "$VENV_DIR/bin/activate"

	ensure_chip_blobs "$vendor"

	printf 'Building %s for %s...\n' "$display_path" "$target"
	(cd "$ZEPHYR_WORKSPACE" && "$WEST" build -p always -b "$target" "$example_dir")
	printf 'Build succeeded: %s\n' "$display_path"
}

main "$@"
