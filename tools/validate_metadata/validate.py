# Usage:
#   Run from the repository root.
#   python3 -m pip install -r tools/validate_metadata/requirements.txt
#   python3 tools/validate_metadata/validate.py

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable

import yaml


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
VALID_ZEPHYR_SUPPORT = {"sensor_driver", "gnss_driver", "adc", "custom"}
DRIVER_BACKED_SUPPORT = {"sensor_driver", "gnss_driver"}
DRIVERLESS_SUPPORT = {"adc", "custom"}
EXPANSION_BOARD_PORT_KEYS = {"id", "type", "label"}


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
    board_paths = sorted((repo_root / "metadata" / "boards").glob("*.yaml"))
    grove_paths = sorted((repo_root / "metadata" / "grove_modules").glob("*.yaml"))
    expansion_board_paths = sorted(
        (repo_root / "metadata" / "expansion_boards").glob("*.yaml")
    )

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
    return results


def validate_file(
    path: Path, schema_validator: Callable[[ValidationResult, dict[str, Any]], None]
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
    validate_exact_keys(result, document, BOARD_REQUIRED_KEYS)

    for key in ("display_name", "zephyr_target", "vendor", "soc"):
        validate_non_empty_string(result, document, key)

    validate_allowed_value(result, document, "form_factor", VALID_FORM_FACTORS)
    validate_string_list(result, document, "also_known_as")
    validate_allowed_value(result, document, "version_policy", VALID_VERSION_POLICIES)


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
