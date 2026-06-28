#!/usr/bin/env python3

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import platform
import shutil
import subprocess
import sys
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
    show_example.add_argument("board_id", help="Board id such as xiao_esp32c6.")
    show_example.add_argument("demo", help="Demo name such as blinky.")
    add_json_flag(show_example)
    show_example.set_defaults(func=cmd_show_example)

    build = subparsers.add_parser("build", help="Build a board example.")
    build.add_argument("board_id", help="Board id such as xiao_esp32c6.")
    build.add_argument(
        "example",
        nargs="?",
        default=None,
        help="Example name such as blinky. Omit to select interactively.",
    )
    build.add_argument(
        "--app",
        default=None,
        help="Path to an external Zephyr application directory.",
    )
    build.set_defaults(func=cmd_build)

    flash = subparsers.add_parser("flash", help="Build and flash a board example.")
    flash.add_argument("board_id", help="Board id such as xiao_esp32c6.")
    flash.add_argument(
        "example",
        nargs="?",
        default=None,
        help="Example name such as blinky. Omit to select interactively.",
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
    flash.set_defaults(func=cmd_flash)

    debug = subparsers.add_parser("debug", help="Build and start a board debug session.")
    debug.add_argument("board_id", help="Board id such as xiao_esp32c6.")
    debug.add_argument(
        "example",
        nargs="?",
        default=None,
        help="Example name such as blinky. Omit to select interactively.",
    )
    debug.add_argument(
        "--app",
        default=None,
        help="Path to an external Zephyr application directory.",
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
    create.set_defaults(func=cmd_create)

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


def select_example(board_id: str, example_name: str | None = None) -> dict[str, str]:
    # Selects an example by name, or interactively when multiple are available.
    # 按名称选择 example，多个可用时交互选择。
    require_board(board_id)
    examples = resolve_board_examples(board_id)
    supported = [e for e in examples if e.get("validation_status") != "unsupported"]

    if not examples:
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


def run_west_build(board_id: str, example: dict[str, str]) -> None:
    # Builds the selected example through Zephyr's west command.
    # 通过 Zephyr 的 west 命令构建选中的示例。
    board = require_board(board_id)
    target = example.get("zephyr_target") or board["target"]
    example_dir = Path(example["path"])
    display_name = _display_path(example_dir)
    ensure_chip_blobs(board)
    print(f"Building {display_name} for {target}...", flush=True)
    command = ["build", "-p", "always", "-b", target]
    if board["vendor"] == "raspberrypi":
        command.extend(["-S", RP2_BOOTLOADER_SNIPPET])
    command.append(str(example_dir))
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
    # Lists Grove modules from metadata. Scalar fields only; nested config lists
    # are read by the YAML-aware consumers (the extension).
    # 列出 Grove 模块元数据。仅标量字段;嵌套配置列表由能解析 YAML 的消费方(插件)读取。
    rows = []
    for module_file in sorted(GROVE_DIR.glob("*.yaml")):
        values = read_flat_yaml(module_file)
        rows.append(
            {
                "id": values.get("id", module_file.stem),
                "sku": values.get("sku", ""),
                "display_name": values.get("display_name", ""),
                "category": values.get("category", ""),
                "interface": values.get("interface", ""),
                "zephyr_support": values.get("zephyr_support", ""),
            }
        )
    if getattr(args, "as_json", False):
        print(json.dumps(rows, indent=2))
        return
    print("id\tinterface\tsupport\tdisplay_name")
    for row in rows:
        print(f"{row['id']}\t{row['interface']}\t{row['zephyr_support']}\t{row['display_name']}")


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
    # 显示某个示例的完整元数据、文件清单和 README。
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


def cmd_create(args: argparse.Namespace) -> None:
    # Creates a standalone project by copying a repository example.
    # 通过复制仓库示例来创建一个独立项目。
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

    # The MVP copies an example as-is; retargeting to another board needs pin and
    # overlay data the catalog does not carry yet.
    # MVP 原样复制示例;改投到别的板子需要目录里还没有的引脚和 overlay 数据。
    if args.board_id != example_board:
        raise CliError(
            f"Example {source_board}/{demo} targets board '{example_board}', "
            f"not '{args.board_id}'. Pass --board {example_board}."
        )

    if values.get("validation_status") == "unsupported":
        reason = values.get("unsupported_reason") or "marked unsupported"
        raise CliError(f"Cannot create from an unsupported example: {reason}.")

    out_dir = Path(args.output).expanduser().resolve()
    if out_dir.is_file():
        raise CliError(f"Output path is a file: {out_dir}.")
    if out_dir.is_dir() and any(out_dir.iterdir()) and not args.force:
        raise CliError(
            f"Output directory is not empty: {out_dir}. Use --force to write anyway."
        )
    out_dir.mkdir(parents=True, exist_ok=True)

    # Copy the whole example directory so optional files (such as app.overlay)
    # come along without a hardcoded file list.
    # 整目录复制示例,让可选文件(例如 app.overlay)无需硬编码清单就一并带上。
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


def cmd_build(args: argparse.Namespace) -> None:
    if args.app:
        example = resolve_app_example(args.board_id, args.app)
    else:
        example = select_example(args.board_id, args.example)
    run_west_build(args.board_id, example)


def cmd_flash(args: argparse.Namespace) -> None:
    if args.app:
        example = resolve_app_example(args.board_id, args.app)
    else:
        example = select_example(args.board_id, args.example)

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
        port = run_ra4m1_rom_flash(ra4m1_rom)
    else:
        run_west_build(args.board_id, example)
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
    if args.app:
        example = resolve_app_example(args.board_id, args.app)
    else:
        example = select_example(args.board_id, args.example)
    run_west_build(args.board_id, example)
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
