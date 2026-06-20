#!/usr/bin/env python3

from __future__ import annotations

import argparse
import datetime as dt
import os
import subprocess
import sys
from pathlib import Path


def resolve_repo_root() -> Path:
    env_root = os.environ.get("SEEED_ZEPHYR_REPO_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()

    return Path(__file__).resolve().parents[2]


REPO_ROOT = resolve_repo_root()
BOARD_DIR = REPO_ROOT / "metadata" / "boards"
EXAMPLES_DIR = REPO_ROOT / "examples" / "boards"
BUILD_SCRIPT = REPO_ROOT / "scripts" / "build-example.sh"
BUILD_MATRIX_SCRIPT = REPO_ROOT / "tools" / "build_matrix" / "run.sh"
HARDWARE_LOG = REPO_ROOT / "AI use" / "HARDWARE_VERIFICATION.md"


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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="seeed-zephyr",
        description="Operate Seeed XIAO + Grove Zephyr repository examples.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List repository assets.")
    list_subparsers = list_parser.add_subparsers(dest="asset", required=True)
    list_boards = list_subparsers.add_parser("boards", help="List XIAO boards.")
    list_boards.set_defaults(func=cmd_list_boards)
    list_examples = list_subparsers.add_parser(
        "examples", help="List board examples."
    )
    list_examples.set_defaults(func=cmd_list_examples)

    build = subparsers.add_parser("build", help="Build a board's baseline example.")
    build.add_argument("board_id", help="Board id such as xiao_esp32c6.")
    build.set_defaults(func=cmd_build)

    flash = subparsers.add_parser("flash", help="Build and flash a board example.")
    flash.add_argument("board_id", help="Board id such as xiao_esp32c6.")
    flash.set_defaults(func=cmd_flash)

    monitor = subparsers.add_parser("monitor", help="Open a board monitor.")
    monitor.add_argument("board_id", help="Board id such as xiao_esp32c6.")
    monitor.set_defaults(func=cmd_monitor)

    matrix = subparsers.add_parser("matrix", help="Run the full board build matrix.")
    matrix.set_defaults(func=cmd_matrix)

    verify = subparsers.add_parser(
        "verify-hardware", help="Build, flash, and record hardware observation."
    )
    verify.add_argument("board_id", help="Board id such as xiao_esp32c6.")
    verify.set_defaults(func=cmd_verify_hardware)

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
        value = value.strip()
        if value in {"[]", "null"}:
            value = ""
        values[key.strip()] = value

    return values


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
                "example_path": example.get("path", "") if example else "",
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
    values["path"] = chosen.parent.relative_to(REPO_ROOT).as_posix()
    return values


def require_board(board_id: str) -> dict[str, str]:
    for record in board_records():
        if record["id"] == board_id:
            return record

    available = ", ".join(record["id"] for record in board_records())
    raise CliError(f"Unknown board id: {board_id}. Available boards: {available}")


def require_supported_example(board_id: str) -> str:
    board = require_board(board_id)
    if not board["example_path"]:
        raise CliError(f"No repository example found for {board_id}.")
    if board["status"] == "unsupported":
        raise CliError(f"{board_id} is unsupported in the selected Zephyr baseline.")
    return board["example_path"]


def run_command(command: list[str], *, cwd: Path = REPO_ROOT) -> None:
    result = subprocess.run(command, cwd=cwd, check=False)
    if result.returncode != 0:
        raise CliError(f"Command failed with status {result.returncode}: {' '.join(command)}")


def west_path() -> Path:
    workspace = Path(os.environ.get("ZEPHYR_WORKSPACE", str(Path.home() / "zephyrproject")))
    return workspace / ".venv" / "bin" / "west"


def zephyr_workspace() -> Path:
    return Path(os.environ.get("ZEPHYR_WORKSPACE", str(Path.home() / "zephyrproject")))


def run_west(command: list[str]) -> None:
    west = west_path()
    if not west.exists():
        raise CliError(f"west was not found: {west}")

    run_command([str(west), *command], cwd=zephyr_workspace())


def cmd_list_boards(_args: argparse.Namespace) -> None:
    print("board_id\tstatus\tdemo\tvendor\ttarget")
    for record in board_records():
        print(
            f"{record['id']}\t{record['status']}\t{record['demo']}\t"
            f"{record['vendor']}\t{record['target']}"
        )


def cmd_list_examples(_args: argparse.Namespace) -> None:
    print("board_id\tstatus\texample")
    for record in board_records():
        print(f"{record['id']}\t{record['status']}\t{record['example_path']}")


def cmd_build(args: argparse.Namespace) -> None:
    example_path = require_supported_example(args.board_id)
    run_command(["bash", str(BUILD_SCRIPT), example_path])


def cmd_flash(args: argparse.Namespace) -> None:
    example_path = require_supported_example(args.board_id)
    run_command(["bash", str(BUILD_SCRIPT), example_path])
    run_west(["flash"])


def cmd_monitor(args: argparse.Namespace) -> None:
    board = require_board(args.board_id)
    if board["vendor"] != "espressif":
        raise CliError("Monitor is currently implemented for Espressif boards only.")

    run_west(["espressif", "monitor"])


def cmd_matrix(_args: argparse.Namespace) -> None:
    env = os.environ.copy()
    # Use today's date for generated matrix evidence unless the caller pins it.
    # 如果调用方没有固定日期，就用当天日期生成矩阵证据。
    env.setdefault("BUILD_MATRIX_GENERATED_ON", dt.date.today().isoformat())
    result = subprocess.run(["bash", str(BUILD_MATRIX_SCRIPT)], cwd=REPO_ROOT, env=env)
    if result.returncode != 0:
        raise CliError(f"Build matrix failed with status {result.returncode}.")


def cmd_verify_hardware(args: argparse.Namespace) -> None:
    example_path = require_supported_example(args.board_id)
    run_command(["bash", str(BUILD_SCRIPT), example_path])
    run_west(["flash"])

    print("\nHardware observation")
    print("Answer the prompts after checking the physical board.")
    observed = prompt_choice("Did the expected behavior happen? [y/N] ")
    serial_output = input("Paste serial output, or press Enter to skip: ").strip()
    notes = input("Notes, or press Enter to skip: ").strip()

    append_hardware_log(
        board_id=args.board_id,
        example_path=example_path,
        observed=observed,
        serial_output=serial_output,
        notes=notes,
    )
    print(f"Hardware verification recorded in {HARDWARE_LOG.relative_to(REPO_ROOT)}.")


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
