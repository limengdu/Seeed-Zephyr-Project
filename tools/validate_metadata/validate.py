# Usage:
#   Run from the repository root.
#   python3 -m pip install -r tools/validate_metadata/requirements.txt
#   python3 tools/validate_metadata/validate.py

from __future__ import annotations

import datetime as dt
import os
import re
import sys
from pathlib import Path
from typing import Any, Callable

import yaml


# Set by collect_results so the pinmap audit can locate the upstream Zephyr tree.
# 由 collect_results 设置，供 pinmap 审计定位上游 Zephyr 树。
REPO_ROOT: Path | None = None


BOARD_REQUIRED_KEYS = {
    "id",
    "display_name",
    "zephyr_target",
    "vendor",
    "soc",
    "form_factor",
    "also_known_as",
    "version_policy",
}
# Per-board pin data is optional; boards populate it progressively.
# 按板引脚数据为可选项，各板逐步补充。
BOARD_OPTIONAL_KEYS = {
    "reserved_pins",
    "analog_pins",
    "pin_map",
    "pin_map_source",
}

GROVE_REQUIRED_KEYS = {
    "id",
    "sku",
    "display_name",
    "category",
    "interface",
    "default_address",
    "default_baud",
    "power_rail",
    "zephyr_support",
    "zephyr_compatible",
    "zephyr_driver",
    "required_configs",
    "supported_templates",
}

EXPANSION_BOARD_REQUIRED_KEYS = {
    "id",
    "sku",
    "display_name",
    "compatible_form_factor",
    "zephyr_shield",
    "ports",
    "onboard",
}

EXAMPLE_REQUIRED_KEYS = {
    "id",
    "board_id",
    "demo",
    "zephyr_target",
    "validation_status",
    "expected_behavior",
}
EXAMPLE_OPTIONAL_KEYS = {"unsupported_reason"}

# Grove examples are board-agnostic: they rely on the XIAO connector abstraction
# and declare which boards are excluded rather than a single board_id.
# Grove 示例与具体板子解耦：依赖 XIAO connector 抽象，声明排除板列表而非单一 board_id。
GROVE_EXAMPLE_REQUIRED_KEYS = {
    "id",
    "kind",
    "module_id",
    "demo",
    "interface",
    "connector",
    "pin_policy",
    "excluded_boards",
    "expected_behavior",
}
GROVE_EXAMPLE_OPTIONAL_KEYS = {"pins"}
GROVE_EXAMPLE_KIND = "grove"
VALID_EXAMPLE_KINDS = {"board", "grove"}
VALID_PIN_POLICIES = {"fixed-bus", "selectable"}
VALID_CONNECTORS = {"xiao"}
GROVE_PIN_REQUIRED_KEYS = {"role", "default", "allowed"}

FORM_FACTOR_REQUIRED_KEYS = {
    "id",
    "display_name",
    "pin_count",
    "pins",
    "layout",
    "buses",
}
FORM_FACTOR_PIN_KEYS = {"id", "type"}
FORM_FACTOR_PIN_OPTIONAL_KEYS = {"bus", "bus_role", "rail"}
VALID_PIN_TYPES = {"gpio", "power"}

STATUS_REQUIRED_KEYS = {
    "example_id",
    "example_ref",
    "zephyr_version",
    "generated_on",
    "boards",
}
STATUS_BOARD_REQUIRED_KEYS = {"board_id", "status"}
STATUS_BOARD_OPTIONAL_KEYS = {"target", "reason", "evidence"}
VALID_MATRIX_STATUSES = {
    "build-verified",
    "build-failed",
    "hardware-tested",
    "pending",
    "excluded",
}

DERIVED_KEYS = {
    "status",
    "validation",
    "evidence",
    "interfaces",
    "known_issues",
    "validated_zephyr_version",
    "power",
}

VALID_FORM_FACTORS = {"xiao"}
VALID_VERSION_POLICIES = {"latest_stable"}
VALID_INTERFACES = {"i2c", "uart", "gpio", "analog", "spi"}
VALID_POWER_RAILS = {"3v3"}
VALID_ZEPHYR_SUPPORT = {"sensor_driver", "gnss_driver", "display_driver", "adc", "custom"}
DRIVER_BACKED_SUPPORT = {"sensor_driver", "gnss_driver", "display_driver"}
DRIVERLESS_SUPPORT = {"adc", "custom"}
EXPANSION_BOARD_PORT_KEYS = {"id", "type", "label"}
VALID_EXAMPLE_DEMOS = {"blinky", "hello_world"}
VALID_EXAMPLE_STATUSES = {
    "build-only",
    "hardware-tested",
    "experimental",
    "blocked",
    "unsupported",
    "unknown",
}


class ValidationResult:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.errors: list[str] = []
        self.metadata_id: str | None = None

    @property
    def passed(self) -> bool:
        return not self.errors

    def fail(self, reason: str) -> None:
        self.errors.append(reason)


def main() -> int:
    repo_root = Path.cwd()
    results = collect_results(repo_root)
    add_duplicate_id_errors(results)

    pass_count = 0
    fail_count = 0

    for result in results:
        relpath = result.path.relative_to(repo_root).as_posix()
        if result.passed:
            pass_count += 1
            print(f"PASS {relpath}")
        else:
            fail_count += 1
            print(f"FAIL {relpath}: {'; '.join(result.errors)}")

    total_count = pass_count + fail_count
    print(f"SUMMARY: {pass_count} passed, {fail_count} failed, {total_count} total")
    return 1 if fail_count else 0


def collect_results(repo_root: Path) -> list[ValidationResult]:
    global REPO_ROOT
    REPO_ROOT = repo_root
    board_paths = sorted((repo_root / "metadata" / "boards").glob("*.yaml"))
    grove_paths = sorted((repo_root / "metadata" / "grove_modules").glob("*.yaml"))
    expansion_board_paths = sorted(
        (repo_root / "metadata" / "expansion_boards").glob("*.yaml")
    )
    form_factor_paths = sorted((repo_root / "metadata" / "form_factors").glob("*.yaml"))
    status_paths = sorted((repo_root / "metadata" / "status").glob("*.yaml"))
    example_paths = sorted((repo_root / "examples").glob("**/example.yaml"))

    results: list[ValidationResult] = []
    for path in board_paths:
        result = validate_file(path, validate_board_metadata)
        results.append(result)
    for path in grove_paths:
        result = validate_file(path, validate_grove_metadata)
        results.append(result)
    for path in expansion_board_paths:
        result = validate_file(path, validate_expansion_board_metadata)
        results.append(result)
    for path in form_factor_paths:
        result = validate_file(path, validate_form_factor_metadata)
        results.append(result)
    for path in status_paths:
        result = validate_file(
            path, validate_status_metadata, id_matches_filename=False
        )
        results.append(result)
    for path in example_paths:
        result = validate_file(path, validate_example_metadata, id_matches_filename=False)
        results.append(result)
    return results


def validate_file(
    path: Path,
    schema_validator: Callable[[ValidationResult, dict[str, Any]], None],
    *,
    id_matches_filename: bool = True,
) -> ValidationResult:
    result = ValidationResult(path)

    try:
        with path.open("r", encoding="utf-8") as yaml_file:
            document = yaml.safe_load(yaml_file)
    except yaml.YAMLError as error:
        result.fail(f"YAML parse error: {error}")
        return result
    except OSError as error:
        result.fail(f"read error: {error}")
        return result

    if not isinstance(document, dict):
        result.fail("top-level YAML document must be a mapping")
        return result

    metadata_id = document.get("id")
    if isinstance(metadata_id, str):
        result.metadata_id = metadata_id

    validate_no_derived_keys(result, document)
    if id_matches_filename:
        validate_id_matches_filename(result, document)
    schema_validator(result, document)
    return result


def validate_no_derived_keys(result: ValidationResult, document: dict[str, Any]) -> None:
    found = sorted(DERIVED_KEYS.intersection(document))
    if found:
        result.fail(f"derived keys are forbidden: {', '.join(found)}")


def validate_id_matches_filename(result: ValidationResult, document: dict[str, Any]) -> None:
    metadata_id = document.get("id")
    expected_id = result.path.stem
    if not is_non_empty_string(metadata_id):
        result.fail("id must be a non-empty string")
        return
    if metadata_id != expected_id:
        result.fail(f"id must match filename stem '{expected_id}'")


def validate_board_metadata(result: ValidationResult, document: dict[str, Any]) -> None:
    validate_allowed_keys(result, document, BOARD_REQUIRED_KEYS, BOARD_OPTIONAL_KEYS)

    for key in ("display_name", "zephyr_target", "vendor", "soc"):
        validate_non_empty_string(result, document, key)

    validate_allowed_value(result, document, "form_factor", VALID_FORM_FACTORS)
    validate_string_list(result, document, "also_known_as")
    validate_allowed_value(result, document, "version_policy", VALID_VERSION_POLICIES)
    validate_reserved_pins(result, document)
    validate_analog_pins(result, document)
    validate_pin_map(result, document)


def validate_reserved_pins(result: ValidationResult, document: dict[str, Any]) -> None:
    # reserved_pins: list of {pin, reason}; optional but must be well-formed when present.
    # reserved_pins：{pin, reason} 列表；可选，存在时必须结构正确。
    reserved = document.get("reserved_pins")
    if reserved is None:
        return
    if not isinstance(reserved, list):
        result.fail("reserved_pins must be a list")
        return
    for index, entry in enumerate(reserved):
        if not isinstance(entry, dict):
            result.fail(f"reserved_pins[{index}] must be a mapping")
            continue
        validate_exact_keys(result, entry, {"pin", "reason"})
        validate_non_empty_string(result, entry, "pin")
        validate_non_empty_string(result, entry, "reason")


def validate_analog_pins(result: ValidationResult, document: dict[str, Any]) -> None:
    validate_string_list(result, document, "analog_pins")


def validate_pin_map(result: ValidationResult, document: dict[str, Any]) -> None:
    # pin_map: list of {pin, chip_pin}; audited against the upstream connector dtsi.
    # pin_map：{pin, chip_pin} 列表；用于审计上游 connector dtsi。
    pin_map = document.get("pin_map")
    if pin_map is None:
        return
    if not isinstance(pin_map, list):
        result.fail("pin_map must be a list")
        return
    pin_indices: set[int] = set()
    for index, entry in enumerate(pin_map):
        if not isinstance(entry, dict):
            result.fail(f"pin_map[{index}] must be a mapping")
            continue
        validate_exact_keys(result, entry, {"pin", "chip_pin"})
        validate_non_empty_string(result, entry, "pin")
        validate_non_empty_string(result, entry, "chip_pin")
        pin_label = entry.get("pin") if isinstance(entry, dict) else None
        if isinstance(pin_label, str):
            match = re.fullmatch(r"D(\d+)", pin_label.strip())
            if match:
                pin_indices.add(int(match.group(1)))
            else:
                result.fail(f"pin_map[{index}].pin '{pin_label}' must look like D0..D15")
    if pin_indices:
        audit_pin_map_against_upstream(result, document, pin_indices)


def audit_pin_map_against_upstream(
    result: ValidationResult, document: dict[str, Any], pin_indices: set[int]
) -> None:
    # Parses the upstream seeed_xiao_connector.dtsi gpio-map and compares the Dn index
    # coverage against the official pin_map. Skips silently when the Zephyr workspace or
    # the board's connector dtsi is unavailable (validation must not depend on a build env).
    # 解析上游 seeed_xiao_connector.dtsi 的 gpio-map，按 Dn 索引核对官方 pin_map 覆盖。
    # 当 Zephyr 工作区或该板 connector dtsi 不可用时静默跳过（校验不应依赖构建环境）。
    if REPO_ROOT is None:
        return
    target = document.get("zephyr_target")
    if not isinstance(target, str) or "/" not in target:
        return
    board_dir_name = target.split("/", 1)[0]
    workspace = Path(os.environ.get("ZEPHYR_WORKSPACE", str(Path.home() / "zephyrproject")))
    dtsi = workspace / "zephyr" / "boards" / "seeed" / board_dir_name / "seeed_xiao_connector.dtsi"
    if not dtsi.is_file():
        # Fall back to a search under boards/ in case the board lives outside seeed/.
        # 回退到 boards/ 下搜索，以防该板不在 seeed/ 目录下。
        hits = list((workspace / "zephyr" / "boards").glob(f"*/{board_dir_name}/seeed_xiao_connector.dtsi"))
        if not hits:
            return
        dtsi = hits[0]
    try:
        text = dtsi.read_text(encoding="utf-8")
    except OSError:
        return
    # gpio-map entries look like: <N 0 &controller PIN 0>
    # gpio-map 条目形如：<N 0 &controller PIN 0>
    dtsi_indices = {
        int(m.group(1))
        for m in re.finditer(r"<\s*(\d+)\s+0\s+&\w+\s+\d+\s+0\s*>", text)
    }
    if not dtsi_indices:
        return
    missing = sorted(pin_indices - dtsi_indices)
    extra = sorted(dtsi_indices - pin_indices)
    for n in missing:
        result.fail(f"pin_map lists D{n} but upstream {dtsi.name} gpio-map has no D{n}")
    for n in extra:
        result.fail(f"upstream {dtsi.name} gpio-map defines D{n} but pin_map does not list it")


def validate_form_factor_metadata(result: ValidationResult, document: dict[str, Any]) -> None:
    validate_exact_keys(result, document, FORM_FACTOR_REQUIRED_KEYS)

    validate_non_empty_string(result, document, "display_name")
    pin_count = document.get("pin_count")
    if not isinstance(pin_count, int) or isinstance(pin_count, bool) or pin_count <= 0:
        result.fail("pin_count must be a positive integer")

    pins = document.get("pins")
    pin_ids: set[str] = set()
    if not isinstance(pins, list) or not pins:
        result.fail("pins must be a non-empty list")
    else:
        for index, pin in enumerate(pins):
            if not isinstance(pin, dict):
                result.fail(f"pins[{index}] must be a mapping")
                continue
            validate_allowed_keys(result, pin, FORM_FACTOR_PIN_KEYS, FORM_FACTOR_PIN_OPTIONAL_KEYS)
            validate_non_empty_string(result, pin, "id")
            validate_allowed_value(result, pin, "type", VALID_PIN_TYPES)
            if isinstance(pin.get("id"), str):
                pin_ids.add(pin["id"])
        if pin_count and isinstance(pin_count, int) and len(pins) != pin_count:
            result.fail(f"pins length ({len(pins)}) must equal pin_count ({pin_count})")

    layout = document.get("layout")
    if not isinstance(layout, dict):
        result.fail("layout must be a mapping")
    else:
        layout_pins = set()
        for side in ("left", "right"):
            side_pins = layout.get(side)
            if not isinstance(side_pins, list):
                result.fail(f"layout.{side} must be a list")
                continue
            for entry in side_pins:
                if not isinstance(entry, str):
                    result.fail(f"layout.{side} entries must be strings")
                else:
                    layout_pins.add(entry)
        if pin_ids and layout_pins:
            missing = pin_ids - layout_pins
            extra = layout_pins - pin_ids
            if missing:
                result.fail(f"layout missing pins: {', '.join(sorted(missing))}")
            if extra:
                result.fail(f"layout references unknown pins: {', '.join(sorted(extra))}")

    buses = document.get("buses")
    if not isinstance(buses, dict) or not buses:
        result.fail("buses must be a non-empty mapping")


def validate_grove_metadata(result: ValidationResult, document: dict[str, Any]) -> None:
    validate_exact_keys(result, document, GROVE_REQUIRED_KEYS)

    sku = document.get("sku")
    if not isinstance(sku, str) or not sku.isdigit():
        result.fail("sku must be a string of digits")

    for key in ("display_name", "category"):
        validate_non_empty_string(result, document, key)

    validate_allowed_value(result, document, "interface", VALID_INTERFACES)
    validate_string_or_null(result, document, "default_address")
    validate_integer_or_null(result, document, "default_baud")
    validate_allowed_value(result, document, "power_rail", VALID_POWER_RAILS)
    validate_allowed_value(result, document, "zephyr_support", VALID_ZEPHYR_SUPPORT)
    validate_string_or_null(result, document, "zephyr_compatible")
    validate_string_or_null(result, document, "zephyr_driver")
    validate_string_list(result, document, "required_configs")
    validate_string_list(result, document, "supported_templates")
    validate_zephyr_support_consistency(result, document)


def validate_expansion_board_metadata(
    result: ValidationResult, document: dict[str, Any]
) -> None:
    validate_exact_keys(result, document, EXPANSION_BOARD_REQUIRED_KEYS)

    sku = document.get("sku")
    if not isinstance(sku, str) or not sku.isdigit():
        result.fail("sku must be a string of digits")

    validate_non_empty_string(result, document, "display_name")
    validate_allowed_value(result, document, "compatible_form_factor", VALID_FORM_FACTORS)
    validate_string_or_null(result, document, "zephyr_shield")
    validate_expansion_board_ports(result, document)
    validate_string_list(result, document, "onboard")


def validate_example_metadata(result: ValidationResult, document: dict[str, Any]) -> None:
    # Board examples omit `kind`; Grove examples set kind: grove.
    # 板级示例省略 kind；Grove 示例设置 kind: grove。
    kind = document.get("kind", "board")
    if "kind" in document:
        validate_allowed_value(result, document, "kind", VALID_EXAMPLE_KINDS)

    if kind == GROVE_EXAMPLE_KIND:
        validate_grove_example_metadata(result, document)
        return

    # Board example schema (the original contract).
    # 板级示例契约（原有约定）。
    validate_allowed_keys(result, document, EXAMPLE_REQUIRED_KEYS, EXAMPLE_OPTIONAL_KEYS)

    for key in ("id", "board_id", "zephyr_target", "expected_behavior"):
        validate_non_empty_string(result, document, key)

    validate_allowed_value(result, document, "demo", VALID_EXAMPLE_DEMOS)
    validate_allowed_value(result, document, "validation_status", VALID_EXAMPLE_STATUSES)
    validate_example_path_consistency(result, document)

    if document.get("validation_status") == "unsupported":
        validate_non_empty_string(result, document, "unsupported_reason")
    elif "unsupported_reason" in document:
        result.fail("unsupported_reason is only allowed when validation_status is unsupported")


def validate_grove_example_metadata(result: ValidationResult, document: dict[str, Any]) -> None:
    validate_allowed_keys(
        result, document, GROVE_EXAMPLE_REQUIRED_KEYS, GROVE_EXAMPLE_OPTIONAL_KEYS
    )

    for key in ("id", "module_id", "demo", "expected_behavior"):
        validate_non_empty_string(result, document, key)

    validate_allowed_value(result, document, "interface", VALID_INTERFACES)
    validate_allowed_value(result, document, "connector", VALID_CONNECTORS)
    validate_allowed_value(result, document, "pin_policy", VALID_PIN_POLICIES)
    validate_string_list(result, document, "excluded_boards")
    validate_grove_example_path_consistency(result, document)
    validate_grove_module_exists(result, document)
    validate_grove_pins(result, document)


def validate_grove_example_path_consistency(
    result: ValidationResult, document: dict[str, Any]
) -> None:
    # A grove example lives at examples/grove/<module_id>/<demo>/example.yaml.
    # Grove 示例位于 examples/grove/<module_id>/<demo>/example.yaml。
    expected_demo = result.path.parent.name
    expected_module_id = result.path.parent.parent.name

    if document.get("demo") != expected_demo:
        result.fail(f"demo must match parent directory '{expected_demo}'")
    if document.get("module_id") != expected_module_id:
        result.fail(f"module_id must match module directory '{expected_module_id}'")


def validate_grove_module_exists(result: ValidationResult, document: dict[str, Any]) -> None:
    module_id = document.get("module_id")
    if not is_non_empty_string(module_id):
        return
    # Walk up from examples/grove/<module>/<demo>/example.yaml to the repo root.
    # 从 examples/grove/<module>/<demo>/example.yaml 向上找到仓库根目录。
    repo_root = result.path.parent.parent.parent.parent.parent
    module_file = repo_root / "metadata" / "grove_modules" / f"{module_id}.yaml"
    if not module_file.is_file():
        result.fail(f"module_id '{module_id}' has no matching metadata/grove_modules/{module_id}.yaml")


def validate_grove_pins(result: ValidationResult, document: dict[str, Any]) -> None:
    # For selectable modules: pins is a list of {role, default, allowed}.
    # fixed-bus modules must not declare pins.
    # 可选引脚模块：pins 为 {role, default, allowed} 列表；fixed-bus 模块不得声明 pins。
    pin_policy = document.get("pin_policy")
    pins = document.get("pins")

    if pin_policy == "fixed-bus":
        if pins is not None:
            result.fail("pins must be omitted when pin_policy is fixed-bus")
        return

    if pins is None:
        result.fail("pins is required when pin_policy is selectable")
        return

    if not isinstance(pins, list) or not pins:
        result.fail("pins must be a non-empty list")
        return

    roles = set()
    for index, pin in enumerate(pins):
        if not isinstance(pin, dict):
            result.fail(f"pins[{index}] must be a mapping")
            continue
        validate_exact_keys(result, pin, GROVE_PIN_REQUIRED_KEYS)
        validate_non_empty_string(result, pin, "role")
        validate_non_empty_string(result, pin, "default")
        validate_string_list(result, pin, "allowed")
        if isinstance(pin.get("role"), str):
            if pin["role"] in roles:
                result.fail(f"pins[{index}] duplicate role '{pin['role']}'")
            roles.add(pin["role"])


def validate_status_metadata(result: ValidationResult, document: dict[str, Any]) -> None:
    validate_exact_keys(result, document, STATUS_REQUIRED_KEYS)

    for key in ("example_id", "example_ref", "zephyr_version"):
        validate_non_empty_string(result, document, key)

    example_id = document.get("example_id")
    if isinstance(example_id, str) and example_id != result.path.stem:
        result.fail(f"example_id must match filename stem '{result.path.stem}'")

    generated_on = document.get("generated_on")
    if isinstance(generated_on, dt.date):
        pass
    elif isinstance(generated_on, str) and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", generated_on):
        result.fail("generated_on must use YYYY-MM-DD")
    else:
        result.fail("generated_on must use YYYY-MM-DD")

    excluded_boards = validate_status_example_ref(result, document)
    validate_status_board_rows(result, document, excluded_boards)


def validate_status_example_ref(
    result: ValidationResult, document: dict[str, Any]
) -> set[str]:
    example_ref = document.get("example_ref")
    example_id = document.get("example_id")
    if not isinstance(example_ref, str):
        return set()

    parts = [part for part in example_ref.strip("/").split("/") if part]
    if len(parts) != 3 or parts[0] != "grove":
        result.fail("example_ref must look like grove/<module>/<demo>")
        return set()

    repo_root = result.path.parent.parent.parent
    example_file = repo_root / "examples" / "grove" / parts[1] / parts[2] / "example.yaml"
    if not example_file.is_file():
        result.fail(f"example_ref target does not exist: {example_ref}")
        return set()

    try:
        example_doc = yaml.safe_load(example_file.read_text(encoding="utf-8"))
    except (yaml.YAMLError, OSError) as error:
        result.fail(f"example_ref target cannot be read: {error}")
        return set()

    if not isinstance(example_doc, dict):
        result.fail("example_ref target must be a YAML mapping")
        return set()

    if isinstance(example_id, str) and example_doc.get("id") != example_id:
        result.fail("example_id must match the referenced Grove example id")

    excluded = example_doc.get("excluded_boards")
    if not isinstance(excluded, list):
        return set()
    return {str(board) for board in excluded if isinstance(board, str)}


def validate_status_board_rows(
    result: ValidationResult, document: dict[str, Any], excluded_boards: set[str]
) -> None:
    boards = document.get("boards")
    if not isinstance(boards, list) or not boards:
        result.fail("boards must be a non-empty list")
        return

    repo_root = result.path.parent.parent.parent
    seen: set[str] = set()
    for index, row in enumerate(boards):
        if not isinstance(row, dict):
            result.fail(f"boards[{index}] must be a mapping")
            continue
        validate_allowed_keys(
            result, row, STATUS_BOARD_REQUIRED_KEYS, STATUS_BOARD_OPTIONAL_KEYS
        )
        validate_non_empty_string(result, row, "board_id")
        validate_allowed_value(result, row, "status", VALID_MATRIX_STATUSES)
        for key in ("target", "reason", "evidence"):
            if key in row:
                validate_non_empty_string(result, row, key)

        board_id = row.get("board_id")
        status = row.get("status")
        if not isinstance(board_id, str):
            continue
        if board_id in seen:
            result.fail(f"boards[{index}] duplicate board_id '{board_id}'")
        seen.add(board_id)

        board_file = repo_root / "metadata" / "boards" / f"{board_id}.yaml"
        if not board_file.is_file():
            result.fail(f"boards[{index}].board_id '{board_id}' has no board metadata")

        if status == "excluded" and board_id not in excluded_boards:
            result.fail(f"boards[{index}] is excluded but the Grove example does not exclude {board_id}")
        if board_id in excluded_boards and status != "excluded":
            result.fail(f"boards[{index}] must be excluded because the Grove example excludes {board_id}")
        if status in {"build-verified", "build-failed", "hardware-tested"}:
            validate_non_empty_string(result, row, "evidence")
        if status == "excluded":
            validate_non_empty_string(result, row, "reason")


def validate_example_path_consistency(
    result: ValidationResult, document: dict[str, Any]
) -> None:
    expected_demo = result.path.parent.name
    expected_board_id = result.path.parent.parent.name

    if document.get("demo") != expected_demo:
        result.fail(f"demo must match parent directory '{expected_demo}'")
    if document.get("board_id") != expected_board_id:
        result.fail(f"board_id must match board directory '{expected_board_id}'")


def validate_expansion_board_ports(
    result: ValidationResult, document: dict[str, Any]
) -> None:
    ports = document.get("ports")
    if not isinstance(ports, list):
        result.fail("ports must be a list")
        return

    for index, port in enumerate(ports):
        if not isinstance(port, dict):
            result.fail(f"ports[{index}] must be a mapping")
            continue

        validate_exact_keys(result, port, EXPANSION_BOARD_PORT_KEYS)
        validate_non_empty_string(result, port, "id")
        validate_allowed_value(result, port, "type", VALID_INTERFACES)
        validate_non_empty_string(result, port, "label")


def validate_exact_keys(
    result: ValidationResult, document: dict[str, Any], required_keys: set[str]
) -> None:
    actual_keys = set(document)
    missing = sorted(required_keys - actual_keys)
    extra = sorted(actual_keys - required_keys)

    if missing:
        result.fail(f"missing required keys: {', '.join(missing)}")
    if extra:
        result.fail(f"extra keys are not allowed: {', '.join(extra)}")


def validate_allowed_keys(
    result: ValidationResult,
    document: dict[str, Any],
    required_keys: set[str],
    optional_keys: set[str],
) -> None:
    actual_keys = set(document)
    missing = sorted(required_keys - actual_keys)
    allowed = required_keys | optional_keys
    extra = sorted(actual_keys - allowed)

    if missing:
        result.fail(f"missing required keys: {', '.join(missing)}")
    if extra:
        result.fail(f"extra keys are not allowed: {', '.join(extra)}")


def validate_non_empty_string(
    result: ValidationResult, document: dict[str, Any], key: str
) -> None:
    if not is_non_empty_string(document.get(key)):
        result.fail(f"{key} must be a non-empty string")


def validate_allowed_value(
    result: ValidationResult, document: dict[str, Any], key: str, allowed_values: set[str]
) -> None:
    value = document.get(key)
    if value not in allowed_values:
        allowed = ", ".join(sorted(allowed_values))
        result.fail(f"{key} must be one of: {allowed}")


def validate_string_or_null(
    result: ValidationResult, document: dict[str, Any], key: str
) -> None:
    value = document.get(key)
    if value is not None and not isinstance(value, str):
        result.fail(f"{key} must be a string or null")


def validate_integer_or_null(
    result: ValidationResult, document: dict[str, Any], key: str
) -> None:
    value = document.get(key)
    if value is not None and (not isinstance(value, int) or isinstance(value, bool)):
        result.fail(f"{key} must be an integer or null")


def validate_string_list(
    result: ValidationResult, document: dict[str, Any], key: str
) -> None:
    value = document.get(key)
    if not isinstance(value, list):
        result.fail(f"{key} must be a list of strings")
        return

    invalid_indexes = [
        str(index) for index, item in enumerate(value) if not isinstance(item, str)
    ]
    if invalid_indexes:
        result.fail(f"{key} must contain only strings; invalid indexes: {', '.join(invalid_indexes)}")


def validate_zephyr_support_consistency(
    result: ValidationResult, document: dict[str, Any]
) -> None:
    zephyr_support = document.get("zephyr_support")
    zephyr_compatible = document.get("zephyr_compatible")
    zephyr_driver = document.get("zephyr_driver")

    if zephyr_support in DRIVER_BACKED_SUPPORT:
        if zephyr_compatible is None or zephyr_driver is None:
            result.fail(
                "zephyr_compatible and zephyr_driver must be non-null for driver-backed support"
            )
    elif zephyr_support in DRIVERLESS_SUPPORT:
        if zephyr_compatible is not None or zephyr_driver is not None:
            result.fail(
                "zephyr_compatible and zephyr_driver must be null for driverless support"
            )


def add_duplicate_id_errors(results: list[ValidationResult]) -> None:
    results_by_id: dict[str, list[ValidationResult]] = {}
    for result in results:
        if result.metadata_id is None:
            continue
        results_by_id.setdefault(result.metadata_id, []).append(result)

    for metadata_id, duplicate_results in results_by_id.items():
        if len(duplicate_results) < 2:
            continue
        relpaths = ", ".join(sorted(result.path.as_posix() for result in duplicate_results))
        for result in duplicate_results:
            result.fail(f"duplicate id '{metadata_id}' also found in: {relpaths}")


def is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


if __name__ == "__main__":
    sys.exit(main())
