#!/usr/bin/env python3

from __future__ import annotations

import argparse
import datetime as dt
import os
import platform
import shutil
import subprocess
import sys
import time
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
    debug.set_defaults(func=cmd_debug)

    monitor = subparsers.add_parser("monitor", help="Open a board monitor.")
    monitor.add_argument("board_id", help="Board id such as xiao_esp32c6.")
    monitor.add_argument("--port", default=None, help="Serial port device path.")
    monitor.add_argument(
        "--baud",
        type=int,
        default=115200,
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
        return "Use the WSL2 setup path, then install it inside WSL2 with scripts/setup-linux.sh"

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


def require_flash_tools(board_id: str) -> None:
    board = require_board(board_id)
    if board["vendor"] == "espressif":
        require_west_venv_tool(
            "esptool",
            "Run setup again, or install it with: "
            f"{zephyr_workspace()}/.venv/bin/python -m pip install esptool",
        )
    if board["target"] == "seeeduino_xiao":
        require_host_tool("bossac", bossac_install_hint())


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
    if uses_uf2_runner(board):
        port = prepare_uf2_bootloader(board_id, port)

    command = ["flash"]
    if board["id"] in UF2_RUNNER_BOARD_IDS:
        command.extend(["--runner", "uf2"])
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
    # Builds the selected repository example through Zephyr's west command.
    # 通过 Zephyr 的 west 命令构建选中的仓库示例。
    board = require_board(board_id)
    target = example.get("zephyr_target") or board["target"]
    example_dir = REPO_ROOT / example["path"]
    ensure_chip_blobs(board)
    print(f"Building {example['path']} for {target}...", flush=True)
    command = ["build", "-p", "always", "-b", target]
    if board["vendor"] == "raspberrypi":
        command.extend(["-S", RP2_BOOTLOADER_SNIPPET])
    command.append(str(example_dir))
    run_west(command)
    print(f"Build succeeded: {example['path']}", flush=True)


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
        run_monitor(args.board_id, port=monitor_port, baud=args.baud)


def cmd_debug(args: argparse.Namespace) -> None:
    example = require_supported_example(args.board_id)
    run_west_build(args.board_id, example)
    try:
        run_west(["debug"])
    except CliError as error:
        raise CliError(f"{error}\nHint: {DEBUG_HINT}") from error


def cmd_monitor(args: argparse.Namespace) -> None:
    require_supported_example(args.board_id)
    run_monitor(args.board_id, port=args.port, baud=args.baud)


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
    run_west_flash(args.board_id)

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
