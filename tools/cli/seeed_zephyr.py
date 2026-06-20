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
    flash.add_argument(
        "--monitor",
        action="store_true",
        help="Open the board monitor after a successful flash.",
    )
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
    command: list[str], *, cwd: Path = REPO_ROOT, env: dict[str, str] | None = None
) -> None:
    result = subprocess.run(command, cwd=cwd, env=env, check=False)
    if result.returncode != 0:
        raise CliError(f"Command failed with status {result.returncode}: {' '.join(command)}")


def run_command_capture(
    command: list[str], *, cwd: Path = REPO_ROOT, env: dict[str, str] | None = None
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


def west_path() -> Path:
    workspace = Path(os.environ.get("ZEPHYR_WORKSPACE", str(Path.home() / "zephyrproject")))
    return workspace / ".venv" / "bin" / "west"


def zephyr_workspace() -> Path:
    return Path(os.environ.get("ZEPHYR_WORKSPACE", str(Path.home() / "zephyrproject")))


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


def require_flash_tools(board_id: str) -> None:
    board = require_board(board_id)
    if board["vendor"] == "espressif":
        require_west_venv_tool(
            "esptool",
            "Run setup again, or install it with: "
            f"{zephyr_workspace()}/.venv/bin/python -m pip install esptool",
        )


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


def run_west_build(board_id: str, example: dict[str, str]) -> None:
    # Builds the selected repository example through Zephyr's west command.
    # 通过 Zephyr 的 west 命令构建选中的仓库示例。
    board = require_board(board_id)
    target = example.get("zephyr_target") or board["target"]
    example_dir = REPO_ROOT / example["path"]
    ensure_chip_blobs(board)
    print(f"Building {example['path']} for {target}...", flush=True)
    run_west(["build", "-p", "always", "-b", target, str(example_dir)])
    print(f"Build succeeded: {example['path']}", flush=True)


def require_monitor_supported(board_id: str) -> dict[str, str]:
    board = require_board(board_id)
    if board["vendor"] != "espressif":
        raise CliError("Monitor is currently implemented for Espressif boards only.")

    return board


def run_monitor(board_id: str) -> None:
    require_monitor_supported(board_id)
    run_west(["espressif", "monitor"])


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
    example = require_supported_example(args.board_id)
    run_west_build(args.board_id, example)


def cmd_flash(args: argparse.Namespace) -> None:
    example = require_supported_example(args.board_id)
    require_flash_tools(args.board_id)
    if args.monitor:
        require_monitor_supported(args.board_id)

    run_west_build(args.board_id, example)
    run_west(["flash"])
    if args.monitor:
        run_monitor(args.board_id)


def cmd_monitor(args: argparse.Namespace) -> None:
    run_monitor(args.board_id)


def cmd_matrix(_args: argparse.Namespace) -> None:
    env = os.environ.copy()
    # Use today's date for generated matrix evidence unless the caller pins it.
    # 如果调用方没有固定日期，就用当天日期生成矩阵证据。
    env.setdefault("BUILD_MATRIX_GENERATED_ON", dt.date.today().isoformat())
    result = subprocess.run(["bash", str(BUILD_MATRIX_SCRIPT)], cwd=REPO_ROOT, env=env)
    if result.returncode != 0:
        raise CliError(f"Build matrix failed with status {result.returncode}.")


def cmd_verify_hardware(args: argparse.Namespace) -> None:
    example = require_supported_example(args.board_id)
    require_flash_tools(args.board_id)
    run_west_build(args.board_id, example)
    run_west(["flash"])

    print("\nHardware observation")
    print("Answer the prompts after checking the physical board.")
    observed = prompt_choice("Did the expected behavior happen? [y/N] ")
    serial_output = input("Paste serial output, or press Enter to skip: ").strip()
    notes = input("Notes, or press Enter to skip: ").strip()

    append_hardware_log(
        board_id=args.board_id,
        example_path=example["path"],
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
