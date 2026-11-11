#!/usr/bin/env python3
"""Upload a signed XIAO nRF54LM20B image through the factory USB loader.
通过出厂 USB 加载器上传 XIAO nRF54LM20B 签名镜像。
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import io
import struct
import sys
import time
from pathlib import Path

CHUNK_SIZE = 64
RESPONSE_TIMEOUT = 15.0
MAX_ATTEMPTS = 3
PACKET_MARKER = b"\x06\x09"
FRAGMENT_MARKER = b"\x04\x14"
SMP_HEADER = struct.Struct(">BBHHBB")


class UploadError(Exception):
    pass


def _cbor_length(major: int, value: int) -> bytes:
    if value < 24:
        return bytes([(major << 5) | value])
    for additional, size in ((24, 1), (25, 2), (26, 4), (27, 8)):
        if value < 1 << (size * 8):
            return bytes([(major << 5) | additional]) + value.to_bytes(size, "big")
    raise UploadError("CBOR integer is too large.")


def cbor_encode(value: object) -> bytes:
    # Encodes the maps, integers, and strings used by image-upload requests.
    # 编码镜像上传请求使用的映射、整数和字符串。
    if isinstance(value, bool):
        return b"\xf5" if value else b"\xf4"
    if isinstance(value, int):
        return _cbor_length(0, value) if value >= 0 else _cbor_length(1, -1 - value)
    if isinstance(value, bytes):
        return _cbor_length(2, len(value)) + value
    if isinstance(value, str):
        encoded = value.encode("utf-8")
        return _cbor_length(3, len(encoded)) + encoded
    if isinstance(value, dict):
        return _cbor_length(5, len(value)) + b"".join(
            cbor_encode(key) + cbor_encode(item) for key, item in value.items()
        )
    raise UploadError(f"Unsupported CBOR value: {type(value).__name__}")


def cbor_decode(data: bytes) -> object:
    # Decodes definite and indefinite response maps, including nested SMP errors.
    # 解码固定长度和不定长响应映射，包括嵌套的 SMP 错误。
    stream = io.BytesIO(data)
    end = object()

    def read_exact(size: int) -> bytes:
        value = stream.read(size)
        if len(value) != size:
            raise UploadError("Truncated CBOR response.")
        return value

    def read_value(depth: int = 0) -> object:
        if depth > 16:
            raise UploadError("CBOR response is too deeply nested.")
        first = read_exact(1)[0]
        if first == 0xFF:
            return end
        major, additional = first >> 5, first & 31
        if major == 7 and additional in (20, 21):
            return additional == 21
        if additional < 24:
            size = additional
        elif additional in (24, 25, 26, 27):
            size = int.from_bytes(read_exact(1 << (additional - 24)), "big")
        elif major == 5 and additional == 31:
            size = None
        else:
            raise UploadError("Unsupported CBOR response type.")
        if major in (0, 1):
            return size if major == 0 else -1 - size
        if major in (2, 3):
            value = read_exact(size)
            return value if major == 2 else value.decode("utf-8")
        if major == 5:
            result = {}
            while size is None or len(result) < size:
                key = read_value(depth + 1)
                if key is end:
                    if size is not None:
                        raise UploadError("Unexpected CBOR map terminator.")
                    break
                if not isinstance(key, str) or key in result:
                    raise UploadError("Invalid CBOR response key.")
                value = read_value(depth + 1)
                if value is end:
                    raise UploadError("Missing CBOR response value.")
                result[key] = value
            return result
        raise UploadError("Unsupported CBOR response type.")

    result = read_value()
    if not isinstance(result, dict) or stream.read(1):
        raise UploadError("Expected one CBOR response map.")
    return result


def serial_frames(packet: bytes) -> list[bytes]:
    # Splits a length-prefixed SMP packet and its CRC into 127-byte serial frames.
    # 将带长度和 CRC 的 SMP 消息拆成最多 127 字节的串口帧。
    raw = struct.pack(">H", len(packet) + 2) + packet + struct.pack(">H", binascii.crc_hqx(packet, 0))
    return [
        (PACKET_MARKER if offset == 0 else FRAGMENT_MARKER)
        + base64.b64encode(raw[offset : offset + 93])
        + b"\n"
        for offset in range(0, len(raw), 93)
    ]


class SmpClient:
    def __init__(self, port):
        self.port = port
        self.sequence = 0

    def _response(self, group: int, command: int, sequence: int) -> dict:
        # Reassembles matching SMP replies and validates the header and CRC.
        # 重组匹配的 SMP 回应，并校验消息头和 CRC。
        deadline = time.monotonic() + RESPONSE_TIMEOUT
        assembled = bytearray()
        expected = None
        while time.monotonic() < deadline:
            line = self.port.readline(512).rstrip(b"\r\n")
            if line.startswith(PACKET_MARKER):
                raw = base64.b64decode(line[2:], validate=True)
                if len(raw) < 2:
                    raise UploadError("Missing serial packet length.")
                expected = int.from_bytes(raw[:2], "big")
                if not SMP_HEADER.size + 2 <= expected <= 4096:
                    raise UploadError("Invalid serial packet length.")
                assembled = bytearray(raw[2:])
            elif line.startswith(FRAGMENT_MARKER) and expected is not None:
                assembled.extend(base64.b64decode(line[2:], validate=True))
            else:
                continue
            if len(assembled) < expected:
                continue
            if len(assembled) != expected or binascii.crc_hqx(assembled, 0) != 0:
                raise UploadError("Serial response checksum mismatch.")
            operation, flags, length, reply_group, reply_sequence, reply_command = SMP_HEADER.unpack(
                assembled[: SMP_HEADER.size]
            )
            if (reply_group, reply_sequence, reply_command) != (group, sequence, command):
                expected = None
                continue
            if operation != 11 or flags != 0 or length != expected - SMP_HEADER.size - 2:
                raise UploadError("Invalid SMP response header.")
            return cbor_decode(assembled[SMP_HEADER.size : -2])
        raise TimeoutError("Timed out waiting for the firmware loader response.")

    def request(self, group: int, command: int, body: dict) -> dict:
        # Retries one SMP v2 write with the same sequence number after a lost response.
        # 回应丢失时，使用相同序号重试一条 SMP v2 写请求。
        payload = cbor_encode(body)
        sequence = self.sequence
        self.sequence = (sequence + 1) % 256
        packet = SMP_HEADER.pack(10, 0, len(payload), group, sequence, command) + payload
        for attempt in range(MAX_ATTEMPTS):
            for frame in serial_frames(packet):
                self.port.write(frame)
            self.port.flush()
            try:
                response = self._response(group, command, sequence)
            except TimeoutError:
                if attempt + 1 == MAX_ATTEMPTS:
                    raise
                print("Retrying firmware loader request...", flush=True)
                continue
            if response.get("rc", 0) != 0 or "err" in response:
                raise UploadError(f"Firmware loader rejected the request: {response}")
            return response
        raise UploadError("Firmware loader request failed.")


def upload_image(client: SmpClient, image: bytes) -> None:
    # Sends a SHA-256 transfer digest and advances through acknowledged image offsets.
    # 发送 SHA-256 传输摘要，并按加载器确认的镜像位置继续上传。
    if len(image) < 32 or image[:4] != b"\x3d\xb8\xf3\x96":
        raise UploadError("Expected a signed MCUboot image.")
    digest = hashlib.sha256(image).digest()
    offset = 0
    progress = -1
    while offset < len(image):
        body = {"off": offset, "data": image[offset : offset + CHUNK_SIZE]}
        if offset == 0:
            body.update({"image": 0, "len": len(image), "sha": digest})
        response = client.request(1, 1, body)
        next_offset = response.get("off")
        if type(next_offset) is not int or not offset < next_offset <= len(image):
            raise UploadError(f"Unexpected image upload offset: {response}")
        offset = next_offset
        percent = offset * 100 // len(image)
        if percent // 5 > progress or offset == len(image):
            progress = percent // 5
            print(f"Uploading signed image: {percent}% ({offset}/{len(image)} bytes)", flush=True)
    client.request(0, 5, {})
    print("nRF54LM20B signed image uploaded; the board is resetting.", flush=True)


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: nrf54lm20b_smp_upload.py <serial_port> <signed_image>", file=sys.stderr)
        return 1
    import serial

    try:
        image = Path(sys.argv[2]).read_bytes()
        with serial.Serial(sys.argv[1], 115200, timeout=0.5, write_timeout=5) as port:
            port.reset_input_buffer()
            upload_image(SmpClient(port), image)
    except (OSError, ValueError, UploadError, TimeoutError, serial.SerialException) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
