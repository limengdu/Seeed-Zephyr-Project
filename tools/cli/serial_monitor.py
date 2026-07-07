#!/usr/bin/env python3
#
# Reconnecting serial monitor.
#   Streams a serial port to the terminal and, when the device drops, waits and
#   reconnects instead of exiting. Press Ctrl+] to quit.
#
# 可重连的串口监视器：
#   把串口输出打到终端；设备掉线时保持等待并自动重连，而不是退出。按 Ctrl+] 退出。

from __future__ import annotations

import argparse
import os
import select
import sys
import time

import serial
from serial.tools import list_ports

EXIT_CHAR = 0x1D  # Ctrl+]
POLL_INTERVAL_S = 0.3
READ_CHUNK = 1024

try:
    import termios
    import tty

    _HAS_TERMIOS = True
except ImportError:  # pragma: no cover - non-POSIX hosts
    _HAS_TERMIOS = False


def port_present(port: str) -> bool:
    # True when the device path exists or is listed among serial ports.
    # 当设备路径存在，或出现在串口列表中时返回 True。
    if os.path.exists(port):
        return True
    return any(p.device == port for p in list_ports.comports())


def write_out(data: bytes) -> None:
    os.write(sys.stdout.fileno(), data)
    # os.write is unbuffered, so no explicit flush is needed here.


def status(message: str) -> None:
    write_out(f"\r\n[seeed-zephyr monitor] {message}\r\n".encode())


def stdin_has_exit(fd: int) -> bool:
    # Reads pending stdin and reports whether Ctrl+] was pressed. Other bytes are
    # returned to the caller for forwarding via the module-level _pending buffer.
    # 读取待处理的 stdin，判断是否按了 Ctrl+]；其它字节通过 _pending 交回调用方转发。
    data = os.read(fd, 64)
    if EXIT_CHAR in data:
        return True
    _pending.extend(data)
    return False


_pending = bytearray()


def wait_for_port(port: str, stdin_fd: int | None) -> bool:
    # Blocks until the port reappears. Returns False if the user asked to quit.
    # 阻塞直到端口重新出现；用户请求退出时返回 False。
    while not port_present(port):
        if stdin_fd is not None:
            ready, _, _ = select.select([stdin_fd], [], [], POLL_INTERVAL_S)
            if ready and stdin_has_exit(stdin_fd):
                return False
        else:
            time.sleep(POLL_INTERVAL_S)
    return True


def read_serial_chunk(ser: serial.Serial) -> bytes | None:
    # Reads serial data. Empty bytes mean no data while the port is still present;
    # None means the monitor should reconnect.
    # 读取串口数据。空 bytes 表示端口仍在但暂无数据；None 表示需要重连。
    try:
        data = ser.read(READ_CHUNK)
    except (OSError, serial.SerialException):
        return None

    if data:
        return data

    port = getattr(ser, "port", None) or getattr(ser, "name", None)
    if isinstance(port, str) and not port_present(port):
        return None
    return b""


def pump(ser: serial.Serial, stdin_fd: int | None) -> bool:
    # Streams the port until it drops (returns True to reconnect) or the user quits
    # (returns False). stdin bytes are forwarded to the device; Ctrl+] quits.
    # 传输串口直到掉线（返回 True 以重连）或用户退出（返回 False）。stdin 转发到设备，Ctrl+] 退出。
    ser_fd = ser.fileno()
    if _pending:
        try:
            ser.write(bytes(_pending))
        except (OSError, serial.SerialException):
            return True
        _pending.clear()

    watch = [ser_fd] if stdin_fd is None else [ser_fd, stdin_fd]
    while True:
        try:
            ready, _, _ = select.select(watch, [], [], 0.5)
        except (OSError, ValueError):
            return True

        if ser_fd in ready:
            data = read_serial_chunk(ser)
            if data is None:
                return True
            if data:
                write_out(data)

        if stdin_fd is not None and stdin_fd in ready:
            try:
                if stdin_has_exit(stdin_fd):
                    return False
                if _pending:
                    ser.write(bytes(_pending))
                    _pending.clear()
            except (OSError, serial.SerialException):
                return True


def monitor(port: str, baud: int) -> int:
    is_tty = _HAS_TERMIOS and sys.stdin.isatty()
    stdin_fd = sys.stdin.fileno() if is_tty else None
    saved = termios.tcgetattr(stdin_fd) if is_tty else None
    if is_tty:
        tty.setraw(stdin_fd)

    try:
        first = True
        while True:
            if not port_present(port):
                status(f"waiting for {port} ... (Ctrl+] to quit)")
                if not wait_for_port(port, stdin_fd):
                    return 0
            try:
                ser = serial.Serial(port, baud, timeout=0)
            except serial.SerialException:
                time.sleep(POLL_INTERVAL_S)
                continue

            status(
                f"{'connected' if first else 'reconnected'} {port} @ {baud} baud "
                "(Ctrl+] to quit)"
            )
            first = False
            reconnect = pump(ser, stdin_fd)
            try:
                ser.close()
            except Exception:  # noqa: BLE001 - closing a dropped port may raise
                pass
            if not reconnect:
                return 0
            status("device disconnected — waiting to reconnect (Ctrl+] to quit)")
    finally:
        if saved is not None:
            termios.tcsetattr(stdin_fd, termios.TCSADRAIN, saved)
        write_out(b"\r\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Reconnecting serial monitor.")
    parser.add_argument("port", help="Serial port device path.")
    parser.add_argument("baud", type=int, nargs="?", default=115200, help="Baud rate.")
    args = parser.parse_args()
    try:
        return monitor(args.port, args.baud)
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
