#!/usr/bin/env python3

from __future__ import annotations

import unittest
from unittest import mock

import seeed_zephyr


class FlashHintTests(unittest.TestCase):
    def test_raspberrypi_flash_error_adds_bootsel_hint(self) -> None:
        west_error = seeed_zephyr.CliError("Command failed with status 1: west flash")

        for board_id in ("xiao_rp2040", "xiao_rp2350"):
            with self.subTest(board_id=board_id):
                with mock.patch.object(seeed_zephyr, "uf2_mounts", return_value=["/Volumes/RPI-RP2"]):
                    with mock.patch.object(seeed_zephyr, "run_west", side_effect=west_error):
                        with self.assertRaises(seeed_zephyr.CliError) as context:
                            seeed_zephyr.run_west_flash(board_id)

                message = str(context.exception)
                self.assertIn("Command failed with status 1: west flash", message)
                self.assertIn("BOOTSEL", message)
                self.assertIn("UF2 mass storage", message)

    def test_raspberrypi_flash_requests_bootloader_before_west_flash(self) -> None:
        with mock.patch.object(seeed_zephyr, "uf2_mounts", return_value=[]):
            with mock.patch.object(seeed_zephyr, "detect_serial_port", return_value="/dev/cu.usbmodem1101"):
                with mock.patch.object(seeed_zephyr, "touch_serial_1200") as touch:
                    with mock.patch.object(
                        seeed_zephyr, "wait_for_uf2_mount", return_value="/Volumes/RPI-RP2"
                    ):
                        with mock.patch.object(seeed_zephyr, "run_west") as run_west:
                            selected_port = seeed_zephyr.run_west_flash("xiao_rp2040")

        self.assertEqual(selected_port, "/dev/cu.usbmodem1101")
        touch.assert_called_once_with("/dev/cu.usbmodem1101")
        run_west.assert_called_once_with(["flash"])

    def test_raspberrypi_flash_skips_touch_when_uf2_is_already_mounted(self) -> None:
        with mock.patch.object(seeed_zephyr, "uf2_mounts", return_value=["/Volumes/RPI-RP2"]):
            with mock.patch.object(seeed_zephyr, "touch_serial_1200") as touch:
                with mock.patch.object(seeed_zephyr, "run_west") as run_west:
                    selected_port = seeed_zephyr.run_west_flash("xiao_rp2040")

        self.assertIsNone(selected_port)
        touch.assert_not_called()
        run_west.assert_called_once_with(["flash"])

    def test_raspberrypi_flash_uses_explicit_port_for_bootloader_touch(self) -> None:
        with mock.patch.object(seeed_zephyr, "uf2_mounts", return_value=[]):
            with mock.patch.object(seeed_zephyr, "detect_serial_port") as detect:
                with mock.patch.object(seeed_zephyr, "touch_serial_1200") as touch:
                    with mock.patch.object(
                        seeed_zephyr, "wait_for_uf2_mount", return_value="/Volumes/RPI-RP2"
                    ):
                        with mock.patch.object(seeed_zephyr, "run_west"):
                            selected_port = seeed_zephyr.run_west_flash(
                                "xiao_rp2040", port="/dev/cu.usbmodem1101"
                            )

        self.assertEqual(selected_port, "/dev/cu.usbmodem1101")
        detect.assert_not_called()
        touch.assert_called_once_with("/dev/cu.usbmodem1101")

    def test_raspberrypi_flash_timeout_keeps_manual_bootsel_hint(self) -> None:
        with mock.patch.object(seeed_zephyr, "uf2_mounts", return_value=[]):
            with mock.patch.object(seeed_zephyr, "detect_serial_port", return_value="/dev/cu.usbmodem1101"):
                with mock.patch.object(seeed_zephyr, "touch_serial_1200"):
                    with mock.patch.object(
                        seeed_zephyr,
                        "wait_for_uf2_mount",
                        side_effect=seeed_zephyr.CliError(
                            "Timed out waiting for the UF2 mass storage volume."
                        ),
                    ):
                        with self.assertRaises(seeed_zephyr.CliError) as context:
                            seeed_zephyr.run_west_flash("xiao_rp2040")

        message = str(context.exception)
        self.assertIn("Timed out waiting for the UF2 mass storage volume", message)
        self.assertIn("BOOTSEL", message)

    def test_raspberrypi_touch_keeps_1200_baud_open_long_enough(self) -> None:
        with mock.patch.object(
            seeed_zephyr, "zephyr_venv_python", return_value=seeed_zephyr.Path("/tmp/venv/bin/python")
        ):
            with mock.patch.object(
                seeed_zephyr,
                "run_command_capture",
                return_value=seeed_zephyr.subprocess.CompletedProcess([], 0, ""),
            ) as run_capture:
                seeed_zephyr.touch_serial_1200("/dev/cu.usbmodem1101")

        command = run_capture.call_args.args[0]
        self.assertIn(str(seeed_zephyr.RP2_BOOTLOADER_TOUCH_SECONDS), command)
        self.assertGreaterEqual(seeed_zephyr.RP2_BOOTLOADER_TOUCH_SECONDS, 1.5)


class BuildCommandTests(unittest.TestCase):
    def test_raspberrypi_build_uses_bootmode_retention_snippet(self) -> None:
        example = {"path": "examples/boards/xiao_rp2040/blinky", "zephyr_target": "xiao_rp2040"}

        with mock.patch.object(seeed_zephyr, "ensure_chip_blobs"):
            with mock.patch.object(seeed_zephyr, "run_west") as run_west:
                seeed_zephyr.run_west_build("xiao_rp2040", example)

        run_west.assert_called_once_with(
            [
                "build",
                "-p",
                "always",
                "-b",
                "xiao_rp2040",
                "-S",
                "rp2-boot-mode-retention",
                str(seeed_zephyr.REPO_ROOT / "examples/boards/xiao_rp2040/blinky"),
            ]
        )

    def test_non_raspberrypi_build_does_not_use_bootmode_retention_snippet(self) -> None:
        example = {
            "path": "examples/boards/xiao_samd21/blinky",
            "zephyr_target": "seeeduino_xiao",
        }

        with mock.patch.object(seeed_zephyr, "ensure_chip_blobs"):
            with mock.patch.object(seeed_zephyr, "run_west") as run_west:
                seeed_zephyr.run_west_build("xiao_samd21", example)

        command = run_west.call_args.args[0]
        self.assertNotIn("-S", command)
        self.assertNotIn("rp2-boot-mode-retention", command)


if __name__ == "__main__":
    unittest.main()
