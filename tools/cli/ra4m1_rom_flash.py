#!/usr/bin/env python3
"""Flash firmware to XIAO RA4M1 via the Renesas ROM bootloader (045B:0261).

Standalone script invoked by seeed_zephyr.py through the Zephyr venv Python.

Usage:
    python ra4m1_rom_flash.py <serial_port> <bin_file>
"""

from __future__ import annotations

import os
import struct
import sys
import time

import serial
import serial.tools.list_ports

# Renesas ROM bootloader protocol commands
INQ_CMD = 0x00
ERA_CMD = 0x12
WRI_CMD = 0x13
ARE_CMD = 0x3B

CHUNK_SIZE = 256
BAUD = 9600
TIMEOUT = 5.0
ETX = 0x03
MAX_HANDSHAKE_RETRIES = 20


def _checksum(cmd: int, data: bytes | list[int]) -> tuple[int, int, int]:
    data_len = len(data)
    lnh = ((data_len + 1) & 0xFF00) >> 8
    lnl = (data_len + 1) & 0x00FF
    total = lnh + lnl + cmd
    for b in data:
        total += b if isinstance(b, int) else int(b, 16)
    return lnh, lnl, (~(total - 1)) & 0xFF


def pack_pkt(cmd: int, data: bytes, ack: bool = False) -> bytes:
    # Packet format: [SOD | LNH | LNL | CMD | DATA | SUM | ETX]
    # SOD = 0x81 for data packets from host, 0x01 for command packets
    sod = 0x81 if ack else 0x01
    lnh, lnl, chk = _checksum(cmd, data)
    fmt = f"<BBBB{len(data)}sBB"
    return struct.pack(fmt, sod, lnh, lnl, cmd, bytes(data), chk, ETX)


def unpack_pkt(data: bytearray) -> list[int]:
    # Response format: [0x81 | LNH | LNL | RES | DAT... | SUM | ETX]
    if len(data) < 7:
        raise ValueError(f"Response too short: {len(data)} bytes")
    sod, lnh, lnl, res = struct.unpack_from("<BBBB", data)
    if sod != 0x81:
        raise ValueError(f"Bad SOD: 0x{sod:02X}")
    pkt_len = ((lnh << 8) | lnl) - 1
    payload = list(data[4 : 4 + pkt_len])
    if res & 0x80:
        raise ValueError(f"MCU error: 0x{payload[0]:02X}" if payload else "MCU error")
    return payload


def send_recv(ser: serial.Serial, pkt: bytes, resp_len: int = 7) -> bytearray:
    ser.write(pkt)
    resp = bytearray()
    while len(resp) < resp_len:
        chunk = ser.read(resp_len - len(resp))
        if not chunk:
            raise TimeoutError(
                f"ROM bootloader did not respond (got {len(resp)}/{resp_len} bytes)"
            )
        resp += chunk
    return resp


def connect(port: str) -> serial.Serial:
    ser = serial.Serial(port, BAUD, timeout=TIMEOUT, write_timeout=TIMEOUT)
    time.sleep(0.3)

    # Check if already connected via INQ_CMD
    ser.write(pack_pkt(INQ_CMD, b""))
    info = ser.read(1)
    if info and info != b"\x00":
        info += ser.read(6)
        unpack_pkt(bytearray(info))
        return ser

    # Fresh handshake: send 0x55, expect 0xC3
    for i in range(MAX_HANDSHAKE_RETRIES):
        ser.write(bytes([0x55]))
        ret = ser.read(1)
        if ret and ret[0] == 0xC3:
            return ser

    raise RuntimeError(
        "ROM bootloader handshake failed. "
        "Verify the board is in ROM Boot mode (hold BOOT, tap RESET)."
    )


def int_to_addr_bytes(num: int) -> bytes:
    # Convert a 32-bit address to 4 big-endian bytes
    return struct.pack(">I", num)


def get_area_info(ser: serial.Serial) -> dict[int, dict]:
    cfg: dict[int, dict] = {}
    for i in range(3):
        pkt = pack_pkt(ARE_CMD, bytes([i]))
        resp = send_recv(ser, pkt, 23)
        msg = unpack_pkt(resp)
        raw = bytes(msg)
        koa, sad, ead, eau, wau = struct.unpack(">BIIII", raw)
        cfg[i] = {"SAD": sad, "EAD": ead, "ALIGN": eau, "WAU": wau}
    return cfg


def erase(ser: serial.Serial, start: int, end: int) -> None:
    addr_data = int_to_addr_bytes(start) + int_to_addr_bytes(end)
    resp = send_recv(ser, pack_pkt(ERA_CMD, addr_data), 7)
    unpack_pkt(resp)


def write_image(
    ser: serial.Serial, bin_path: str, start: int, end: int
) -> None:
    file_size = os.path.getsize(bin_path)

    # WRI_CMD setup
    addr_data = int_to_addr_bytes(start) + int_to_addr_bytes(end)
    resp = send_recv(ser, pack_pkt(WRI_CMD, addr_data), 7)
    unpack_pkt(resp)

    # Send data in CHUNK_SIZE-byte blocks
    written = 0
    with open(bin_path, "rb") as f:
        while written < file_size:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            if len(chunk) < CHUNK_SIZE:
                chunk += b"\x00" * (CHUNK_SIZE - len(chunk))

            resp = send_recv(ser, pack_pkt(WRI_CMD, chunk, ack=True), 7)
            unpack_pkt(resp)

            written += CHUNK_SIZE
            pct = min(100, written * 100 // file_size)
            print(
                f"\r  Writing: {pct}% ({min(written, file_size)}/{file_size})",
                end="",
                flush=True,
            )

    print(flush=True)


def main() -> None:
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <serial_port> <bin_file>", file=sys.stderr)
        sys.exit(1)

    port, bin_path = sys.argv[1], sys.argv[2]

    if not os.path.isfile(bin_path):
        print(f"Firmware file not found: {bin_path}", file=sys.stderr)
        sys.exit(1)

    file_size = os.path.getsize(bin_path)
    print(f"Firmware: {bin_path} ({file_size} bytes)")

    print("Connecting to ROM bootloader...", flush=True)
    ser = connect(port)

    cfg = get_area_info(ser)
    sector_size = cfg[0]["ALIGN"]
    blocks = (file_size + sector_size - 1) // sector_size
    end_addr = blocks * sector_size - 1

    print(f"Erasing {blocks} sectors ({blocks * sector_size} bytes)...", flush=True)
    erase(ser, 0x0, end_addr)

    print(f"Writing {file_size} bytes ({CHUNK_SIZE}-byte chunks)...", flush=True)
    write_image(ser, bin_path, 0x0, end_addr)

    ser.close()
    print("ROM boot flash complete. Press RESET to boot the new firmware.")


if __name__ == "__main__":
    main()
