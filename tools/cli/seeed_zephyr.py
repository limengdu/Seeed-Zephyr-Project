#!/usr/bin/env python3

from __future__ import annotations

import argparse
import datetime as dt
import importlib
import importlib.metadata as importlib_metadata
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def _find_repo_root() -> Path | None:
    """Walk up from this file to find repo root (identified by metadata/boards/).
    Returns None when running as an installed package without a local repo.
    从当前文件向上遍历目录，通过 metadata/boards/ 标记识别仓库根目录。
    以安装包形式运行时返回 None。"""
    env_root = os.environ.get("SEEED_ZEPHYR_REPO_ROOT")
    if env_root:
        candidate = Path(env_root).expanduser().resolve()
        if (candidate / "metadata" / "boards").is_dir():
            return candidate
        print(
            f"Warning: SEEED_ZEPHYR_REPO_ROOT={env_root} does not contain "
            "metadata/boards/; ignoring.",
            file=sys.stderr,
        )

    current = Path(__file__).resolve().parent
    for _ in range(8):
        if (current / "metadata" / "boards").is_dir():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


_REPO_ROOT = _find_repo_root()
# Bundled data directory for installed package mode
# 安装包模式下使用的打包数据目录
_PKG_DATA = Path(__file__).resolve().parent / "data"


def _display_path(p: Path) -> str:
    """Return a short display form: repo-relative when possible, otherwise the dir name.
    返回简短的显示路径：在仓库内时用相对路径，否则用目录名。"""
    if _REPO_ROOT and p.is_relative_to(_REPO_ROOT):
        return p.relative_to(_REPO_ROOT).as_posix()
    return p.name

BOARD_DIR = (_REPO_ROOT / "metadata" / "boards") if _REPO_ROOT else (_PKG_DATA / "boards")
EXAMPLES_DIR = (_REPO_ROOT / "examples" / "boards") if _REPO_ROOT else (_PKG_DATA / "examples")
GROVE_DIR = (_REPO_ROOT / "metadata" / "grove_modules") if _REPO_ROOT else (_PKG_DATA / "grove_modules")
EXPANSION_DIR = (
    (_REPO_ROOT / "metadata" / "expansion_boards") if _REPO_ROOT else (_PKG_DATA / "expansion_boards")
)
FORM_FACTOR_DIR = (
    (_REPO_ROOT / "metadata" / "form_factors") if _REPO_ROOT else (_PKG_DATA / "form_factors")
)
# Board-agnostic Grove examples live under examples/grove/<module_id>/<demo>/.
# 与具体板子解耦的 Grove 示例位于 examples/grove/<module_id>/<demo>/。
GROVE_EXAMPLES_DIR = (_REPO_ROOT / "examples" / "grove") if _REPO_ROOT else (_PKG_DATA / "grove_examples")
STATUS_DIR = (_REPO_ROOT / "metadata" / "status") if _REPO_ROOT else (_PKG_DATA / "status")
BUILD_MATRIX_SCRIPT = (_REPO_ROOT / "tools" / "build_matrix" / "run.sh") if _REPO_ROOT else None
HARDWARE_LOG = (_REPO_ROOT / "AI use" / "HARDWARE_VERIFICATION.md") if _REPO_ROOT else None
# Zephyr baseline version recorded in generated project snapshots.
# 写入生成项目 snapshot 的 Zephyr 基线版本号。
ZEPHYR_BASELINE = "v4.4.0"
DEBUG_HINT = (
    "Debugging needs a hardware debugger (J-Link, CMSIS-DAP, or on-chip "
    "USB-JTAG); most XIAO boards use printf-over-serial (`seeed-zephyr monitor`) "
    "for everyday debugging."
)
SAMD21_BOSSAC_DELAY_SECONDS = "3"
RP2_BOOTLOADER_SNIPPET = "rp2-boot-mode-retention"
RP2_BOOTLOADER_BAUD = 1200
RP2_BOOTLOADER_TOUCH_SECONDS = 1.5
RP2_BOOTLOADER_WAIT_SECONDS = 10
SERIAL_READY_WAIT_SECONDS = 10
SERIAL_READY_POLL_SECONDS = 0.5
UF2_RUNNER_BOARD_IDS = {"xiao_nrf52840"}
MG24_BOARD_ID = "xiao_mg24"
MG24_PYOCD_TARGET = "EFR32MG24B220F1536IM48"
RA4M1_BOARD_ID = "xiao_ra4m1"
RA4M1_DFU_VID_PID = "2886:0049,:8049"
RA4M1_DFU_RUNTIME_ID = "2886:0049"
RA4M1_DFU_BOOTLOADER_ID = "2886:8049"
RA4M1_ROM_BOOT_VID = "045b"
RA4M1_ROM_BOOT_PID = "0261"
RA4M1_DFU_ALT = "0"
RA4M1_DFU_MAX_IMAGE_BYTES = 0x40000 - 0x4000
RA4M1_DFU_WAIT_SECONDS = 10
RA4M1_DFU_POLL_SECONDS = 0.5
RA4M1_ROM_FLASH_SCRIPT = Path(__file__).resolve().parent / "ra4m1_rom_flash.py"
RA4M1_DFU_BOOTLOADER_BIN = Path(__file__).resolve().parent / "bootloaders" / "ra4m1_dfu.bin"


class CliError(Exception):
    pass


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        args.func(args)
    except CliError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        return 130

    return 0


def add_json_flag(parser: argparse.ArgumentParser) -> None:
    # Adds an opt-in machine-readable JSON output flag.
    # 添加一个可选的机器可读 JSON 输出标志。
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Emit machine-readable JSON instead of text.",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="seeed-zephyr",
        description="Operate Seeed XIAO + Grove Zephyr repository examples.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List repository assets.")
    list_subparsers = list_parser.add_subparsers(dest="asset", required=True)
    list_boards = list_subparsers.add_parser("boards", help="List XIAO boards.")
    add_json_flag(list_boards)
    list_boards.set_defaults(func=cmd_list_boards)
    list_examples = list_subparsers.add_parser(
        "examples", help="List board examples."
    )
    add_json_flag(list_examples)
    list_examples.set_defaults(func=cmd_list_examples)
    list_grove = list_subparsers.add_parser("grove", help="List Grove modules.")
    add_json_flag(list_grove)
    list_grove.set_defaults(func=cmd_list_grove)
    list_expansion = list_subparsers.add_parser("expansion", help="List expansion boards.")
    add_json_flag(list_expansion)
    list_expansion.set_defaults(func=cmd_list_expansion)

    show_parser = subparsers.add_parser(
        "show", help="Show details for a board or example."
    )
    show_subparsers = show_parser.add_subparsers(dest="asset", required=True)
    show_board = show_subparsers.add_parser("board", help="Show board details.")
    show_board.add_argument("board_id", help="Board id such as xiao_esp32c6.")
    add_json_flag(show_board)
    show_board.set_defaults(func=cmd_show_board)
    show_example = show_subparsers.add_parser("example", help="Show example details.")
    show_example.add_argument(
        "board_id",
        help="Board id (for a board example), or grove/<module>/<demo> for a Grove example.",
    )
    show_example.add_argument(
        "demo",
        nargs="?",
        default=None,
        help="Demo name for a board example, such as blinky.",
    )
    add_json_flag(show_example)
    show_example.set_defaults(func=cmd_show_example)
    show_pins = show_subparsers.add_parser(
        "pins", help="Show pin states for a board and example (data source for the pinout diagram)."
    )
    show_pins.add_argument("board_id", help="Board id such as xiao_nrf52840.")
    show_pins.add_argument(
        "example_ref",
        help="Example reference: grove/<module>/<demo>, or a board demo name such as blinky.",
    )
    add_json_flag(show_pins)
    show_pins.set_defaults(func=cmd_show_pins)

    build = subparsers.add_parser("build", help="Build a board or Grove example.")
    build.add_argument("board_id", help="Board id such as xiao_esp32c6.")
    build.add_argument(
        "example",
        nargs="?",
        default=None,
        help="Board demo name (blinky) or grove/<module>/<demo>. Omit to select interactively.",
    )
    build.add_argument(
        "--app",
        default=None,
        help="Path to an external Zephyr application directory.",
    )
    build.add_argument(
        "--pin",
        dest="pins",
        action="append",
        default=None,
        metavar="Dn|role=Dn",
        help="Grove pin assignment, e.g. --pin D2 or --pin data=D2. Repeatable per role.",
    )
    build.set_defaults(func=cmd_build)

    flash = subparsers.add_parser("flash", help="Build and flash a board or Grove example.")
    flash.add_argument("board_id", help="Board id such as xiao_esp32c6.")
    flash.add_argument(
        "example",
        nargs="?",
        default=None,
        help="Board demo name (blinky) or grove/<module>/<demo>. Omit to select interactively.",
    )
    flash.add_argument(
        "--app",
        default=None,
        help="Path to an external Zephyr application directory.",
    )
    flash.add_argument(
        "--monitor",
        action="store_true",
        help="Open the board monitor after a successful flash.",
    )
    flash.add_argument(
        "--port",
        default=None,
        help="Serial port for flashing and --monitor when supported.",
    )
    flash.add_argument(
        "--baud",
        type=int,
        default=115200,
        help="Serial baud rate for --monitor (default: 115200).",
    )
    flash.add_argument(
        "--pin",
        dest="pins",
        action="append",
        default=None,
        metavar="Dn|role=Dn",
        help="Grove pin assignment, e.g. --pin D2 or --pin data=D2. Repeatable per role.",
    )
    flash.set_defaults(func=cmd_flash)

    debug = subparsers.add_parser("debug", help="Build and start a board debug session.")
    debug.add_argument("board_id", help="Board id such as xiao_esp32c6.")
    debug.add_argument(
        "example",
        nargs="?",
        default=None,
        help="Board demo name (blinky) or grove/<module>/<demo>. Omit to select interactively.",
    )
    debug.add_argument(
        "--app",
        default=None,
        help="Path to an external Zephyr application directory.",
    )
    debug.add_argument(
        "--pin",
        dest="pins",
        action="append",
        default=None,
        metavar="Dn|role=Dn",
        help="Grove pin assignment, e.g. --pin D2 or --pin data=D2. Repeatable per role.",
    )
    debug.set_defaults(func=cmd_debug)

    monitor = subparsers.add_parser("monitor", help="Open a board monitor.")
    monitor.add_argument(
        "board_id",
        nargs="?",
        default=None,
        help="Board id such as xiao_esp32c6. Omit for interactive port selection.",
    )
    monitor.add_argument("--port", default=None, help="Serial port device path.")
    monitor.add_argument(
        "--baud",
        type=int,
        default=None,
        help="Serial baud rate (default: 115200).",
    )
    monitor.set_defaults(func=cmd_monitor)

    info = subparsers.add_parser("info", help="Show CLI version and data source.")
    add_json_flag(info)
    info.set_defaults(func=cmd_info)

    matrix = subparsers.add_parser("matrix", help="Run the full board build matrix.")
    matrix.set_defaults(func=cmd_matrix)

    verify = subparsers.add_parser(
        "verify-hardware", help="Build, flash, and record hardware observation."
    )
    verify.add_argument("board_id", help="Board id such as xiao_esp32c6.")
    verify.set_defaults(func=cmd_verify_hardware)

    create = subparsers.add_parser(
        "create", help="Create a project from a repository example."
    )
    create.add_argument(
        "--from",
        dest="from_asset",
        required=True,
        help="Source asset, such as xiao_esp32c6/blinky.",
    )
    create.add_argument(
        "--board",
        dest="board_id",
        required=True,
        help="Board id the project targets, such as xiao_esp32c6.",
    )
    create.add_argument(
        "--output",
        dest="output",
        required=True,
        help="Destination directory for the generated project.",
    )
    create.add_argument(
        "--force",
        action="store_true",
        help="Write into the output directory even when it is not empty.",
    )
    create.add_argument(
        "--pin",
        dest="pins",
        action="append",
        default=None,
        metavar="Dn|role=Dn",
        help="Grove pin assignment baked into the generated project, e.g. --pin D2.",
    )
    create.set_defaults(func=cmd_create)

    update = subparsers.add_parser(
        "update", help="Update seeed-zephyr and bundled repository assets."
    )
    update.add_argument(
        "--version",
        default=None,
        help="Install or select a specific seeed-zephyr version, tag, or commit.",
    )
    update.set_defaults(func=cmd_update)

    validate_parser = subparsers.add_parser("validate", help="Validate repository assets.")
    validate_subparsers = validate_parser.add_subparsers(dest="asset", required=True)
    validate_metadata = validate_subparsers.add_parser("metadata", help="Validate all metadata.")
    validate_metadata.set_defaults(func=cmd_validate_metadata)

    return parser


def read_flat_yaml(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}

    # This parser reads only the flat scalar fields used by repository metadata.
    # 这个解析器只读取仓库元数据里使用的扁平标量字段。
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue

        key, value = line.split(":", 1)
        values[key.strip()] = read_flat_yaml_scalar(value.strip())

    return values


def read_flat_yaml_scalar(value: str) -> str:
    # Normalizes the flat scalar syntax used by repository metadata.
    # 规范化仓库元数据使用的扁平标量语法。
    if value in {"[]", "null"}:
        return ""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def parse_scalar_or_list(value: str) -> str | list[str]:
    # Parses an inline YAML scalar or flow list such as "[D0, D1, D2]".
    # 解析行内 YAML 标量或流式列表，如 "[D0, D1, D2]"。
    value = value.strip()
    if value == "[]":
        return []
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [read_flat_yaml_scalar(part.strip()) for part in inner.split(",")]
    return read_flat_yaml_scalar(value)


def read_structured_yaml(path: Path) -> dict[str, object]:
    # Parses scalars, flow lists, block string lists, and one-level block list-of-mappings.
    # Zero-dependency; covers grove example.yaml and board pin metadata.
    # 解析标量、流式列表、块字符串列表和一层块映射列表；零依赖；覆盖 grove example.yaml 与板引脚 metadata。
    values: dict[str, object] = {}
    lines = path.read_text(encoding="utf-8").splitlines()
    i = 0
    n = len(lines)
    while i < n:
        raw = lines[i]
        if not raw.strip() or raw.strip().startswith("#"):
            i += 1
            continue
        if not raw[0].isspace() and ":" in raw:
            key, rest = raw.split(":", 1)
            key = key.strip()
            rest = rest.strip()
            if rest == "":
                if i + 1 < n and lines[i + 1].lstrip().startswith("-"):
                    # _parse_yaml_block_list returns i pointing at the next unprocessed line,
                    # so the outer loop must continue from there without an extra increment.
                    # _parse_yaml_block_list 返回的 i 已指向下一条未处理行,外层循环直接从该行继续。
                    items, i = _parse_yaml_block_list(lines, i + 1)
                    values[key] = items
                else:
                    values[key] = ""
                    i += 1
            else:
                values[key] = parse_scalar_or_list(rest)
                i += 1
        else:
            i += 1
    return values


def _parse_yaml_block_list(lines: list[str], start: int) -> tuple[list[object], int]:
    items: list[object] = []
    i = start
    n = len(lines)
    while i < n:
        raw = lines[i]
        if not raw.strip() or raw.strip().startswith("#"):
            i += 1
            continue
        if not raw[0].isspace():
            break
        stripped = raw.strip()
        if not stripped.startswith("-"):
            break
        after_dash = stripped[1:].strip()
        dash_indent = len(raw) - len(raw.lstrip(" \t"))
        if ":" in after_dash and not _starts_quoted(after_dash):
            mapping: dict[str, object] = {}
            k, v = after_dash.split(":", 1)
            mapping[k.strip()] = parse_scalar_or_list(v)
            i += 1
            while i < n:
                sub = lines[i]
                if not sub.strip() or sub.strip().startswith("#"):
                    i += 1
                    continue
                sub_indent = len(sub) - len(sub.lstrip(" \t"))
                if sub_indent <= dash_indent:
                    break
                sub_stripped = sub.strip()
                if sub_stripped.startswith("-"):
                    break
                if ":" in sub_stripped:
                    sk, sv = sub_stripped.split(":", 1)
                    mapping[sk.strip()] = parse_scalar_or_list(sv)
                i += 1
            items.append(mapping)
        else:
            items.append(read_flat_yaml_scalar(after_dash))
            i += 1
    return items, i


def _starts_quoted(text: str) -> bool:
    return bool(text) and text[0] in {"'", '"'}


def _yaml_indent(line: str) -> int:
    return len(line) - len(line.lstrip(" \t"))


def load_yaml_subset(text: str) -> object:
    # Minimal YAML-subset parser: mappings, block lists (scalar and mapping items),
    # flow lists, and scalars. Zero-dependency; used for the nested form-factor file.
    # 极简 YAML 子集解析器:映射、块列表(标量项与映射项)、流式列表、标量。零依赖;用于嵌套的形态因子文件。
    lines = [ln for ln in text.splitlines() if ln.strip() and not ln.strip().startswith("#")]
    if not lines:
        return {}
    value, _ = _yaml_parse_block(lines, 0, -1)
    return value if isinstance(value, dict) else {}


def _yaml_parse_block(lines: list[str], i: int, parent_indent: int) -> tuple[object, int]:
    indent = _yaml_indent(lines[i])
    content = lines[i][indent:]
    if content.lstrip().startswith("-"):
        return _yaml_parse_list(lines, i, indent)
    return _yaml_parse_mapping(lines, i, indent)


def _yaml_parse_mapping(lines: list[str], i: int, indent: int) -> tuple[dict[str, object], int]:
    mapping: dict[str, object] = {}
    n = len(lines)
    while i < n:
        line = lines[i]
        ind = _yaml_indent(line)
        if ind < indent:
            break
        if ind != indent:
            i += 1
            continue
        content = line[ind:]
        if content.lstrip().startswith("-"):
            break
        key, rest = content.split(":", 1)
        key = key.strip()
        rest = rest.strip()
        if rest:
            mapping[key] = parse_scalar_or_list(rest)
            i += 1
        else:
            j = i + 1
            if j < n and _yaml_indent(lines[j]) > ind:
                mapping[key], i = _yaml_parse_block(lines, j, ind)
            else:
                mapping[key] = ""
                i += 1
    return mapping, i


def _yaml_parse_list(lines: list[str], i: int, indent: int) -> tuple[list[object], int]:
    items: list[object] = []
    n = len(lines)
    while i < n:
        line = lines[i]
        ind = _yaml_indent(line)
        if ind < indent:
            break
        if ind != indent:
            i += 1
            continue
        content = line[ind:]
        stripped = content.strip()
        if not stripped.startswith("-"):
            break
        after = stripped[1:]
        after_lstrip = after.lstrip()
        if after_lstrip == "":
            j = i + 1
            if j < n and _yaml_indent(lines[j]) > ind:
                value, i = _yaml_parse_block(lines, j, ind)
                items.append(value)
            else:
                items.append("")
                i += 1
        elif ":" in after_lstrip and not _starts_quoted(after_lstrip):
            k, v = after_lstrip.split(":", 1)
            mapping: dict[str, object] = {}
            if v.strip():
                mapping[k.strip()] = parse_scalar_or_list(v)
                i += 1
            else:
                j = i + 1
                if j < n and _yaml_indent(lines[j]) > ind + 1:
                    value, i = _yaml_parse_block(lines, j, ind)
                    mapping[k.strip()] = value
                else:
                    mapping[k.strip()] = ""
                    i += 1
            # Consume subsequent deeper-indented lines as additional mapping entries.
            # 继续消费更深缩进的行作为该映射项的其余字段。
            while i < n:
                nl = lines[i]
                if not nl.strip():
                    i += 1
                    continue
                ni = _yaml_indent(nl)
                if ni <= ind:
                    break
                nc = nl[ni:]
                if nc.lstrip().startswith("-"):
                    break
                if ":" in nc:
                    nk, nv = nc.split(":", 1)
                    if nv.strip():
                        mapping[nk.strip()] = parse_scalar_or_list(nv)
                        i += 1
                    else:
                        j = i + 1
                        if j < n and _yaml_indent(lines[j]) > ni:
                            value, i = _yaml_parse_block(lines, j, ni)
                            mapping[nk.strip()] = value
                        else:
                            mapping[nk.strip()] = ""
                            i += 1
                else:
                    i += 1
            items.append(mapping)
        else:
            items.append(read_flat_yaml_scalar(after_lstrip))
            i += 1
    return items, i


def load_form_factor(form_factor_id: str = "xiao") -> dict[str, object]:
    path = FORM_FACTOR_DIR / f"{form_factor_id}.yaml"
    if not path.is_file():
        raise CliError(f"Form factor metadata not found: {path}")
    data = load_yaml_subset(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise CliError(f"Form factor metadata is malformed: {path}")
    return data


def read_example_status(example_id: str) -> dict[str, str]:
    # Reads the example x board status matrix from metadata/status/<example_id>.yaml.
    # 从 metadata/status/<example_id>.yaml 读取"示例 x 板子"状态矩阵。
    path = STATUS_DIR / f"{example_id}.yaml"
    if not path.is_file():
        return {}
    values = read_structured_yaml(path)
    boards = values.get("boards")
    if not isinstance(boards, list):
        return {}
    statuses: dict[str, str] = {}
    for entry in boards:
        if isinstance(entry, dict) and entry.get("board_id") and entry.get("status"):
            statuses[str(entry["board_id"])] = str(entry["status"])
    return statuses


def board_records() -> list[dict[str, str]]:
    records: list[dict[str, str]] = []

    for board_file in sorted(BOARD_DIR.glob("*.yaml")):
        values = read_flat_yaml(board_file)
        board_id = values.get("id", board_file.stem)
        example = resolve_example(board_id)
        status = example.get("validation_status", "unknown") if example else "missing"
        demo = example.get("demo", "missing") if example else "missing"
        records.append(
            {
                "id": board_id,
                "display_name": values.get("display_name", board_id),
                "vendor": values.get("vendor", ""),
                "target": values.get("zephyr_target", ""),
                "demo": demo,
                "status": status,
                "example_path": (
                    _display_path(Path(example["path"])) if example and example.get("path") else ""
                ),
            }
        )

    return records


def resolve_example(board_id: str) -> dict[str, str] | None:
    board_example_dir = EXAMPLES_DIR / board_id
    if not board_example_dir.is_dir():
        return None

    example_files = sorted(board_example_dir.glob("*/example.yaml"))
    if not example_files:
        return None

    chosen = example_files[0]
    # Prefer a buildable example when a board also has an unsupported placeholder.
    # 当一个开发板同时有不可用占位示例时，优先选择可构建示例。
    for example_file in example_files:
        values = read_flat_yaml(example_file)
        if values.get("validation_status") != "unsupported":
            chosen = example_file
            break

    values = read_flat_yaml(chosen)
    values["path"] = str(chosen.parent)
    return values


def resolve_board_examples(board_id: str) -> list[dict[str, str]]:
    # Returns all examples for a board, each with a 'path' and 'demo' field.
    # 返回一个板的所有 example，每个包含 'path' 和 'demo' 字段。
    board_example_dir = EXAMPLES_DIR / board_id
    if not board_example_dir.is_dir():
        return []

    examples = []
    for example_file in sorted(board_example_dir.glob("*/example.yaml")):
        values = read_flat_yaml(example_file)
        values["path"] = str(example_file.parent)
        examples.append(values)
    return examples


def select_example(board_id: str, example_name: str | None = None) -> dict[str, object]:
    # Selects an example by name, or interactively when multiple are available.
    # Accepts a plain board demo name ("blinky") or a grove reference ("grove/<module>/<demo>").
    # 按名称选择 example，多个可用时交互选择；接受板级 demo 名或 grove 引用。
    require_board(board_id)

    if example_name is not None and example_name.startswith("grove/"):
        return select_grove_example(board_id, example_name)

    examples = resolve_board_examples(board_id)
    supported = [e for e in examples if e.get("validation_status") != "unsupported"]

    if not examples:
        if example_name is not None and GROVE_EXAMPLES_DIR.is_dir():
            raise CliError(
                f"No board example found for {board_id}. "
                "Use a grove reference like grove/<module>/<demo> for a Grove module."
            )
        raise CliError(f"No repository example found for {board_id}.")
    if not supported:
        raise CliError(f"{board_id} is unsupported in the selected Zephyr baseline.")

    if example_name is not None:
        for ex in supported:
            if ex.get("demo") == example_name:
                return ex
        available = ", ".join(ex.get("demo", "?") for ex in supported)
        raise CliError(
            f"Example '{example_name}' not found for {board_id}. "
            f"Available: {available}"
        )

    if len(supported) == 1:
        return supported[0]

    print(f"\nAvailable examples for {board_id}:", flush=True)
    for i, ex in enumerate(supported, 1):
        demo = ex.get("demo", "unknown")
        status = ex.get("validation_status", "")
        print(f"  [{i}] {demo}  ({status})", flush=True)
    while True:
        choice = input(f"Select example [1]: ").strip()
        if not choice:
            return supported[0]
        try:
            index = int(choice)
            if 1 <= index <= len(supported):
                return supported[index - 1]
        except ValueError:
            pass
        print(f"  Enter a number between 1 and {len(supported)}.", flush=True)


def select_grove_example(board_id: str, ref: str) -> dict[str, object]:
    # Resolves a grove/<module>/<demo> reference for a specific board.
    # 为指定板解析 grove/<module>/<demo> 引用。
    module_id, demo = parse_grove_ref(ref)

    if not demo:
        demos = sorted(
            p.parent.name
            for p in grove_example_dirs()
            if p.parent.parent.name == module_id
        )
        if not demos:
            raise CliError(
                f"Grove module '{module_id}' has no examples. "
                "Run 'seeed-zephyr list grove' to see available modules."
            )
        if len(demos) == 1:
            demo = demos[0]
        else:
            raise CliError(
                f"Specify a demo for {module_id}. Available: {', '.join(demos)}."
            )
        ref = f"{module_id}/{demo}"

    example = resolve_grove_example(module_id, demo)
    if not grove_supports_board(example, board_id):
        raise CliError(
            f"Grove example {module_id}/{demo} excludes board '{board_id}'. "
            f"Excluded boards: {', '.join(grove_excluded_boards(example)) or 'none'}."
        )
    return example


# --- Grove pin assignment -----------------------------------------------------
# A selectable Grove module declares pin roles (signal / data / clock ...). The CLI
# computes the valid pin set per board (declared allowed minus board reserved pins)
# and materializes a devicetree overlay from a template for the build.
# 可选引脚的 Grove 模块声明引脚角色；CLI 按板计算有效引脚集合，并由模板生成 devicetree overlay。


def pin_index(pin: str) -> int:
    # Maps a physical pin name such as "D2" to its connector position index.
    # 将物理引脚名（如 D2）映射为 connector 位置索引。
    pin = pin.strip().upper()
    match = re.fullmatch(r"D(\d+)", pin)
    if not match:
        raise CliError(f"Invalid pin '{pin}'. Use the form D0..D10.")
    index = int(match.group(1))
    if index < 0 or index > 15:
        raise CliError(f"Pin '{pin}' is out of the XIAO connector range.")
    return index


def board_reserved_pins(board_id: str) -> dict[str, str]:
    values = read_structured_yaml(BOARD_DIR / f"{board_id}.yaml")
    reserved = values.get("reserved_pins")
    if not isinstance(reserved, list):
        return {}
    result: dict[str, str] = {}
    for entry in reserved:
        if isinstance(entry, dict) and entry.get("pin") and entry.get("reason"):
            result[str(entry["pin"])] = str(entry["reason"])
    return result


def board_analog_pins(board_id: str) -> set[str]:
    values = read_structured_yaml(BOARD_DIR / f"{board_id}.yaml")
    analog = values.get("analog_pins")
    if isinstance(analog, list):
        return {str(p) for p in analog}
    return set()


def board_pin_map(board_id: str) -> dict[str, str]:
    # Official Dn -> chip pin name baseline from board metadata (audits upstream dtsi).
    # 来自板 metadata 的官方 Dn -> 芯片引脚名基准表(用于审计上游 dtsi)。
    values = read_structured_yaml(BOARD_DIR / f"{board_id}.yaml")
    pin_map = values.get("pin_map")
    if not isinstance(pin_map, list):
        return {}
    result: dict[str, str] = {}
    for entry in pin_map:
        if isinstance(entry, dict) and entry.get("pin") and entry.get("chip_pin"):
            result[str(entry["pin"])] = str(entry["chip_pin"])
    return result


def resolve_pin_assignment(
    example: dict[str, object], board_id: str, pins_arg: list[str] | None
) -> dict[str, str]:
    # Validates user-supplied --pin values against the example and board, then returns
    # a {role: pin} map. fixed-bus examples reject --pin; selectable examples default
    # any unassigned role.
    # 校验 --pin 取值并返回 {role: pin}；fixed-bus 示例拒绝 --pin，selectable 示例对未指定角色用默认值。
    policy = example.get("pin_policy")
    if policy != "selectable":
        if pins_arg:
            raise CliError(
                f"This example uses pin_policy={policy}; --pin is not applicable. "
                "Fixed-bus modules connect to the XIAO I2C/SPI/UART pins directly."
            )
        return {}

    declared = example.get("pins")
    if not isinstance(declared, list) or not declared:
        raise CliError("Example declares pin_policy=selectable but lists no pins.")
    roles: dict[str, dict[str, object]] = {}
    for spec in declared:
        if isinstance(spec, dict) and spec.get("role"):
            roles[str(spec["role"])] = spec
    if not roles:
        raise CliError("Example declares pin_policy=selectable but lists no pin roles.")

    reserved = board_reserved_pins(board_id)
    single_role: str | None = next(iter(roles)) if len(roles) == 1 else None
    assignments: dict[str, str] = {}

    for item in pins_arg or []:
        if "=" in item:
            role, pin = item.split("=", 1)
            role, pin = role.strip(), pin.strip()
        else:
            if not single_role:
                raise CliError(
                    f"Use --pin role=Dn for this module. Roles: {', '.join(sorted(roles))}."
                )
            role, pin = single_role, item.strip()
        if role not in roles:
            raise CliError(f"Unknown pin role '{role}'. Roles: {', '.join(sorted(roles))}.")
        spec = roles[role]
        allowed = [str(p) for p in (spec.get("allowed") or [])]
        if pin not in allowed:
            raise CliError(
                f"Pin '{pin}' is not allowed for role '{role}'. Allowed: {', '.join(allowed)}."
            )
        if pin in reserved:
            available = [p for p in allowed if p not in reserved]
            raise CliError(
                f"Pin '{pin}' is reserved on {board_id} ({reserved[pin]}). "
                f"Available for '{role}': {', '.join(available)}."
            )
        assignments[role] = pin

    for role, spec in roles.items():
        if role in assignments:
            continue
        default = str(spec.get("default", ""))
        allowed = [str(p) for p in (spec.get("allowed") or [])]
        if default in reserved:
            available = [p for p in allowed if p not in reserved]
            raise CliError(
                f"Default pin '{default}' for role '{role}' is reserved on {board_id} "
                f"({reserved[default]}). Specify --pin {role}=<Dn>. "
                f"Available: {', '.join(available)}."
            )
        assignments[role] = default
    return assignments


def generate_pin_overlay(example: dict[str, object], assignments: dict[str, str]) -> str | None:
    # Renders pins/pin.overlay.in with @PIN_<ROLE>@ placeholders into a temp overlay.
    # 将 pins/pin.overlay.in 中的 @PIN_<ROLE>@ 占位符替换为引脚索引，写入临时 overlay。
    if not assignments:
        return None
    example_dir = Path(str(example["path"]))
    template = example_dir / "pins" / "pin.overlay.in"
    if not template.is_file():
        raise CliError(
            f"Example declares selectable pins but has no pins/pin.overlay.in template at {template}."
        )
    text = template.read_text(encoding="utf-8")
    for role, pin in assignments.items():
        placeholder = f"@PIN_{role.upper()}@"
        if placeholder not in text:
            raise CliError(
                f"Pin overlay template {template} is missing placeholder '{placeholder}' "
                f"for role '{role}'."
            )
        text = text.replace(placeholder, str(pin_index(pin)))
    fd, name = tempfile.mkstemp(prefix="grove_pin_", suffix=".overlay")
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(text)
    return name


def resolve_build_example(args: argparse.Namespace) -> tuple[dict[str, object], str | None]:
    # Shared by build/flash/debug: resolves the example, applies --pin, returns the
    # example dict and an optional extra devicetree overlay path.
    # build/flash/debug 共用：解析示例、应用 --pin、返回示例与可选 overlay 路径。
    if args.app:
        example = resolve_app_example(args.board_id, args.app)
        return example, None
    example = select_example(args.board_id, args.example)
    assignments = resolve_pin_assignment(example, args.board_id, getattr(args, "pins", None))
    overlay = generate_pin_overlay(example, assignments) if assignments else None
    return example, overlay


def resolve_app_example(board_id: str, app_path: str) -> dict[str, str]:
    # Builds an example dict from an external Zephyr application directory.
    # 从外部 Zephyr 应用目录构造 example 字典。
    app_dir = Path(app_path).expanduser().resolve()
    if not app_dir.is_dir():
        raise CliError(f"Application directory not found: {app_dir}")

    has_cmakelists = (app_dir / "CMakeLists.txt").exists()
    has_prj_conf = (app_dir / "prj.conf").exists()
    if not has_cmakelists:
        raise CliError(f"Not a Zephyr application: {app_dir} (CMakeLists.txt missing)")
    if not has_prj_conf:
        raise CliError(f"Not a Zephyr application: {app_dir} (prj.conf missing)")

    board = require_board(board_id)
    return {
        "path": str(app_dir),
        "demo": app_dir.name,
        "zephyr_target": board["target"],
        "validation_status": "external",
    }


# --- Grove example resolution -------------------------------------------------
# Grove examples are board-agnostic: one source tree builds for every XIAO board
# via the upstream seeed_xiao_connector abstraction.
# Grove 示例与板子解耦：一份源码通过上游 seeed_xiao_connector 抽象适配所有 XIAO 板。


def grove_example_dirs() -> list[Path]:
    if not GROVE_EXAMPLES_DIR.is_dir():
        return []
    return sorted(GROVE_EXAMPLES_DIR.glob("*/*/example.yaml"))


def resolve_grove_example(module_id: str, demo: str) -> dict[str, object]:
    example_file = GROVE_EXAMPLES_DIR / module_id / demo / "example.yaml"
    if not example_file.is_file():
        raise CliError(
            f"Grove example '{module_id}/{demo}' not found. "
            "Run 'seeed-zephyr list grove' to see available examples."
        )
    values = read_structured_yaml(example_file)
    values["path"] = str(example_file.parent)
    values["kind"] = "grove"
    return values


def resolve_grove_examples() -> list[dict[str, object]]:
    examples: list[dict[str, object]] = []
    for example_file in grove_example_dirs():
        values = read_structured_yaml(example_file)
        values["path"] = str(example_file.parent)
        values["kind"] = "grove"
        examples.append(values)
    return examples


def grove_excluded_boards(example: dict[str, object]) -> list[str]:
    excluded = example.get("excluded_boards")
    if isinstance(excluded, list):
        return [str(item) for item in excluded]
    return []


def grove_supports_board(example: dict[str, object], board_id: str) -> bool:
    return board_id not in grove_excluded_boards(example)


def parse_grove_ref(ref: str) -> tuple[str, str]:
    # Accepts grove/<module>/<demo>, grove/<module>, or <module>/<demo>.
    # 接受 grove/<module>/<demo>、grove/<module> 或 <module>/<demo>。
    parts = [p for p in ref.strip().strip("/").split("/") if p]
    if parts and parts[0] == "grove":
        parts = parts[1:]
    if len(parts) == 1:
        # Single-segment ref: treat as module id, pick its first demo later by caller.
        return parts[0], ""
    if len(parts) == 2:
        return parts[0], parts[1]
    raise CliError(
        f"Invalid grove example reference: {ref}. "
        "Use grove/<module_id>/<demo>, such as grove/grove_scd41_co2_temperature_humidity_sensor/basic_read."
    )


def require_board(board_id: str) -> dict[str, str]:
    for record in board_records():
        if record["id"] == board_id:
            return record

    available = ", ".join(record["id"] for record in board_records())
    raise CliError(f"Unknown board id: {board_id}. Available boards: {available}")


def require_supported_example(board_id: str) -> dict[str, str]:
    board = require_board(board_id)
    if not board["example_path"]:
        raise CliError(f"No repository example found for {board_id}.")
    if board["status"] == "unsupported":
        raise CliError(f"{board_id} is unsupported in the selected Zephyr baseline.")
    example = resolve_example(board_id)
    if example is None:
        raise CliError(f"No repository example found for {board_id}.")
    return example


def run_command(
    command: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None
) -> None:
    result = subprocess.run(command, cwd=cwd, env=env, check=False)
    if result.returncode != 0:
        raise CliError(f"Command failed with status {result.returncode}: {' '.join(command)}")


def run_command_capture(
    command: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        env=env,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def require_path_command(command: str, install_hint: str) -> None:
    # Verifies that a command is available before running an update command.
    # 执行更新命令前，确认指定命令已经在 PATH 中可用。
    if shutil.which(command) is None:
        raise CliError(f"{command} was not found. {install_hint}")


def read_repo_cli_version() -> str | None:
    # Reads the repository package version without importing package build code.
    # 直接读取仓库包版本，避免导入打包代码。
    if _REPO_ROOT is None:
        return None
    version_file = _REPO_ROOT / "packages" / "seeed-zephyr" / "src" / "seeed_zephyr" / "__init__.py"
    if not version_file.is_file():
        return None
    match = re.search(r'__version__\s*=\s*"([^"]+)"', version_file.read_text(encoding="utf-8"))
    return match.group(1) if match else None


def cli_version() -> str:
    if _REPO_ROOT is not None:
        return read_repo_cli_version() or "unknown"
    try:
        return importlib_metadata.version("seeed-zephyr")
    except importlib_metadata.PackageNotFoundError:
        return "unknown"


def package_build_commit() -> str | None:
    try:
        build_info = importlib.import_module("seeed_zephyr.build_info")
    except Exception:
        return None
    commit = getattr(build_info, "GIT_COMMIT", None)
    return commit if commit and commit != "unknown" else None


def git_output(repo_root: Path, args: list[str]) -> str | None:
    if shutil.which("git") is None:
        return None
    result = run_command_capture(["git", "-C", str(repo_root), *args])
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def repo_git_commit(repo_root: Path) -> str | None:
    return git_output(repo_root, ["rev-parse", "HEAD"])


def repo_git_branch(repo_root: Path) -> str | None:
    return git_output(repo_root, ["branch", "--show-current"]) or None


def repo_is_clean(repo_root: Path) -> bool:
    status = git_output(repo_root, ["status", "--porcelain"])
    return status == ""


def package_source() -> str:
    if _REPO_ROOT is not None:
        return "repo"
    if is_homebrew_install():
        return "homebrew"
    if is_pipx_install():
        return "pipx"
    try:
        importlib_metadata.distribution("seeed-zephyr")
    except importlib_metadata.PackageNotFoundError:
        return "unknown"
    return "pip"


def current_info() -> dict[str, str | None]:
    repo_root = str(_REPO_ROOT) if _REPO_ROOT else None
    commit = repo_git_commit(_REPO_ROOT) if _REPO_ROOT else package_build_commit()
    return {
        "cli_version": cli_version(),
        "install_mode": "repo" if _REPO_ROOT else "package",
        "package_source": package_source(),
        "data_source": "repo" if _REPO_ROOT else "bundled",
        "repo_root": repo_root,
        "git_branch": repo_git_branch(_REPO_ROOT) if _REPO_ROOT else None,
        "git_commit": commit,
        "git_dirty": str(not repo_is_clean(_REPO_ROOT)).lower() if _REPO_ROOT else None,
        "zephyr_baseline": ZEPHYR_BASELINE,
        "python": sys.executable,
    }


def print_info(info: dict[str, str | None]) -> None:
    labels = [
        ("CLI version", "cli_version"),
        ("Install mode", "install_mode"),
        ("Package source", "package_source"),
        ("Data source", "data_source"),
        ("Repository root", "repo_root"),
        ("Git branch", "git_branch"),
        ("Git commit", "git_commit"),
        ("Git dirty", "git_dirty"),
        ("Zephyr baseline", "zephyr_baseline"),
        ("Python", "python"),
    ]
    for label, key in labels:
        print(f"{label}: {info.get(key) or 'unknown'}")


def update_repo_checkout(repo_root: Path) -> None:
    # Updates a local repository checkout that supplies metadata and examples.
    # 更新提供 metadata 和 examples 的本地仓库签出。
    require_path_command("git", "Install Git, then rerun 'seeed-zephyr update'.")
    result = run_command_capture(
        ["git", "-C", str(repo_root), "rev-parse", "--is-inside-work-tree"]
    )
    if result.returncode != 0 or result.stdout.strip() != "true":
        raise CliError(f"Repository root is not a Git checkout: {repo_root}")

    print(f"Updating repository assets in {repo_root}...", flush=True)
    run_command(["git", "-C", str(repo_root), "pull", "--no-ff"])
    print("Update complete.", flush=True)
    print("Run 'seeed-zephyr list examples' to view the refreshed examples.", flush=True)


def checkout_repo_version(repo_root: Path, version: str) -> None:
    # Selects a repository tag, branch, or commit after confirming local cleanliness.
    # 在确认本地干净后，选择仓库 tag、分支或 commit。
    require_path_command("git", "Install Git, then rerun 'seeed-zephyr update'.")
    if not repo_is_clean(repo_root):
        raise CliError(
            "Repository has local changes. Commit or stash them before selecting a version."
        )

    print(f"Fetching tags for {repo_root}...", flush=True)
    run_command(["git", "-C", str(repo_root), "fetch", "--tags", "--force"])

    candidates = [version]
    if not version.startswith("v"):
        candidates.append(f"v{version}")
    candidates.append(f"seeed-zephyr-{version}")

    for candidate in candidates:
        result = run_command_capture(
            ["git", "-C", str(repo_root), "rev-parse", "--verify", f"{candidate}^{{commit}}"]
        )
        if result.returncode == 0:
            run_command(["git", "-C", str(repo_root), "checkout", candidate])
            print(f"Repository selected: {candidate}", flush=True)
            return

    raise CliError(
        f"Version, tag, branch, or commit not found: {version}. "
        "Use a published package version in package mode, or a Git ref in repo mode."
    )


def path_parts(path: Path) -> set[str]:
    # Normalizes path parts for installation-source detection.
    # 归一化路径片段，用于判断安装来源。
    try:
        resolved = path.resolve()
    except OSError:
        resolved = path
    return {part.lower() for part in resolved.parts}


def is_homebrew_install() -> bool:
    parts = path_parts(Path(sys.executable)) | path_parts(Path(sys.prefix))
    return "cellar" in parts and "seeed-zephyr" in parts


def is_pipx_install() -> bool:
    parts = path_parts(Path(sys.executable)) | path_parts(Path(sys.prefix))
    return "pipx" in parts and "seeed-zephyr" in parts


def installed_package_update_commands(version: str | None = None) -> tuple[str, list[list[str]]]:
    # Selects the package-manager command that should refresh this installation.
    # 选择应刷新当前安装的包管理器命令。
    if is_homebrew_install():
        if version is not None:
            raise CliError(
                "Homebrew-managed CLI version selection is not automatic. "
                "Use the editor extension managed CLI for older package versions."
            )
        require_path_command(
            "brew", "Add Homebrew to PATH, then rerun 'seeed-zephyr update'."
        )
        return "Homebrew", [["brew", "update"], ["brew", "upgrade", "seeed-zephyr"]]

    if is_pipx_install():
        require_path_command(
            "pipx", "Install pipx or add it to PATH, then rerun 'seeed-zephyr update'."
        )
        if version is not None:
            return "pipx", [["pipx", "install", "--force", f"seeed-zephyr=={version}"]]
        return "pipx", [["pipx", "upgrade", "seeed-zephyr"]]

    package = f"seeed-zephyr=={version}" if version else "seeed-zephyr"
    return "pip", [[sys.executable, "-m", "pip", "install", "--upgrade", package]]


def update_installed_package(version: str | None = None) -> None:
    source, commands = installed_package_update_commands(version)
    print(f"Updating seeed-zephyr with {source}...", flush=True)
    for command in commands:
        print(f"$ {' '.join(command)}", flush=True)
        run_command(command)
    print("Update complete.", flush=True)


def west_path() -> Path:
    workspace = Path(os.environ.get("ZEPHYR_WORKSPACE", str(Path.home() / "zephyrproject")))
    return workspace / ".venv" / "bin" / "west"


def zephyr_workspace() -> Path:
    return Path(os.environ.get("ZEPHYR_WORKSPACE", str(Path.home() / "zephyrproject")))


def zephyr_venv_python() -> Path:
    python = west_path().parent / "python3"
    if python.exists():
        return python

    python = west_path().parent / "python"
    if python.exists():
        return python

    raise CliError(f"Zephyr venv python was not found in: {west_path().parent}")


def west_command_env() -> dict[str, str]:
    env = os.environ.copy()
    venv_bin = str(west_path().parent)
    current_path = env.get("PATH", "")
    # Zephyr runners spawn tools such as esptool by name, so expose the venv bin.
    # Zephyr runner 会按命令名启动 esptool 等工具，因此要把 venv bin 放进 PATH。
    env["PATH"] = f"{venv_bin}{os.pathsep}{current_path}" if current_path else venv_bin
    return env


def run_west(command: list[str]) -> None:
    west = west_path()
    if not west.exists():
        raise CliError(f"west was not found: {west}")

    run_command([str(west), *command], cwd=zephyr_workspace(), env=west_command_env())


def run_west_capture(command: list[str]) -> subprocess.CompletedProcess[str]:
    west = west_path()
    if not west.exists():
        raise CliError(f"west was not found: {west}")

    return run_command_capture([str(west), *command], cwd=zephyr_workspace(), env=west_command_env())


def require_west_venv_tool(tool_name: str, install_hint: str) -> None:
    tool_path = west_path().parent / tool_name
    if not tool_path.exists():
        raise CliError(f"{tool_name} was not found: {tool_path}. {install_hint}")


def bossac_install_hint() -> str:
    system = platform.system().lower()
    release = platform.release().lower()

    if system == "darwin":
        return "Install it with: brew install bossa"
    if system == "linux":
        if "microsoft" in release:
            return (
                "Install it inside WSL2 with: sudo apt-get install bossa-cli, "
                "or sudo dnf install bossa"
            )
        return "Install it with: sudo apt-get install bossa-cli, or sudo dnf install bossa"
    if system == "windows":
        return "Use WSL2, then install it with: sudo apt-get install bossa-cli"

    return "Install BOSSA/bossac for this platform"


def samd21_bootloader_hint(port: str | None) -> str:
    port_hint = f" Current port: {port}." if port else ""
    return (
        "XIAO SAMD21 flashing uses the SAMD bootloader through bossac."
        f"{port_hint} Double-tap RESET, wait for the bootloader serial port "
        "to appear, then rerun the flash command. If more than one USB serial "
        "device is attached, pass the bootloader port with --port <device>."
    )


def uf2_bootloader_hint(board_id: str) -> str:
    if board_id == "xiao_nrf52840":
        return (
            "XIAO nRF52840 flashing uses Zephyr's UF2 runner with the Adafruit "
            "nRF52 Bootloader. If the current firmware does not support USB CDC "
            "1200 baud bootloader requests yet, double-tap RESET once, wait for "
            "the UF2 mass storage volume to appear, then rerun the flash command. "
            "After repository firmware is installed, later flashes should enter "
            "UF2 automatically."
        )

    return (
        f"{board_id} flashing uses Zephyr's UF2 runner. If the current firmware "
        "does not expose an automatic UF2 request path, hold BOOTSEL while "
        "plugging in USB, or hold BOOTSEL and press RESET, then wait for the "
        "UF2 mass storage volume to appear and rerun the flash command."
    )


def require_host_tool(tool_name: str, install_hint: str) -> None:
    if shutil.which(tool_name, path=west_command_env().get("PATH")) is None:
        raise CliError(f"{tool_name} was not found. {install_hint}.")


def pyocd_path() -> Path:
    return west_path().parent / "pyocd"


def mg24_pyocd_pack_hint() -> str:
    return (
        "XIAO MG24 flashing uses Zephyr's pyocd runner. "
        f"Install the CMSIS pack with: {pyocd_path()} pack install {MG24_PYOCD_TARGET}."
    )


def pyocd_target_available(target: str) -> bool:
    # Checks pyOCD's installed target list for the selected CMSIS pack target.
    # 检查 pyOCD 已安装 target 列表中是否包含选定的 CMSIS pack target。
    pyocd = pyocd_path()
    if not pyocd.exists():
        return False

    result = run_command_capture(
        [str(pyocd), "list", "--targets"],
        cwd=zephyr_workspace(),
        env=west_command_env(),
    )
    return result.returncode == 0 and target.lower() in result.stdout.lower()


def require_mg24_pyocd_pack() -> None:
    if not pyocd_target_available(MG24_PYOCD_TARGET):
        raise CliError(mg24_pyocd_pack_hint())


def dfu_util_path() -> Path | None:
    path = shutil.which("dfu-util", path=west_command_env().get("PATH"))
    if path is None:
        return None
    return Path(path)


def dfu_util_install_hint() -> str:
    if _REPO_ROOT:
        return (
            "XIAO RA4M1 flashing uses the board USB DFU bootloader. "
            "Run scripts/setup-macos.sh --board xiao_ra4m1 or "
            "scripts/setup-linux.sh --board xiao_ra4m1 so setup installs dfu-util."
        )
    system = platform.system().lower()
    if system == "darwin":
        return "XIAO RA4M1 flashing requires dfu-util. Install it with: brew install dfu-util"
    return "XIAO RA4M1 flashing requires dfu-util. Install it with: sudo apt-get install dfu-util"


def require_ra4m1_dfu_util() -> None:
    if dfu_util_path() is None:
        raise CliError(f"dfu-util was not found. {dfu_util_install_hint()}")


def require_flash_tools(board_id: str, rom_boot: bool = False) -> None:
    board = require_board(board_id)
    if board["vendor"] == "espressif":
        require_west_venv_tool(
            "esptool",
            "Run setup again, or install it with: "
            f"{zephyr_workspace()}/.venv/bin/python -m pip install esptool",
        )
    if board["target"] == "seeeduino_xiao":
        require_host_tool("bossac", bossac_install_hint())
    if board["id"] == MG24_BOARD_ID:
        require_mg24_pyocd_pack()
    if board["id"] == RA4M1_BOARD_ID and not rom_boot:
        require_ra4m1_dfu_util()


def zephyr_objcopy_path() -> Path:
    path = shutil.which("arm-zephyr-eabi-objcopy", path=west_command_env().get("PATH"))
    if path is not None:
        return Path(path)

    for sdk_dir in sorted(Path.home().glob("zephyr-sdk-*"), reverse=True):
        candidate = sdk_dir / "gnu" / "arm-zephyr-eabi" / "bin" / "arm-zephyr-eabi-objcopy"
        if candidate.exists():
            return candidate

    raise CliError(
        "arm-zephyr-eabi-objcopy was not found. Rerun setup so the Zephyr SDK is installed."
    )


def prepare_ra4m1_dfu_image() -> Path:
    build_zephyr_dir = zephyr_workspace() / "build" / "zephyr"
    elf_file = build_zephyr_dir / "zephyr.elf"
    image_file = build_zephyr_dir / "zephyr.ra4m1.dfu.bin"

    if not elf_file.exists():
        raise CliError(f"Zephyr ELF was not found: {elf_file}")

    run_command(
        [
            str(zephyr_objcopy_path()),
            "-O",
            "binary",
            "-R",
            ".option_setting_osis",
            str(elf_file),
            str(image_file),
        ],
        cwd=zephyr_workspace(),
        env=west_command_env(),
    )

    image_size = image_file.stat().st_size
    if image_size > RA4M1_DFU_MAX_IMAGE_BYTES:
        raise CliError(
            f"RA4M1 DFU image is too large: {image_size} bytes. "
            f"Maximum is {RA4M1_DFU_MAX_IMAGE_BYTES} bytes."
        )

    return image_file


def run_ra4m1_rom_flash(rom_port: str) -> str | None:
    # Flashes firmware through the Renesas ROM bootloader serial protocol.
    # 通过 Renesas ROM bootloader 串口协议烧录固件。
    app_image = prepare_ra4m1_dfu_image()
    combined_image = app_image.parent / "zephyr.ra4m1.combined.bin"

    bootloader_bytes = RA4M1_DFU_BOOTLOADER_BIN.read_bytes()
    app_bytes = app_image.read_bytes()
    # Combines the factory DFU bootloader at 0x0 with the offset app image at 0x4000.
    # 将出厂 DFU bootloader 放在 0x0，并把偏移后的应用镜像接在 0x4000 之后。
    combined_image.write_bytes(bootloader_bytes + app_bytes)

    python = zephyr_venv_python()
    run_command(
        [str(python), str(RA4M1_ROM_FLASH_SCRIPT), rom_port, str(combined_image)],
        cwd=zephyr_workspace(),
        env=west_command_env(),
    )
    return None


def ra4m1_bootloader_hint(port: str | None) -> str:
    port_hint = f" Current port: {port}." if port else ""
    return (
        "XIAO RA4M1 flashing uses the board USB DFU bootloader."
        f"{port_hint} If this is the first repository firmware install, hold BOOT, "
        "tap RESET, keep holding BOOT for 1 to 2 seconds, then rerun the flash "
        "command. After repository firmware is installed, later flashes should "
        "enter DFU automatically. If the board DFU bootloader is missing, enter "
        "ROM Boot mode (hold BOOT, tap RESET) and rerun the flash command."
    )


def ra4m1_dfu_device_available() -> bool:
    dfu_util = dfu_util_path()
    if dfu_util is None:
        raise CliError(f"dfu-util was not found. {dfu_util_install_hint()}")

    result = run_command_capture(
        [str(dfu_util), "--list"], cwd=zephyr_workspace(), env=west_command_env()
    )
    output = result.stdout.lower()
    return (
        RA4M1_DFU_RUNTIME_ID.lower() in output
        or RA4M1_DFU_BOOTLOADER_ID.lower() in output
    )


def ra4m1_rom_boot_port() -> str | None:
    python = zephyr_venv_python()
    script = (
        "import serial.tools.list_ports\n"
        f"target_vid = '{RA4M1_ROM_BOOT_VID}'\n"
        f"target_pid = '{RA4M1_ROM_BOOT_PID}'\n"
        "for port in serial.tools.list_ports.comports():\n"
        "    vid = f'{port.vid:04x}' if port.vid is not None else ''\n"
        "    pid = f'{port.pid:04x}' if port.pid is not None else ''\n"
        "    description = (port.description or '').lower()\n"
        "    if (vid, pid) == (target_vid, target_pid) or 'ra usb boot' in description:\n"
        "        print(port.device)\n"
        "        break\n"
    )
    result = run_command_capture(
        [str(python), "-c", script], cwd=zephyr_workspace(), env=west_command_env()
    )
    if result.returncode != 0:
        return None

    ports = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return ports[0] if ports else None


def ra4m1_rom_boot_hint(port: str) -> str:
    return (
        f"XIAO RA4M1 is in Renesas ROM bootloader mode on {port}. "
        "Run 'seeed-zephyr flash xiao_ra4m1' to flash via ROM boot automatically."
    )


def wait_for_ra4m1_dfu_device(
    timeout_seconds: int = RA4M1_DFU_WAIT_SECONDS,
    poll_seconds: float = RA4M1_DFU_POLL_SECONDS,
) -> None:
    # Waits for either runtime DFU or bootloader DFU to enumerate.
    # 等待 runtime DFU 或 bootloader DFU 完成枚举。
    deadline = time.monotonic() + timeout_seconds

    while time.monotonic() < deadline:
        if ra4m1_dfu_device_available():
            return
        rom_boot_port = ra4m1_rom_boot_port()
        if rom_boot_port is not None:
            raise CliError(ra4m1_rom_boot_hint(rom_boot_port))
        time.sleep(poll_seconds)

    raise CliError("Timed out waiting for the RA4M1 DFU bootloader.")


def prepare_ra4m1_dfu_bootloader(
    port: str | None,
    timeout_seconds: int = RA4M1_DFU_WAIT_SECONDS,
    poll_seconds: float = RA4M1_DFU_POLL_SECONDS,
) -> str | None:
    if ra4m1_dfu_device_available():
        return port

    rom_boot_port = ra4m1_rom_boot_port()
    if rom_boot_port is not None:
        raise CliError(ra4m1_rom_boot_hint(rom_boot_port))

    try:
        selected_port = port or detect_serial_port()
    except CliError as error:
        raise CliError(f"{error}\nHint: {ra4m1_bootloader_hint(port)}") from error

    print(
        f"Requesting RA4M1 DFU bootloader via {selected_port} at {RP2_BOOTLOADER_BAUD} baud...",
        flush=True,
    )
    touch_serial_1200(selected_port)

    try:
        wait_for_ra4m1_dfu_device(timeout_seconds, poll_seconds)
    except CliError as error:
        raise CliError(f"{error}\nHint: {ra4m1_bootloader_hint(selected_port)}") from error

    print("RA4M1 DFU bootloader detected.", flush=True)
    return selected_port


def run_ra4m1_dfu_flash(port: str | None = None) -> str | None:
    dfu_util = dfu_util_path()
    if dfu_util is None:
        raise CliError(f"dfu-util was not found. {dfu_util_install_hint()}")

    image = prepare_ra4m1_dfu_image()
    selected_port = prepare_ra4m1_dfu_bootloader(port)
    run_command(
        [
            str(dfu_util),
            "--device",
            RA4M1_DFU_VID_PID,
            "-D",
            str(image),
            "-a",
            RA4M1_DFU_ALT,
            "-R",
        ],
        cwd=zephyr_workspace(),
        env=west_command_env(),
    )
    return selected_port


def uses_uf2_runner(board: dict[str, str]) -> bool:
    # Identifies boards whose normal repository flash path is UF2 mass storage.
    # 识别仓库默认通过 UF2 存储盘烧录的开发板。
    return board["vendor"] == "raspberrypi" or board["id"] in UF2_RUNNER_BOARD_IDS


def resolve_flash_port(board: dict[str, str], port: str | None) -> str | None:
    # Resolves the serial port only for runners that require it before flashing.
    # 仅为烧录前需要串口的 runner 解析串口。
    if board["target"] != "seeeduino_xiao":
        return port

    try:
        return port or detect_serial_port()
    except CliError as error:
        raise CliError(f"{error}\nHint: {samd21_bootloader_hint(port)}") from error


def uf2_mounts() -> list[str]:
    python = zephyr_venv_python()
    # Mirrors Zephyr's UF2 runner mount detection before invoking west flash.
    # 在调用 west flash 前，复用 Zephyr UF2 runner 的挂载盘判断规则。
    script = (
        "from pathlib import Path\n"
        "import psutil\n"
        "mounts = []\n"
        "for part in psutil.disk_partitions():\n"
        "    info = Path(part.mountpoint) / 'INFO_UF2.TXT'\n"
        "    if part.fstype in ('vfat', 'FAT', 'msdos') and info.is_file():\n"
        "        mounts.append(part.mountpoint)\n"
        "print('\\n'.join(mounts))\n"
    )
    result = run_command_capture(
        [str(python), "-c", script], cwd=zephyr_workspace(), env=west_command_env()
    )
    if result.returncode != 0:
        raise CliError(
            "UF2 volume detection failed. Zephyr's UF2 runner requires psutil "
            f"in the Zephyr venv: {zephyr_workspace()}/.venv"
        )

    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def wait_for_uf2_mount(timeout_seconds: int = RP2_BOOTLOADER_WAIT_SECONDS) -> str:
    # Waits for exactly one UF2 mass-storage volume after the board reboots.
    # 等待开发板重启后出现唯一的 UF2 存储卷。
    deadline = time.monotonic() + timeout_seconds

    while time.monotonic() < deadline:
        mounts = uf2_mounts()
        if len(mounts) == 1:
            return mounts[0]
        if len(mounts) > 1:
            mount_list = "\n".join(f"  {mount}" for mount in mounts)
            raise CliError(
                f"Multiple UF2 mass storage volumes found:\n{mount_list}\n"
                "Disconnect the extra UF2 boards and rerun the flash command."
            )
        time.sleep(0.5)

    raise CliError("Timed out waiting for the UF2 mass storage volume.")


def wait_for_uf2_detach(timeout_seconds: int = RP2_BOOTLOADER_WAIT_SECONDS) -> None:
    # Waits for UF2 storage to disappear after Zephyr copies the firmware.
    # 等待 Zephyr 复制固件后 UF2 存储盘消失。
    deadline = time.monotonic() + timeout_seconds

    while time.monotonic() < deadline:
        if not uf2_mounts():
            return
        time.sleep(0.5)

    raise CliError(
        "UF2 mass storage volume did not detach after flashing. "
        "Unplug and reconnect the board, then open monitor again."
    )


def wait_for_ra4m1_rom_boot_detach(timeout_seconds: int = 30) -> None:
    # Waits for the ROM bootloader USB device to disappear after flash.
    # 等待 ROM bootloader USB 设备在烧录后消失。
    print(
        "Press RESET to boot the new firmware. "
        "Waiting for ROM bootloader to detach...",
        flush=True,
    )
    deadline = time.monotonic() + timeout_seconds

    while time.monotonic() < deadline:
        if ra4m1_rom_boot_port() is None:
            print("Board rebooted. Starting monitor...", flush=True)
            return
        time.sleep(0.5)

    raise CliError(
        "ROM bootloader did not detach after flashing. "
        "Press RESET on the board, then open monitor manually with: "
        "seeed-zephyr monitor xiao_ra4m1"
    )


def touch_serial_1200(port: str) -> None:
    python = zephyr_venv_python()
    script = (
        "import sys, time;"
        "import serial;"
        "port = sys.argv[1];"
        "hold_seconds = float(sys.argv[2]);"
        "ser = serial.Serial(port=port, baudrate=1200, timeout=0.1);"
        "time.sleep(hold_seconds);"
        "ser.close()"
    )
    result = run_command_capture(
        [str(python), "-c", script, port, str(RP2_BOOTLOADER_TOUCH_SECONDS)],
        cwd=zephyr_workspace(),
        env=west_command_env(),
    )
    if result.returncode != 0:
        details = result.stdout.strip()
        message = f"Unable to open {port} at {RP2_BOOTLOADER_BAUD} baud."
        if details:
            message = f"{message}\n{details}"
        raise CliError(message)


def prepare_uf2_bootloader(board_id: str, port: str | None) -> str | None:
    mounts = uf2_mounts()
    if len(mounts) == 1:
        return port
    if len(mounts) > 1:
        mount_list = "\n".join(f"  {mount}" for mount in mounts)
        raise CliError(
            f"Multiple UF2 mass storage volumes found:\n{mount_list}\n"
            "Disconnect the extra UF2 boards and rerun the flash command."
        )

    try:
        selected_port = port or detect_serial_port()
    except CliError as error:
        raise CliError(f"{error}\nHint: {uf2_bootloader_hint(board_id)}") from error

    print(
        f"Requesting UF2 bootloader via {selected_port} at {RP2_BOOTLOADER_BAUD} baud...",
        flush=True,
    )
    touch_serial_1200(selected_port)

    try:
        mount = wait_for_uf2_mount()
    except CliError as error:
        raise CliError(f"{error}\nHint: {uf2_bootloader_hint(board_id)}") from error

    print(f"UF2 bootloader volume detected: {mount}", flush=True)
    return selected_port


def run_west_flash(board_id: str, port: str | None = None) -> str | None:
    # Runs Zephyr flash and returns the serial port selected for later monitor use.
    # 执行 Zephyr 烧录，并返回后续 monitor 可复用的串口。
    board = require_board(board_id)
    port = resolve_flash_port(board, port)
    if board["id"] == RA4M1_BOARD_ID:
        return run_ra4m1_dfu_flash(port)

    if uses_uf2_runner(board):
        port = prepare_uf2_bootloader(board_id, port)

    command = ["flash"]
    if board["id"] in UF2_RUNNER_BOARD_IDS:
        command.extend(["--runner", "uf2"])
    if board["id"] == MG24_BOARD_ID:
        command.extend(["--runner", "pyocd"])
    if board["target"] == "seeeduino_xiao" and port is not None:
        command.extend(["--bossac-port", port, "--delay", SAMD21_BOSSAC_DELAY_SECONDS])

    try:
        run_west(command)
    except CliError as error:
        if board["target"] == "seeeduino_xiao":
            raise CliError(f"{error}\nHint: {samd21_bootloader_hint(port)}") from error
        if uses_uf2_runner(board):
            raise CliError(f"{error}\nHint: {uf2_bootloader_hint(board_id)}") from error
        raise

    return port


def vendor_to_hal_module(vendor: str) -> str | None:
    # Maps repository vendor ids to Zephyr HAL module names.
    # 将仓库 vendor id 映射为 Zephyr HAL 模块名称。
    return {
        "espressif": "hal_espressif",
        "nordic": "hal_nordic",
        "renesas": "hal_renesas",
        "silabs": "hal_silabs",
        "raspberrypi": "hal_rpi_pico",
        "microchip": "hal_atmel",
    }.get(vendor)


def ensure_chip_blobs(board: dict[str, str]) -> None:
    # Fetches Zephyr-declared binary blobs for the board vendor when present.
    # 当开发板厂商对应的 Zephyr 模块声明二进制 blobs 时，获取这些 blobs。
    module = vendor_to_hal_module(board["vendor"])
    if module is None:
        return

    result = run_west_capture(["blobs", "list", module])
    if result.returncode != 0 or not result.stdout.strip():
        return

    run_west(["blobs", "fetch", module])


def run_west_build(
    board_id: str, example: dict[str, object], extra_overlay: str | None = None
) -> None:
    # Builds the selected example through Zephyr's west command.
    # An optional extra devicetree overlay stacks on top of app.overlay (used for --pin).
    # 通过 Zephyr 的 west 命令构建选中的示例；可选的额外 overlay 叠加在 app.overlay 之上（用于 --pin）。
    board = require_board(board_id)
    target = example.get("zephyr_target") or board["target"]
    example_dir = Path(str(example["path"]))
    display_name = _display_path(example_dir)
    ensure_chip_blobs(board)
    print(f"Building {display_name} for {target}...", flush=True)
    command = ["build", "-p", "always", "-b", target]
    if board["vendor"] == "raspberrypi":
        command.extend(["-S", RP2_BOOTLOADER_SNIPPET])
    command.append(str(example_dir))
    if extra_overlay:
        command.extend(["--", f"-DEXTRA_DTC_OVERLAY_FILE={extra_overlay}"])
    run_west(command)
    print(f"Build succeeded: {display_name}", flush=True)


def usb_serial_devices() -> list[str]:
    python = zephyr_venv_python()
    # Lists USB-like serial devices through pyserial in the Zephyr venv.
    # 通过 Zephyr venv 中的 pyserial 列出类似 USB 的串口设备。
    script = (
        "import serial.tools.list_ports;"
        "ports = [p for p in serial.tools.list_ports.comports() "
        "if any(k in (p.device + ' ' + (p.description or '')).lower() "
        "for k in ('usbmodem', 'ttyacm', 'ttyusb', 'cu.usbmodem', 'usb'))];"
        "print('\\n'.join(p.device for p in ports))"
    )
    result = run_command_capture([str(python), "-c", script], cwd=zephyr_workspace())
    if result.returncode != 0:
        raise CliError(
            "Serial port detection failed. Is pyserial installed in the Zephyr venv?\n"
            f"Try: {zephyr_workspace()}/.venv/bin/python -m pip install pyserial"
        )

    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def list_serial_ports_detailed() -> list[tuple[str, str]]:
    python = zephyr_venv_python()
    # Lists USB serial devices with their descriptions.
    # 列出 USB 串口设备及其描述信息。
    script = (
        "import serial.tools.list_ports\n"
        "for p in serial.tools.list_ports.comports():\n"
        "    if any(k in (p.device + ' ' + (p.description or '')).lower() "
        "for k in ('usbmodem', 'ttyacm', 'ttyusb', 'cu.usbmodem', 'usb')):\n"
        "        desc = p.description or p.device\n"
        "        print(f'{p.device}\\t{desc}')\n"
    )
    result = run_command_capture([str(python), "-c", script], cwd=zephyr_workspace())
    if result.returncode != 0:
        raise CliError(
            "Serial port detection failed. Is pyserial installed in the Zephyr venv?\n"
            f"Try: {zephyr_workspace()}/.venv/bin/python -m pip install pyserial"
        )
    ports = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t", 1)
        device = parts[0]
        description = parts[1] if len(parts) > 1 else device
        ports.append((device, description))
    return ports


COMMON_BAUD_RATES = [9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600]


def interactive_select_port() -> str:
    # Prompts the user to select a serial port from available devices.
    # 让用户从可用串口设备中交互选择一个。
    ports = list_serial_ports_detailed()
    if not ports:
        raise CliError(
            "No USB serial device found. Check:\n"
            "- Is the board plugged in?\n"
            "- On WSL2: did you run 'usbipd attach --wsl --busid <BUSID>'?\n"
            "- Try specifying the port manually with --port <device>"
        )
    if len(ports) == 1:
        device, description = ports[0]
        print(f"Serial port: {device} ({description})", flush=True)
        return device

    print("\nAvailable serial ports:", flush=True)
    for i, (device, description) in enumerate(ports, 1):
        print(f"  [{i}] {device} - {description}", flush=True)
    while True:
        choice = input(f"Select port [1]: ").strip()
        if not choice:
            return ports[0][0]
        try:
            index = int(choice)
            if 1 <= index <= len(ports):
                return ports[index - 1][0]
        except ValueError:
            pass
        print(f"  Enter a number between 1 and {len(ports)}.", flush=True)


def interactive_select_baud(default: int = 115200) -> int:
    # Prompts the user to enter or select a baud rate.
    # 让用户输入或选择波特率。
    print(f"\nCommon baud rates: {', '.join(str(b) for b in COMMON_BAUD_RATES)}")
    while True:
        choice = input(f"Baud rate [{default}]: ").strip()
        if not choice:
            return default
        try:
            baud = int(choice)
            if baud > 0:
                return baud
        except ValueError:
            pass
        print("  Enter a valid baud rate (positive integer).", flush=True)


def detect_serial_port() -> str:
    devices = usb_serial_devices()
    if not devices:
        raise CliError(
            "No USB serial device found. Check:\n"
            "- Is the board plugged in?\n"
            "- On WSL2: did you run 'usbipd attach --wsl --busid <BUSID>'?\n"
            "- Try specifying the port manually with --port <device>"
        )
    if len(devices) > 1:
        device_list = "\n".join(f"  {device}" for device in devices)
        raise CliError(
            f"Multiple USB serial devices found:\n{device_list}\n"
            "Specify one with --port <device>."
        )

    return devices[0]


def wait_for_serial_port(timeout_seconds: int = 10) -> str:
    # Waits for a single USB serial device after boards reset and re-enumerate.
    # 等待开发板复位并重新枚举后出现唯一的 USB 串口设备。
    deadline = time.monotonic() + timeout_seconds

    while time.monotonic() < deadline:
        devices = usb_serial_devices()
        if len(devices) == 1:
            return devices[0]
        if len(devices) > 1:
            device_list = "\n".join(f"  {device}" for device in devices)
            raise CliError(
                f"Multiple USB serial devices found:\n{device_list}\n"
                "Specify one with --port <device>."
            )
        time.sleep(0.5)

    raise CliError(
        "No USB serial device appeared after waiting. Check:\n"
        "- Is the board running firmware with USB CDC serial enabled?\n"
        "- Is the board plugged in and fully reset?\n"
        "- Try specifying the port manually with --port <device>"
    )


def serial_port_open_check_script() -> str:
    # Checks whether pyserial can open and close the selected port.
    # 检查 pyserial 是否可以打开并关闭选中的串口。
    return (
        "import sys\n"
        "import serial\n"
        "\n"
        "port = sys.argv[1]\n"
        "baud = int(sys.argv[2])\n"
        "\n"
        "try:\n"
        "    ser = serial.Serial(port=port, baudrate=baud, timeout=0.1)\n"
        "    ser.close()\n"
        "except Exception as error:\n"
        "    print(error)\n"
        "    raise SystemExit(1)\n"
    )


def serial_port_is_openable(port: str, baud: int) -> tuple[bool, str]:
    python = zephyr_venv_python()
    result = run_command_capture(
        [str(python), "-c", serial_port_open_check_script(), port, str(baud)],
        cwd=zephyr_workspace(),
        env=west_command_env(),
    )
    return result.returncode == 0, result.stdout.strip()


def wait_for_serial_port_ready(
    port: str | None = None,
    baud: int = 115200,
    timeout_seconds: int = SERIAL_READY_WAIT_SECONDS,
) -> str:
    # Waits until a USB serial device exists and can be opened by pyserial.
    # 等待 USB 串口出现，并确认 pyserial 已经可以实际打开它。
    deadline = time.monotonic() + timeout_seconds
    last_error = ""

    while time.monotonic() < deadline:
        try:
            selected_port = port or wait_for_serial_port(timeout_seconds=1)
        except CliError as error:
            last_error = str(error)
            time.sleep(SERIAL_READY_POLL_SECONDS)
            continue

        openable, details = serial_port_is_openable(selected_port, baud)
        if openable:
            return selected_port

        last_error = details or f"{selected_port} is not ready."
        time.sleep(SERIAL_READY_POLL_SECONDS)

    message = "USB serial device is present but not ready for monitor after waiting."
    if last_error:
        message = f"{message}\nLast error: {last_error}"
    raise CliError(message)


def run_monitor(board_id: str, port: str | None = None, baud: int = 115200) -> None:
    board = require_board(board_id)

    if board["vendor"] == "espressif":
        # Espressif boards use idf_monitor through the Zephyr west extension.
        # Espressif 开发板通过 Zephyr west extension 使用 idf_monitor。
        command = ["espressif", "monitor", "-b", str(baud)]
        if port is not None:
            command.extend(["-p", port])
        run_west(command)
        return

    # Non-Espressif boards use pyserial miniterm from the Zephyr venv.
    # 非 Espressif 开发板使用 Zephyr venv 中的 pyserial miniterm。
    port = wait_for_serial_port_ready(port, baud)
    python = zephyr_venv_python()
    print(f"Opening serial monitor: {port} @ {baud} baud", flush=True)
    print("Press Ctrl+] to exit.", flush=True)
    run_command([str(python), "-m", "serial.tools.miniterm", port, str(baud)])


def cmd_list_boards(args: argparse.Namespace) -> None:
    records = board_records()
    if getattr(args, "as_json", False):
        print(json.dumps(records, indent=2))
        return
    print("board_id\tstatus\tdemo\tvendor\ttarget")
    for record in records:
        print(
            f"{record['id']}\t{record['status']}\t{record['demo']}\t"
            f"{record['vendor']}\t{record['target']}"
        )


def cmd_list_examples(args: argparse.Namespace) -> None:
    rows = []
    for board_file in sorted(BOARD_DIR.glob("*.yaml")):
        values = read_flat_yaml(board_file)
        board_id = values.get("id", board_file.stem)
        examples = resolve_board_examples(board_id)
        if not examples:
            rows.append(
                {"board_id": board_id, "demo": None, "status": "missing", "example_path": None}
            )
            continue
        for ex in examples:
            rows.append(
                {
                    "board_id": board_id,
                    "demo": ex.get("demo"),
                    "status": ex.get("validation_status", "unknown"),
                    "example_path": _display_path(Path(ex["path"])) if ex.get("path") else None,
                    "zephyr_target": ex.get("zephyr_target"),
                    "id": ex.get("id"),
                }
            )
    if getattr(args, "as_json", False):
        print(json.dumps(rows, indent=2))
        return
    print("board_id\tdemo\tstatus\texample")
    for row in rows:
        demo = row["demo"] or "-"
        example = row["example_path"] or "-"
        print(f"{row['board_id']}\t{demo}\t{row['status']}\t{example}")


def cmd_list_grove(args: argparse.Namespace) -> None:
    # Lists Grove modules with their available examples and supported board counts.
    # 列出 Grove 模块及其可用示例与支持板数量。
    board_ids = [record["id"] for record in board_records()]
    grove_examples = resolve_grove_examples()
    rows = []
    for module_file in sorted(GROVE_DIR.glob("*.yaml")):
        values = read_flat_yaml(module_file)
        module_id = values.get("id", module_file.stem)
        examples = [e for e in grove_examples if e.get("module_id") == module_id]
        example_rows = []
        for ex in examples:
            excluded = set(grove_excluded_boards(ex))
            supported = [b for b in board_ids if b not in excluded]
            example_rows.append(
                {
                    "demo": ex.get("demo"),
                    "interface": ex.get("interface"),
                    "pin_policy": ex.get("pin_policy"),
                    "supported_boards": len(supported),
                    "excluded_boards": sorted(excluded),
                }
            )
        rows.append(
            {
                "id": module_id,
                "sku": values.get("sku", ""),
                "display_name": values.get("display_name", ""),
                "category": values.get("category", ""),
                "interface": values.get("interface", ""),
                "zephyr_support": values.get("zephyr_support", ""),
                "examples": example_rows,
            }
        )
    if getattr(args, "as_json", False):
        print(json.dumps(rows, indent=2))
        return
    print("id\tinterface\tsupport\texamples\tdisplay_name")
    for row in rows:
        if row["examples"]:
            ex_summary = "; ".join(
                f"{e['demo']}({e['supported_boards']} boards)" for e in row["examples"]
            )
        else:
            ex_summary = "-"
        print(
            f"{row['id']}\t{row['interface']}\t{row['zephyr_support']}\t"
            f"{ex_summary}\t{row['display_name']}"
        )


def cmd_list_expansion(args: argparse.Namespace) -> None:
    # Lists expansion boards from metadata. Scalar fields only.
    # 列出扩展板元数据。仅标量字段。
    rows = []
    for board_file in sorted(EXPANSION_DIR.glob("*.yaml")):
        values = read_flat_yaml(board_file)
        rows.append(
            {
                "id": values.get("id", board_file.stem),
                "sku": values.get("sku", ""),
                "display_name": values.get("display_name", ""),
                "compatible_form_factor": values.get("compatible_form_factor", ""),
                "zephyr_shield": values.get("zephyr_shield", ""),
            }
        )
    if getattr(args, "as_json", False):
        print(json.dumps(rows, indent=2))
        return
    print("id\tshield\tdisplay_name")
    for row in rows:
        print(f"{row['id']}\t{row['zephyr_shield'] or '-'}\t{row['display_name']}")


def cmd_show_board(args: argparse.Namespace) -> None:
    # Shows full metadata and examples for one board.
    # 显示某块板子的完整元数据和示例。
    require_board(args.board_id)
    values = read_flat_yaml(BOARD_DIR / f"{args.board_id}.yaml")
    examples = [
        {
            "demo": e.get("demo"),
            "validation_status": e.get("validation_status", "unknown"),
            "zephyr_target": e.get("zephyr_target"),
            "example_path": _display_path(Path(e["path"])) if e.get("path") else None,
        }
        for e in resolve_board_examples(args.board_id)
    ]
    if getattr(args, "as_json", False):
        print(json.dumps({**values, "examples": examples}, indent=2))
        return
    for key in ("id", "display_name", "vendor", "soc", "zephyr_target"):
        print(f"{key}:\t{values.get(key, '')}")
    print("examples:")
    for example in examples:
        print(f"  {example['demo']}\t{example['validation_status']}")


def cmd_show_example(args: argparse.Namespace) -> None:
    # Shows full metadata, file list, and README for one example.
    # board_id may be a grove/<module>/<demo> reference for a Grove example.
    # 显示某个示例的完整元数据、文件清单和 README;board_id 可为 grove/<module>/<demo> 引用。
    if args.board_id.startswith("grove/"):
        _cmd_show_grove_example(args)
        return

    if not args.demo:
        raise CliError("Demo name is required for a board example, such as: show example xiao_esp32c6 blinky")
    require_board(args.board_id)
    src_dir = EXAMPLES_DIR / args.board_id / args.demo
    example_file = src_dir / "example.yaml"
    if not example_file.is_file():
        examples = resolve_board_examples(args.board_id)
        demos = ", ".join(sorted(e.get("demo", "?") for e in examples)) or "none"
        raise CliError(
            f"Example '{args.demo}' not found for {args.board_id}. Available: {demos}."
        )
    values = read_flat_yaml(example_file)
    files = sorted(p.name for p in src_dir.iterdir() if p.is_file())
    detail = {**values, "path": _display_path(src_dir), "files": files}
    readme = src_dir / "README.md"
    if readme.is_file():
        detail["readme"] = readme.read_text(encoding="utf-8")
    if getattr(args, "as_json", False):
        print(json.dumps(detail, indent=2))
        return
    for key in (
        "id",
        "board_id",
        "demo",
        "zephyr_target",
        "validation_status",
        "expected_behavior",
    ):
        print(f"{key}:\t{values.get(key, '')}")
    print(f"path:\t{detail['path']}")
    print(f"files:\t{', '.join(files)}")


def _cmd_show_grove_example(args: argparse.Namespace) -> None:
    # Shows a Grove example: interface, pin policy, and per-board support matrix.
    # 显示 Grove 示例:接口、引脚策略与按板支持矩阵。
    module_id, demo = parse_grove_ref(args.board_id)
    if not demo:
        demos = sorted(
            p.parent.name
            for p in grove_example_dirs()
            if p.parent.parent.name == module_id
        )
        if not demos:
            raise CliError(
                f"Grove module '{module_id}' has no examples. "
                "Run 'seeed-zephyr list grove' to see available modules."
            )
        raise CliError(f"Specify a demo for {module_id}. Available: {', '.join(demos)}.")
    example = resolve_grove_example(module_id, demo)
    src_dir = Path(str(example["path"]))
    excluded = set(grove_excluded_boards(example))
    board_ids = [record["id"] for record in board_records()]
    statuses = read_example_status(str(example.get("id", "")))
    matrix = [
        {
            "board_id": bid,
            "supported": bid not in excluded,
            "status": statuses.get(bid, "pending" if bid not in excluded else "excluded"),
        }
        for bid in board_ids
    ]
    files = sorted(p.name for p in src_dir.iterdir() if p.is_file())
    detail = {
        "id": example.get("id"),
        "kind": "grove",
        "module_id": module_id,
        "demo": demo,
        "interface": example.get("interface"),
        "connector": example.get("connector"),
        "pin_policy": example.get("pin_policy"),
        "excluded_boards": sorted(excluded),
        "expected_behavior": example.get("expected_behavior"),
        "path": _display_path(src_dir),
        "files": files,
        "board_matrix": matrix,
    }
    pins = example.get("pins")
    if isinstance(pins, list):
        detail["pins"] = pins
    readme = src_dir / "README.md"
    if readme.is_file():
        detail["readme"] = readme.read_text(encoding="utf-8")
    if getattr(args, "as_json", False):
        print(json.dumps(detail, indent=2))
        return
    for key in ("id", "module_id", "demo", "interface", "connector", "pin_policy", "expected_behavior"):
        print(f"{key}:\t{detail.get(key, '')}")
    print(f"path:\t{detail['path']}")
    print(f"files:\t{', '.join(files)}")
    supported = [m["board_id"] for m in matrix if m["supported"]]
    print(f"supported_boards:\t{', '.join(supported)}")
    if excluded:
        print(f"excluded_boards:\t{', '.join(sorted(excluded))}")


def cmd_show_pins(args: argparse.Namespace) -> None:
    # Returns the full pin diagram data for a board + example: form-factor layout,
    # per-pin state, role assignments, and the module interface. Pure query, no build.
    # 返回板+示例的完整引脚图数据:形态布局、每脚状态、角色分配与模块接口。纯查询,不构建。
    require_board(args.board_id)
    example_ref = args.example_ref
    is_grove = example_ref.startswith("grove/")
    if is_grove:
        module_id, demo = parse_grove_ref(example_ref)
        if not demo:
            raise CliError("Provide a full Grove reference: grove/<module>/<demo>.")
        example = resolve_grove_example(module_id, demo)
        if not grove_supports_board(example, args.board_id):
            raise CliError(
                f"Grove example {module_id}/{demo} excludes board '{args.board_id}'."
            )
        interface = str(example.get("interface", ""))
        pin_policy = str(example.get("pin_policy", ""))
        declared_pins = example.get("pins") if isinstance(example.get("pins"), list) else []
    else:
        example = select_example(args.board_id, example_ref)
        interface = ""
        pin_policy = ""
        declared_pins = []

    form_factor = load_form_factor("xiao")
    ff_pins = form_factor.get("pins", [])
    layout = form_factor.get("layout", {})
    buses = form_factor.get("buses", {})

    reserved = board_reserved_pins(args.board_id)
    analog = board_analog_pins(args.board_id)
    chip_pins = board_pin_map(args.board_id)

    # Resolve current role assignments from the example defaults (no --pin here).
    # 由示例默认值解析当前角色分配(此处不带 --pin)。
    roles: list[dict[str, object]] = []
    allowed_by_pin: dict[str, str] = {}
    assigned_by_pin: dict[str, str] = {}
    if pin_policy == "selectable" and isinstance(declared_pins, list):
        for spec in declared_pins:
            if not isinstance(spec, dict) or not spec.get("role"):
                continue
            role = str(spec["role"])
            default = str(spec.get("default", "")).upper()
            allowed = spec.get("allowed")
            allowed_list = [str(p).upper() for p in allowed] if isinstance(allowed, list) else []
            roles.append(
                {
                    "role": role,
                    "assigned": default,
                    "default": default,
                    "allowed": allowed_list,
                }
            )
            if default:
                assigned_by_pin[default] = role
            for p in allowed_list:
                if p not in allowed_by_pin:
                    allowed_by_pin[p] = role

    # Pins that the module's fixed bus occupies (wiring position, not selectable).
    # 模块固定总线占用的引脚(接线位置,不可选)。
    bus_pins: dict[str, str] = {}
    if pin_policy == "fixed-bus" and interface and isinstance(buses, dict):
        bus_def = buses.get(interface)
        if isinstance(bus_def, dict):
            for role_name, pin_id in bus_def.items():
                bus_pins[str(pin_id)] = f"{interface}-{role_name}"

    pin_rows: list[dict[str, object]] = []
    for pin in ff_pins:
        if not isinstance(pin, dict):
            continue
        pid = str(pin.get("id", ""))
        ptype = str(pin.get("type", ""))
        row: dict[str, object] = {"id": pid, "type": ptype}
        if pin.get("bus"):
            row["bus"] = pin.get("bus")
        if pin.get("bus_role"):
            row["bus_role"] = pin.get("bus_role")
        if pin.get("rail"):
            row["rail"] = pin.get("rail")
        if pid in chip_pins:
            row["chip_pin"] = chip_pins[pid]

        if ptype == "power":
            row["status"] = "power"
        elif pid in reserved:
            row["status"] = "reserved"
            row["reason"] = reserved[pid]
        elif pin_policy == "selectable":
            if pid in assigned_by_pin:
                row["status"] = "default"
                row["role"] = assigned_by_pin[pid]
            elif pid in allowed_by_pin:
                if interface == "analog" and pid not in analog:
                    row["status"] = "incompatible"
                    row["reason"] = "no-adc"
                else:
                    row["status"] = "selectable"
                    row["role"] = allowed_by_pin[pid]
            else:
                row["status"] = "free"
        elif pin_policy == "fixed-bus":
            if pid in bus_pins:
                row["status"] = "bus"
                row["reason"] = bus_pins[pid]
            else:
                row["status"] = "free"
        else:
            row["status"] = "free"
        pin_rows.append(row)

    payload = {
        "board_id": args.board_id,
        "form_factor": form_factor.get("id", "xiao"),
        "example": {
            "ref": example_ref,
            "interface": interface,
            "pin_policy": pin_policy,
        },
        "layout": layout,
        "pins": pin_rows,
        "roles": roles,
    }
    if getattr(args, "as_json", False):
        print(json.dumps(payload, indent=2))
        return

    print(f"board:\t{args.board_id}")
    print(f"example:\t{example_ref}")
    print(f"interface:\t{interface or '-'}")
    print(f"pin_policy:\t{pin_policy or '-'}")
    print("pins:")
    for row in pin_rows:
        extra = ""
        if row.get("reason"):
            extra = f"  ({row['reason']})"
        if row.get("role"):
            extra += f"  role={row['role']}"
        if row.get("chip_pin"):
            extra += f"  chip={row['chip_pin']}"
        print(f"  {row['id']}\t{row['type']}\t{row['status']}{extra}")
    if roles:
        print("roles:")
        for r in roles:
            print(f"  {r['role']}\tassigned={r['assigned']}\tallowed={','.join(r['allowed'])}")


def _normalize_from_asset(from_asset: str) -> tuple[str, str]:
    """Parse a --from value into (board_id, demo).
    Accepts board/demo, boards/board/demo, or examples/boards/board/demo.
    把 --from 的值解析成 (board_id, demo)。
    支持 board/demo、boards/board/demo、examples/boards/board/demo 三种写法。"""
    parts = [p for p in from_asset.strip().strip("/").split("/") if p]
    if parts[:1] == ["examples"]:
        parts = parts[1:]
    if parts[:1] == ["boards"]:
        parts = parts[1:]
    if len(parts) != 2:
        raise CliError(
            f"Invalid --from value: {from_asset}. "
            "Use the form <board_id>/<demo>, such as xiao_esp32c6/blinky."
        )
    return parts[0], parts[1]


def _is_grove_from_asset(from_asset: str) -> bool:
    return from_asset.strip().lstrip("/").lower().startswith("grove/")


def _board_overlay_name(board_id: str) -> str:
    # Zephyr auto-applies boards/<target>.overlay where target uses underscores for slashes.
    # Zephyr 会自动应用 boards/<target>.overlay,target 中的斜杠替换为下划线。
    board = require_board(board_id)
    return board["target"].replace("/", "_")


def cmd_create(args: argparse.Namespace) -> None:
    # Creates a standalone project by copying a repository example.
    # Board examples copy as-is; Grove examples are board-agnostic and may be generated
    # for any supported board, with --pin baked into a per-board overlay.
    # 通过复制仓库示例创建独立项目。板级示例原样复制;Grove 示例可跨板生成,--pin 固化进按板 overlay。
    if _is_grove_from_asset(args.from_asset):
        _cmd_create_grove(args)
    else:
        _cmd_create_board(args)


def _cmd_create_board(args: argparse.Namespace) -> None:
    source_board, demo = _normalize_from_asset(args.from_asset)
    src_dir = EXAMPLES_DIR / source_board / demo
    example_file = src_dir / "example.yaml"
    if not example_file.is_file():
        examples = resolve_board_examples(source_board)
        if examples:
            demos = ", ".join(sorted(e.get("demo", "?") for e in examples))
            raise CliError(
                f"Example '{demo}' not found for {source_board}. Available: {demos}."
            )
        raise CliError(
            f"Source asset not found: {source_board}/{demo}. "
            "Run 'seeed-zephyr list examples' to see available assets."
        )

    values = read_flat_yaml(example_file)
    example_board = values.get("board_id") or source_board

    if args.board_id != example_board:
        raise CliError(
            f"Example {source_board}/{demo} targets board '{example_board}', "
            f"not '{args.board_id}'. Pass --board {example_board}, "
            "or use a Grove example with --from grove/<module>/<demo> for cross-board projects."
        )

    if args.pins:
        raise CliError("--pin applies to Grove examples only.")

    if values.get("validation_status") == "unsupported":
        reason = values.get("unsupported_reason") or "marked unsupported"
        raise CliError(f"Cannot create from an unsupported example: {reason}.")

    out_dir = _prepare_output_dir(args.output, args.force)
    shutil.copytree(src_dir, out_dir, dirs_exist_ok=True)

    snapshot = {
        "generator": "seeed-zephyr",
        "source_asset": f"examples/boards/{example_board}/{demo}",
        "board": args.board_id,
        "zephyr_version": ZEPHYR_BASELINE,
        "validation_status": values.get("validation_status") or "unknown",
    }
    (out_dir / "snapshot.json").write_text(
        json.dumps(snapshot, indent=2) + "\n", encoding="utf-8"
    )

    print(f"Created project at {out_dir}", flush=True)
    print("Next step:", flush=True)
    print(f"  seeed-zephyr build {args.board_id} --app {out_dir}", flush=True)


def _cmd_create_grove(args: argparse.Namespace) -> None:
    module_id, demo = parse_grove_ref(args.from_asset)
    if not demo:
        demos = sorted(
            p.parent.name
            for p in grove_example_dirs()
            if p.parent.parent.name == module_id
        )
        if not demos:
            raise CliError(
                f"Grove module '{module_id}' has no examples. "
                "Run 'seeed-zephyr list grove' to see available modules."
            )
        if len(demos) != 1:
            raise CliError(f"Specify a demo for {module_id}. Available: {', '.join(demos)}.")
        demo = demos[0]

    example = resolve_grove_example(module_id, demo)
    require_board(args.board_id)
    if not grove_supports_board(example, args.board_id):
        raise CliError(
            f"Grove example {module_id}/{demo} excludes board '{args.board_id}'. "
            f"Excluded boards: {', '.join(grove_excluded_boards(example)) or 'none'}."
        )

    assignments = resolve_pin_assignment(example, args.board_id, args.pins)

    out_dir = _prepare_output_dir(args.output, args.force)
    src_dir = Path(str(example["path"]))
    shutil.copytree(src_dir, out_dir, dirs_exist_ok=True)

    # Bake the chosen pins into a per-board overlay so the generated project is self-contained.
    # 把选定引脚固化进按板 overlay,使生成的项目自包含。
    if assignments:
        boards_dir = out_dir / "boards"
        boards_dir.mkdir(exist_ok=True)
        template = src_dir / "pins" / "pin.overlay.in"
        if not template.is_file():
            raise CliError(
                f"Example declares selectable pins but has no pins/pin.overlay.in template."
            )
        text = template.read_text(encoding="utf-8")
        for role, pin in assignments.items():
            placeholder = f"@PIN_{role.upper()}@"
            if placeholder not in text:
                raise CliError(
                    f"Pin overlay template is missing placeholder '{placeholder}' for role '{role}'."
                )
            text = text.replace(placeholder, str(pin_index(pin)))
        (boards_dir / f"{_board_overlay_name(args.board_id)}.overlay").write_text(
            text, encoding="utf-8"
        )

    snapshot = {
        "generator": "seeed-zephyr",
        "source_asset": f"examples/grove/{module_id}/{demo}",
        "board": args.board_id,
        "zephyr_version": ZEPHYR_BASELINE,
        "pins": assignments,
    }
    (out_dir / "snapshot.json").write_text(
        json.dumps(snapshot, indent=2) + "\n", encoding="utf-8"
    )

    print(f"Created project at {out_dir}", flush=True)
    print("Next step:", flush=True)
    print(f"  seeed-zephyr build {args.board_id} --app {out_dir}", flush=True)


def _prepare_output_dir(output: str, force: bool) -> Path:
    out_dir = Path(output).expanduser().resolve()
    if out_dir.is_file():
        raise CliError(f"Output path is a file: {out_dir}.")
    if out_dir.is_dir() and any(out_dir.iterdir()) and not force:
        raise CliError(
            f"Output directory is not empty: {out_dir}. Use --force to write anyway."
        )
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def cmd_build(args: argparse.Namespace) -> None:
    example, overlay = resolve_build_example(args)
    run_west_build(args.board_id, example, extra_overlay=overlay)


def cmd_flash(args: argparse.Namespace) -> None:
    example, overlay = resolve_build_example(args)

    ra4m1_rom = None
    if args.board_id == RA4M1_BOARD_ID:
        ra4m1_rom = ra4m1_rom_boot_port()

    require_flash_tools(args.board_id, rom_boot=ra4m1_rom is not None)

    if ra4m1_rom is not None:
        print(
            f"ROM bootloader detected on {ra4m1_rom}. "
            "Building app image for DFU offset recovery flash...",
            flush=True,
        )
        run_west_build(args.board_id, example, extra_overlay=overlay)
        port = run_ra4m1_rom_flash(ra4m1_rom)
    else:
        run_west_build(args.board_id, example, extra_overlay=overlay)
        port = run_west_flash(args.board_id, port=args.port)

    if args.monitor:
        board = require_board(args.board_id)
        monitor_port = port
        if board["target"] == "seeeduino_xiao" and args.port is None:
            monitor_port = None
        if uses_uf2_runner(board) and args.port is None:
            monitor_port = None
            wait_for_uf2_detach()
        if board["id"] == RA4M1_BOARD_ID and args.port is None:
            monitor_port = None
            if ra4m1_rom is not None:
                wait_for_ra4m1_rom_boot_detach()
        run_monitor(args.board_id, port=monitor_port, baud=args.baud)


def cmd_debug(args: argparse.Namespace) -> None:
    example, overlay = resolve_build_example(args)
    run_west_build(args.board_id, example, extra_overlay=overlay)
    try:
        run_west(["debug"])
    except CliError as error:
        raise CliError(f"{error}\nHint: {DEBUG_HINT}") from error


def cmd_monitor(args: argparse.Namespace) -> None:
    baud = args.baud if args.baud is not None else 115200

    if args.board_id is not None:
        require_board(args.board_id)
        run_monitor(args.board_id, port=args.port, baud=baud)
        return

    # Interactive mode: select port and baud rate, open miniterm directly.
    # 交互模式：选择串口和波特率，直接用 miniterm 打开。
    port = args.port or interactive_select_port()
    if args.baud is None:
        baud = interactive_select_baud()
    python = zephyr_venv_python()
    print(f"\nOpening serial monitor: {port} @ {baud} baud", flush=True)
    print("Press Ctrl+] to exit.\n", flush=True)
    run_command([str(python), "-m", "serial.tools.miniterm", port, str(baud)])


def cmd_info(args: argparse.Namespace) -> None:
    info = current_info()
    if args.as_json:
        print(json.dumps(info, indent=2))
        return
    print_info(info)


def cmd_update(args: argparse.Namespace) -> None:
    # Updates the current CLI installation or the repository checkout it uses.
    # 更新当前 CLI 安装，或更新它正在使用的仓库签出。
    if _REPO_ROOT is not None:
        if args.version:
            checkout_repo_version(_REPO_ROOT, args.version)
        else:
            update_repo_checkout(_REPO_ROOT)
        return

    update_installed_package(args.version)


def cmd_validate_metadata(_args: argparse.Namespace) -> None:
    # Validates all metadata by delegating to the repo's validator (needs PyYAML).
    # 通过委托给仓库的校验器来校验所有元数据(需要 PyYAML)。
    if _REPO_ROOT is None:
        raise CliError("'validate metadata' requires a local repo clone.")
    script = _REPO_ROOT / "tools" / "validate_metadata" / "validate.py"
    if not script.is_file():
        raise CliError(f"Validator not found: {script}")
    result = subprocess.run([sys.executable, str(script)], cwd=str(_REPO_ROOT))
    if result.returncode != 0:
        raise CliError(
            "Metadata validation failed. If the error above mentions 'yaml', "
            "install PyYAML with: pip install -r tools/validate_metadata/requirements.txt"
        )


def cmd_matrix(_args: argparse.Namespace) -> None:
    if BUILD_MATRIX_SCRIPT is None or _REPO_ROOT is None:
        raise CliError("'matrix' requires a local repo clone.")

    env = os.environ.copy()
    # Use today's date for generated matrix evidence unless the caller pins it.
    # 如果调用方没有固定日期，就用当天日期生成矩阵证据。
    env.setdefault("BUILD_MATRIX_GENERATED_ON", dt.date.today().isoformat())
    result = subprocess.run(["bash", str(BUILD_MATRIX_SCRIPT)], cwd=_REPO_ROOT, env=env)
    if result.returncode != 0:
        raise CliError(f"Build matrix failed with status {result.returncode}.")


def cmd_verify_hardware(args: argparse.Namespace) -> None:
    if HARDWARE_LOG is None or _REPO_ROOT is None:
        raise CliError("'verify-hardware' requires a local repo clone.")

    example = require_supported_example(args.board_id)

    ra4m1_rom = None
    if args.board_id == RA4M1_BOARD_ID:
        ra4m1_rom = ra4m1_rom_boot_port()

    require_flash_tools(args.board_id, rom_boot=ra4m1_rom is not None)

    if ra4m1_rom is not None:
        print(
            f"ROM bootloader detected on {ra4m1_rom}. "
            "Building app image for DFU offset recovery flash...",
            flush=True,
        )
        run_west_build(args.board_id, example)
        run_ra4m1_rom_flash(ra4m1_rom)
    else:
        run_west_build(args.board_id, example)
        run_west_flash(args.board_id)

    print("\nHardware observation")
    print("Answer the prompts after checking the physical board.")
    observed = prompt_choice("Did the expected behavior happen? [y/N] ")
    serial_output = input("Paste serial output, or press Enter to skip: ").strip()
    notes = input("Notes, or press Enter to skip: ").strip()

    append_hardware_log(
        board_id=args.board_id,
        example_path=_display_path(Path(example["path"])),
        observed=observed,
        serial_output=serial_output,
        notes=notes,
    )
    print(f"Hardware verification recorded in {HARDWARE_LOG.relative_to(_REPO_ROOT)}.")


def prompt_choice(prompt: str) -> bool:
    value = input(prompt).strip().lower()
    return value in {"y", "yes"}


def append_hardware_log(
    *, board_id: str, example_path: str, observed: bool, serial_output: str, notes: str
) -> None:
    timestamp = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    result = "PASS" if observed else "FAIL"

    if not HARDWARE_LOG.exists():
        # Create the hardware log on demand for fresh checkouts.
        # 为全新检出仓库按需创建硬件验证日志。
        HARDWARE_LOG.write_text(
            "# Hardware Verification / 硬件验证\n\n"
            "## English\n\n"
            "This file records hardware observations captured by the CLI.\n\n"
            "## 中文\n\n"
            "这个文件记录 CLI 捕获的硬件观察结果。\n\n",
            encoding="utf-8",
        )

    with HARDWARE_LOG.open("a", encoding="utf-8") as log_file:
        log_file.write(f"## {timestamp} - {board_id} - {result}\n\n")
        log_file.write(f"- Board: `{board_id}`\n")
        log_file.write(f"- Example: `{example_path}`\n")
        log_file.write(f"- Result: `{result}`\n")
        log_file.write(f"- Serial output: {serial_output or 'n/a'}\n")
        log_file.write(f"- Notes: {notes or 'n/a'}\n\n")


if __name__ == "__main__":
    raise SystemExit(main())
