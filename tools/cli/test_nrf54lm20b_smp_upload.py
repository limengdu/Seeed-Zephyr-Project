#!/usr/bin/env python3

from __future__ import annotations

import base64
import binascii
import hashlib
import unittest
from unittest import mock

import nrf54lm20b_smp_upload as uploader


class CborTests(unittest.TestCase):
    def test_upload_fields_have_standard_cbor_encoding(self) -> None:
        self.assertEqual(
            uploader.cbor_encode({"off": 0, "data": b"\x01\x02"}),
            bytes.fromhex("a2636f6666006464617461420102"),
        )

    def test_decodes_indefinite_loader_response(self) -> None:
        self.assertEqual(uploader.cbor_decode(b"\xbf\x63off\x19\x01\x00\xff"), {"off": 256})

    def test_decodes_nested_image_group_error(self) -> None:
        self.assertEqual(
            uploader.cbor_decode(b"\xbf\x63err\xbf\x65group\x01\x62rc\x18\x18\xff\xff"),
            {"err": {"group": 1, "rc": 24}},
        )

    def test_rejects_truncated_response_and_extra_payload(self) -> None:
        for data in (b"\xa1\x63off\x19\x01", b"\xa0\x00"):
            with self.subTest(data=data), self.assertRaises(uploader.UploadError):
                uploader.cbor_decode(data)


class SerialProtocolTests(unittest.TestCase):
    def test_serial_frames_preserve_packet_and_standard_crc(self) -> None:
        self.assertEqual(binascii.crc_hqx(b"123456789", 0), 0x31C3)
        packet = bytes(range(256))
        frames = uploader.serial_frames(packet)
        self.assertTrue(frames[0].startswith(b"\x06\x09"))
        self.assertTrue(all(frame.startswith(b"\x04\x14") for frame in frames[1:]))
        self.assertTrue(all(len(frame) <= 127 and frame.endswith(b"\n") for frame in frames))
        raw = b"".join(base64.b64decode(frame[2:-1]) for frame in frames)
        self.assertEqual(int.from_bytes(raw[:2], "big"), len(packet) + 2)
        self.assertEqual(raw[2:-2], packet)
        self.assertEqual(binascii.crc_hqx(raw[2:], 0), 0)

    def test_decodes_framed_loader_acknowledgment(self) -> None:
        body = b"\xbf\x63off\x18\x40\xff"
        packet = uploader.SMP_HEADER.pack(11, 0, len(body), 1, 7, 1) + body
        port = mock.Mock()
        port.readline.side_effect = uploader.serial_frames(packet)
        self.assertEqual(uploader.SmpClient(port)._response(1, 1, 7), {"off": 64})

    def test_rejects_corrupt_serial_response(self) -> None:
        body = b"\xa1\x63off\x18\x40"
        packet = uploader.SMP_HEADER.pack(11, 0, len(body), 1, 7, 1) + body
        frame = uploader.serial_frames(packet)[0]
        raw = bytearray(base64.b64decode(frame[2:-1]))
        raw[-1] ^= 1
        port = mock.Mock()
        port.readline.return_value = b"\x06\x09" + base64.b64encode(raw) + b"\n"
        with self.assertRaisesRegex(uploader.UploadError, "checksum"):
            uploader.SmpClient(port)._response(1, 1, 7)

    def test_lost_response_retries_identical_request(self) -> None:
        port = mock.Mock()
        client = uploader.SmpClient(port)
        with mock.patch.object(client, "_response", side_effect=[TimeoutError(), {"off": 64}]):
            self.assertEqual(client.request(1, 1, {"off": 0}), {"off": 64})
        self.assertEqual(port.write.call_count, 2)
        self.assertEqual(port.write.call_args_list[0], port.write.call_args_list[1])

    def test_loader_error_stops_request(self) -> None:
        client = uploader.SmpClient(mock.Mock())
        with mock.patch.object(client, "_response", return_value={"err": {"group": 1, "rc": 24}}):
            with self.assertRaisesRegex(uploader.UploadError, "24"):
                client.request(1, 1, {"off": 0})


class ImageUploadTests(unittest.TestCase):
    def test_upload_uses_sha256_bounded_chunks_and_reset_after_ack(self) -> None:
        image = b"\x3d\xb8\xf3\x96" + bytes(range(255))
        client = mock.Mock()

        def acknowledge(group, command, body):
            if group == 0:
                self.assertEqual(command, 5)
                return {}
            return {"off": body["off"] + len(body["data"])}

        client.request.side_effect = acknowledge
        uploader.upload_image(client, image)
        calls = client.request.call_args_list
        first = calls[0].args[2]
        self.assertEqual(first["sha"], hashlib.sha256(image).digest())
        self.assertEqual(len(first["sha"]), 32)
        self.assertEqual(first["len"], len(image))
        self.assertEqual(first["image"], 0)
        self.assertEqual(b"".join(call.args[2]["data"] for call in calls[:-1]), image)
        for call in calls[1:-1]:
            self.assertEqual(set(call.args[2]), {"off", "data"})
        self.assertTrue(all(len(call.args[2]["data"]) <= 64 for call in calls[:-1]))
        self.assertEqual(calls[-1], mock.call(0, 5, {}))

    def test_resumes_from_loader_acknowledged_offset(self) -> None:
        image = b"\x3d\xb8\xf3\x96" + b"\xff" * 196
        client = mock.Mock()
        client.request.side_effect = [{"off": 128}, {"off": 192}, {"off": 200}, {}]
        uploader.upload_image(client, image)
        self.assertEqual(client.request.call_args_list[1].args[2]["off"], 128)

    def test_invalid_offset_stops_before_reset(self) -> None:
        image = b"\x3d\xb8\xf3\x96" + b"\xff" * 60
        for offset in (0, -1, len(image) + 1, None, True):
            with self.subTest(offset=offset):
                client = mock.Mock()
                client.request.return_value = {"off": offset}
                with self.assertRaises(uploader.UploadError):
                    uploader.upload_image(client, image)
                self.assertEqual(client.request.call_count, 1)

    def test_rejects_unsigned_input_before_upload(self) -> None:
        client = mock.Mock()
        with self.assertRaises(uploader.UploadError):
            uploader.upload_image(client, b"\x00" * 64)
        client.request.assert_not_called()


if __name__ == "__main__":
    unittest.main()
