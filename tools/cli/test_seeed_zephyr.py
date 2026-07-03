#!/usr/bin/env python3

from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
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

    def test_xiao_nrf52840_flash_uses_uf2_runner(self) -> None:
        with mock.patch.object(seeed_zephyr, "uf2_mounts", return_value=["/Volumes/XIAO-SENSE"]):
            with mock.patch.object(seeed_zephyr, "run_west") as run_west:
                selected_port = seeed_zephyr.run_west_flash("xiao_nrf52840")

        self.assertIsNone(selected_port)
        run_west.assert_called_once_with(["flash", "--runner", "uf2"])

    def test_xiao_mg24_flash_uses_zephyr_pyocd_runner(self) -> None:
        board = {"id": "xiao_mg24", "vendor": "silabs", "target": "xiao_mg24"}

        with mock.patch.object(seeed_zephyr, "require_board", return_value=board):
            with mock.patch.object(seeed_zephyr, "run_west") as run_west:
                selected_port = seeed_zephyr.run_west_flash("xiao_mg24")

        self.assertIsNone(selected_port)
        run_west.assert_called_once_with(["flash", "--runner", "pyocd"])

    def test_xiao_mg24_requires_pyocd_pack(self) -> None:
        board = {"id": "xiao_mg24", "vendor": "silabs", "target": "xiao_mg24"}

        with mock.patch.object(seeed_zephyr, "require_board", return_value=board):
            with mock.patch.object(seeed_zephyr, "pyocd_target_available", return_value=False):
                with self.assertRaises(seeed_zephyr.CliError) as context:
                    seeed_zephyr.require_flash_tools("xiao_mg24")

        message = str(context.exception)
        self.assertIn("pyocd runner", message)
        self.assertIn("pyocd pack install EFR32MG24B220F1536IM48", message)
        self.assertIn("EFR32MG24B220F1536IM48", message)

    def test_xiao_ra4m1_requires_dfu_util(self) -> None:
        board = {"id": "xiao_ra4m1", "vendor": "renesas", "target": "xiao_ra4m1"}

        with mock.patch.object(seeed_zephyr, "require_board", return_value=board):
            with mock.patch.object(seeed_zephyr, "dfu_util_path", return_value=None):
                with self.assertRaises(seeed_zephyr.CliError) as context:
                    seeed_zephyr.require_flash_tools("xiao_ra4m1")

        message = str(context.exception)
        self.assertIn("dfu-util", message)
        self.assertIn("xiao_ra4m1", message)
        self.assertNotIn("rfp-cli", message)

    def test_xiao_ra4m1_rom_boot_skips_dfu_util_check(self) -> None:
        board = {"id": "xiao_ra4m1", "vendor": "renesas", "target": "xiao_ra4m1"}

        with mock.patch.object(seeed_zephyr, "require_board", return_value=board):
            with mock.patch.object(seeed_zephyr, "dfu_util_path", return_value=None):
                seeed_zephyr.require_flash_tools("xiao_ra4m1", rom_boot=True)

    def test_wait_for_ra4m1_rom_boot_detach_returns_after_port_disappears(self) -> None:
        with mock.patch.object(
            seeed_zephyr, "ra4m1_rom_boot_port", side_effect=["/dev/cu.usbmodem1101", None]
        ):
            with mock.patch.object(seeed_zephyr.time, "sleep"):
                seeed_zephyr.wait_for_ra4m1_rom_boot_detach(timeout_seconds=1)

    def test_xiao_ra4m1_flash_uses_dfu_util(self) -> None:
        board = {"id": "xiao_ra4m1", "vendor": "renesas", "target": "xiao_ra4m1"}
        dfu_util = seeed_zephyr.Path("/tmp/dfu-util")
        image = seeed_zephyr.Path("/tmp/zephyr.ra4m1.dfu.bin")

        with mock.patch.object(seeed_zephyr, "require_board", return_value=board):
            with mock.patch.object(seeed_zephyr, "prepare_ra4m1_dfu_image", return_value=image) as prepare:
                with mock.patch.object(seeed_zephyr, "dfu_util_path", return_value=dfu_util):
                    with mock.patch.object(
                        seeed_zephyr, "prepare_ra4m1_dfu_bootloader", return_value=None
                    ) as prepare_dfu:
                        with mock.patch.object(seeed_zephyr, "run_command") as run_command:
                            selected_port = seeed_zephyr.run_west_flash("xiao_ra4m1")

        self.assertIsNone(selected_port)
        prepare.assert_called_once_with()
        prepare_dfu.assert_called_once_with(None)
        run_command.assert_called_once_with(
            [
                str(dfu_util),
                "--device",
                "2886:0049,:8049",
                "-D",
                str(image),
                "-a",
                "0",
                "-R",
            ],
            cwd=seeed_zephyr.zephyr_workspace(),
            env=seeed_zephyr.west_command_env(),
        )

    def test_ra4m1_dfu_image_excludes_option_setting_section(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = seeed_zephyr.Path(tmpdir)
            build_dir = workspace / "build" / "zephyr"
            build_dir.mkdir(parents=True)
            (build_dir / "zephyr.elf").write_bytes(b"ELF")

            def create_image(*_args, **_kwargs) -> None:
                (build_dir / "zephyr.ra4m1.dfu.bin").write_bytes(b"BIN")

            with mock.patch.object(seeed_zephyr, "zephyr_workspace", return_value=workspace):
                with mock.patch.object(
                    seeed_zephyr,
                    "zephyr_objcopy_path",
                    return_value=seeed_zephyr.Path("/tmp/arm-zephyr-eabi-objcopy"),
                ):
                    with mock.patch.object(seeed_zephyr, "run_command", side_effect=create_image) as run_command:
                        image = seeed_zephyr.prepare_ra4m1_dfu_image()

        self.assertEqual(image, workspace / "build" / "zephyr" / "zephyr.ra4m1.dfu.bin")
        command = run_command.call_args.args[0]
        self.assertIn(".option_setting_osis", command)
        self.assertIn("-O", command)
        self.assertIn("binary", command)

    def test_ra4m1_rom_flash_invokes_rom_flash_script(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = seeed_zephyr.Path(tmpdir)
            build_dir = workspace / "build" / "zephyr"
            build_dir.mkdir(parents=True)
            python = workspace / "venv" / "bin" / "python"
            bootloader = workspace / "ra4m1_dfu.bin"
            app_image = build_dir / "zephyr.ra4m1.dfu.bin"
            bootloader.write_bytes(b"\xff" * 16384)
            app_image.write_bytes(b"APP")

            with mock.patch.object(seeed_zephyr, "prepare_ra4m1_dfu_image", return_value=app_image):
                with mock.patch.object(seeed_zephyr, "RA4M1_DFU_BOOTLOADER_BIN", bootloader):
                    with mock.patch.object(seeed_zephyr, "zephyr_venv_python", return_value=python):
                        with mock.patch.object(seeed_zephyr, "zephyr_workspace", return_value=workspace):
                            with mock.patch.object(seeed_zephyr, "west_command_env", return_value={}):
                                with mock.patch.object(seeed_zephyr, "run_command") as run_command:
                                    result = seeed_zephyr.run_ra4m1_rom_flash("/dev/cu.usbmodem1101")

        combined_image = workspace / "build" / "zephyr" / "zephyr.ra4m1.combined.bin"

        self.assertIsNone(result)
        run_command.assert_called_once_with(
            [
                str(python),
                str(seeed_zephyr.RA4M1_ROM_FLASH_SCRIPT),
                "/dev/cu.usbmodem1101",
                str(combined_image),
            ],
            cwd=workspace,
            env={},
        )
        self.assertTrue(str(run_command.call_args.args[0][-1]).endswith("zephyr.ra4m1.combined.bin"))

    def test_ra4m1_rom_flash_combines_bootloader_and_app(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = seeed_zephyr.Path(tmpdir)
            build_dir = workspace / "build" / "zephyr"
            build_dir.mkdir(parents=True)
            bootloader = workspace / "ra4m1_dfu.bin"
            app_image = build_dir / "zephyr.ra4m1.dfu.bin"
            bootloader.write_bytes(b"BOOTLOADER")
            app_image.write_bytes(b"APP")

            with mock.patch.object(seeed_zephyr, "prepare_ra4m1_dfu_image", return_value=app_image):
                with mock.patch.object(seeed_zephyr, "RA4M1_DFU_BOOTLOADER_BIN", bootloader):
                    with mock.patch.object(seeed_zephyr, "zephyr_venv_python", return_value=workspace / "python"):
                        with mock.patch.object(seeed_zephyr, "zephyr_workspace", return_value=workspace):
                            with mock.patch.object(seeed_zephyr, "west_command_env", return_value={}):
                                with mock.patch.object(seeed_zephyr, "run_command") as run_command:
                                    seeed_zephyr.run_ra4m1_rom_flash("/dev/cu.usbmodem1101")

            combined_image = build_dir / "zephyr.ra4m1.combined.bin"
            self.assertEqual(combined_image.read_bytes(), b"BOOTLOADERAPP")
            self.assertEqual(str(combined_image), run_command.call_args.args[0][-1])

    def test_ra4m1_dfu_detection_accepts_runtime_and_bootloader_ids(self) -> None:
        result = seeed_zephyr.subprocess.CompletedProcess(
            [],
            0,
            "Found Runtime: [2886:0049]\nFound DFU: [2886:8049]\n",
        )

        with mock.patch.object(seeed_zephyr, "run_command_capture", return_value=result):
            self.assertTrue(seeed_zephyr.ra4m1_dfu_device_available())

    def test_ra4m1_flash_requests_bootloader_over_serial_before_dfu(self) -> None:
        with mock.patch.object(seeed_zephyr, "ra4m1_dfu_device_available", side_effect=[False, True]):
            with mock.patch.object(seeed_zephyr, "ra4m1_rom_boot_port", return_value=None):
                with mock.patch.object(seeed_zephyr, "detect_serial_port", return_value="/dev/cu.usbmodem1101"):
                    with mock.patch.object(seeed_zephyr, "touch_serial_1200") as touch:
                        with mock.patch.object(seeed_zephyr.time, "sleep"):
                            selected_port = seeed_zephyr.prepare_ra4m1_dfu_bootloader(None)

        self.assertEqual(selected_port, "/dev/cu.usbmodem1101")
        touch.assert_called_once_with("/dev/cu.usbmodem1101")

    def test_ra4m1_flash_skips_serial_touch_when_dfu_is_already_visible(self) -> None:
        with mock.patch.object(seeed_zephyr, "ra4m1_dfu_device_available", return_value=True):
            with mock.patch.object(seeed_zephyr, "detect_serial_port") as detect:
                with mock.patch.object(seeed_zephyr, "touch_serial_1200") as touch:
                    selected_port = seeed_zephyr.prepare_ra4m1_dfu_bootloader("/dev/cu.usbmodem1101")

        self.assertEqual(selected_port, "/dev/cu.usbmodem1101")
        detect.assert_not_called()
        touch.assert_not_called()

    def test_ra4m1_flash_timeout_mentions_manual_dfu(self) -> None:
        with mock.patch.object(seeed_zephyr, "ra4m1_dfu_device_available", return_value=False):
            with mock.patch.object(seeed_zephyr, "ra4m1_rom_boot_port", return_value=None):
                with mock.patch.object(seeed_zephyr, "detect_serial_port", return_value="/dev/cu.usbmodem1101"):
                    with mock.patch.object(seeed_zephyr, "touch_serial_1200"):
                        with mock.patch.object(seeed_zephyr.time, "sleep"):
                            with self.assertRaises(seeed_zephyr.CliError) as context:
                                seeed_zephyr.prepare_ra4m1_dfu_bootloader(
                                    None, timeout_seconds=0, poll_seconds=0
                                )

        message = str(context.exception)
        self.assertIn("DFU bootloader", message)
        self.assertIn("BOOT", message)

    def test_ra4m1_flash_stops_on_rom_boot_serial(self) -> None:
        with mock.patch.object(seeed_zephyr, "ra4m1_dfu_device_available", return_value=False):
            with mock.patch.object(seeed_zephyr, "ra4m1_rom_boot_port", return_value="/dev/cu.usbmodem1101"):
                with mock.patch.object(seeed_zephyr, "detect_serial_port") as detect:
                    with mock.patch.object(seeed_zephyr, "touch_serial_1200") as touch:
                        with self.assertRaises(seeed_zephyr.CliError) as context:
                            seeed_zephyr.prepare_ra4m1_dfu_bootloader(None)

        message = str(context.exception)
        self.assertIn("Renesas ROM bootloader", message)
        self.assertIn("seeed-zephyr flash xiao_ra4m1", message)
        detect.assert_not_called()
        touch.assert_not_called()

    def test_ra4m1_example_supports_1200_baud_bootloader_request(self) -> None:
        source = (
            seeed_zephyr._REPO_ROOT
            / "examples"
            / "boards"
            / "xiao_ra4m1"
            / "blinky"
            / "src"
            / "main.c"
        ).read_text(encoding="utf-8")

        self.assertIn("UART_LINE_CTRL_BAUD_RATE", source)
        self.assertIn("RA4M1_BOOTLOADER_BAUD_RATE", source)
        self.assertIn("RA4M1_BOOTLOADER_MAGIC", source)
        self.assertIn("R_SYSTEM->VBTBKR", source)
        self.assertIn("R_USB_FS0->SYSCFG_b.DPRPU", source)
        self.assertIn("sys_reboot(SYS_REBOOT_COLD)", source)

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


class MonitorCommandTests(unittest.TestCase):
    def test_serial_open_check_script_is_valid_python(self) -> None:
        compile(seeed_zephyr.serial_port_open_check_script(), "<serial-open-check>", "exec")

    def test_monitor_waits_until_serial_port_is_openable(self) -> None:
        with mock.patch.object(seeed_zephyr, "require_board", return_value={"vendor": "nordic"}):
            with mock.patch.object(
                seeed_zephyr, "wait_for_serial_port_ready", return_value="/dev/cu.usbmodem1101"
            ) as wait_ready:
                with mock.patch.object(
                    seeed_zephyr,
                    "zephyr_venv_python",
                    return_value=seeed_zephyr.Path("/tmp/venv/bin/python"),
                ):
                    with mock.patch.object(seeed_zephyr, "run_command") as run_command:
                        seeed_zephyr.run_monitor("xiao_nrf52840", baud=115200)

        wait_ready.assert_called_once_with(None, 115200)
        run_command.assert_called_once_with(
            [
                "/tmp/venv/bin/python",
                str(seeed_zephyr.SERIAL_MONITOR_SCRIPT),
                "/dev/cu.usbmodem1101",
                "115200",
            ]
        )

    def test_serial_ready_check_retries_resource_busy_port(self) -> None:
        busy = seeed_zephyr.subprocess.CompletedProcess([], 1, "Resource busy")
        ready = seeed_zephyr.subprocess.CompletedProcess([], 0, "")

        with mock.patch.object(seeed_zephyr, "usb_serial_devices", return_value=["/dev/cu.usbmodem1101"]):
            with mock.patch.object(seeed_zephyr, "run_command_capture", side_effect=[busy, ready]):
                with mock.patch.object(
                    seeed_zephyr,
                    "zephyr_venv_python",
                    return_value=seeed_zephyr.Path("/tmp/venv/bin/python"),
                ):
                    with mock.patch.object(seeed_zephyr.time, "sleep"):
                        port = seeed_zephyr.wait_for_serial_port_ready(timeout_seconds=1)

        self.assertEqual(port, "/dev/cu.usbmodem1101")

    def test_uf2_flash_monitor_waits_for_bootloader_volume_to_detach(self) -> None:
        args = seeed_zephyr.argparse.Namespace(
            board_id="xiao_nrf52840", example=None, app=None, port=None, monitor=True, baud=115200
        )
        board = {"id": "xiao_nrf52840", "vendor": "nordic", "target": "xiao_ble"}

        with mock.patch.object(seeed_zephyr, "select_example", return_value={"path": "example"}):
            with mock.patch.object(seeed_zephyr, "require_flash_tools"):
                with mock.patch.object(seeed_zephyr, "run_west_build"):
                    with mock.patch.object(seeed_zephyr, "run_west_flash", return_value="/dev/cu.usbmodem1101"):
                        with mock.patch.object(seeed_zephyr, "require_board", return_value=board):
                            with mock.patch.object(seeed_zephyr, "wait_for_uf2_detach") as wait_detach:
                                with mock.patch.object(seeed_zephyr, "run_monitor") as run_monitor:
                                    seeed_zephyr.cmd_flash(args)

        wait_detach.assert_called_once_with()
        run_monitor.assert_called_once_with("xiao_nrf52840", port=None, baud=115200)

    def test_samd21_flash_monitor_redetects_serial_after_bossac(self) -> None:
        args = seeed_zephyr.argparse.Namespace(
            board_id="xiao_samd21",
            example=None,
            app=None,
            port="/dev/cu.usbmodem11301",
            monitor=True,
            baud=115200,
        )
        board = {"id": "xiao_samd21", "vendor": "microchip", "target": "seeeduino_xiao"}

        with mock.patch.object(seeed_zephyr, "select_example", return_value={"path": "example"}):
            with mock.patch.object(seeed_zephyr, "require_flash_tools"):
                with mock.patch.object(seeed_zephyr, "run_west_build"):
                    with mock.patch.object(
                        seeed_zephyr, "run_west_flash", return_value="/dev/cu.usbmodem11301"
                    ) as west_flash:
                        with mock.patch.object(seeed_zephyr, "require_board", return_value=board):
                            with mock.patch.object(seeed_zephyr, "run_monitor") as run_monitor:
                                seeed_zephyr.cmd_flash(args)

        west_flash.assert_called_once_with("xiao_samd21", port="/dev/cu.usbmodem11301")
        run_monitor.assert_called_once_with("xiao_samd21", port=None, baud=115200)

    def test_cmd_flash_uses_rom_boot_path_when_rom_bootloader_detected(self) -> None:
        args = seeed_zephyr.argparse.Namespace(
            board_id="xiao_ra4m1", example=None, app=None, port=None, monitor=False, baud=115200
        )

        with mock.patch.object(seeed_zephyr, "select_example", return_value={"path": "example"}):
            with mock.patch.object(seeed_zephyr, "ra4m1_rom_boot_port", return_value="/dev/cu.usbmodem1101"):
                with mock.patch.object(seeed_zephyr, "require_flash_tools") as req_tools:
                    with mock.patch.object(seeed_zephyr, "run_west_build") as build:
                        with mock.patch.object(seeed_zephyr, "run_ra4m1_rom_flash", return_value=None) as rom_flash:
                            with mock.patch.object(seeed_zephyr, "run_west_flash") as west_flash:
                                seeed_zephyr.cmd_flash(args)

        req_tools.assert_called_once_with("xiao_ra4m1", rom_boot=True)
        build.assert_called_once_with("xiao_ra4m1", {"path": "example"}, extra_overlay=None)
        rom_flash.assert_called_once_with("/dev/cu.usbmodem1101")
        west_flash.assert_not_called()

    def test_cmd_flash_rom_boot_with_monitor_waits_for_detach(self) -> None:
        args = seeed_zephyr.argparse.Namespace(
            board_id="xiao_ra4m1", example=None, app=None, port=None, monitor=True, baud=115200
        )

        with mock.patch.object(seeed_zephyr, "select_example", return_value={"path": "example"}):
            with mock.patch.object(seeed_zephyr, "ra4m1_rom_boot_port", return_value="/dev/cu.usbmodem1101"):
                with mock.patch.object(seeed_zephyr, "require_flash_tools"):
                    with mock.patch.object(seeed_zephyr, "run_west_build"):
                        with mock.patch.object(seeed_zephyr, "run_ra4m1_rom_flash", return_value=None):
                            with mock.patch.object(
                                seeed_zephyr, "wait_for_ra4m1_rom_boot_detach"
                            ) as wait_detach:
                                with mock.patch.object(seeed_zephyr, "run_monitor") as run_monitor:
                                    seeed_zephyr.cmd_flash(args)

        wait_detach.assert_called_once_with()
        run_monitor.assert_called_once_with("xiao_ra4m1", port=None, baud=115200)

    def test_cmd_flash_uses_dfu_path_when_no_rom_bootloader(self) -> None:
        args = seeed_zephyr.argparse.Namespace(
            board_id="xiao_ra4m1", example=None, app=None, port=None, monitor=False, baud=115200
        )

        with mock.patch.object(seeed_zephyr, "select_example", return_value={"path": "example"}):
            with mock.patch.object(seeed_zephyr, "ra4m1_rom_boot_port", return_value=None):
                with mock.patch.object(seeed_zephyr, "require_flash_tools") as req_tools:
                    with mock.patch.object(seeed_zephyr, "run_west_build") as build:
                        with mock.patch.object(seeed_zephyr, "run_west_flash", return_value=None) as west_flash:
                            with mock.patch.object(seeed_zephyr, "run_ra4m1_rom_flash") as rom_flash:
                                seeed_zephyr.cmd_flash(args)

        req_tools.assert_called_once_with("xiao_ra4m1", rom_boot=False)
        build.assert_called_once_with("xiao_ra4m1", {"path": "example"}, extra_overlay=None)
        west_flash.assert_called_once_with("xiao_ra4m1", port=None)
        rom_flash.assert_not_called()

    def test_wait_for_uf2_detach_returns_after_volume_disappears(self) -> None:
        with mock.patch.object(seeed_zephyr, "uf2_mounts", side_effect=[["/Volumes/XIAO-SENSE"], []]):
            with mock.patch.object(seeed_zephyr.time, "sleep"):
                seeed_zephyr.wait_for_uf2_detach(timeout_seconds=1)


class BuildCommandTests(unittest.TestCase):
    def test_raspberrypi_build_uses_bootmode_retention_snippet(self) -> None:
        example = {
            "path": str(seeed_zephyr._REPO_ROOT / "examples/boards/xiao_rp2040/blinky"),
            "zephyr_target": "xiao_rp2040",
        }

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
                str(seeed_zephyr._REPO_ROOT / "examples/boards/xiao_rp2040/blinky"),
            ]
        )

    def test_non_raspberrypi_build_does_not_use_bootmode_retention_snippet(self) -> None:
        example = {
            "path": str(seeed_zephyr._REPO_ROOT / "examples/boards/xiao_samd21/blinky"),
            "zephyr_target": "seeeduino_xiao",
        }

        with mock.patch.object(seeed_zephyr, "ensure_chip_blobs"):
            with mock.patch.object(seeed_zephyr, "run_west") as run_west:
                seeed_zephyr.run_west_build("xiao_samd21", example)

        command = run_west.call_args.args[0]
        self.assertNotIn("-S", command)
        self.assertNotIn("rp2-boot-mode-retention", command)


class ExampleConfigTests(unittest.TestCase):
    def test_rp2350_defaults_to_m33_target(self) -> None:
        board_file = seeed_zephyr._REPO_ROOT / "metadata/boards/xiao_rp2350.yaml"
        example_file = (
            seeed_zephyr._REPO_ROOT / "examples/boards/xiao_rp2350/blinky/example.yaml"
        )
        board = seeed_zephyr.read_flat_yaml(board_file)
        example = seeed_zephyr.read_flat_yaml(example_file)

        self.assertEqual(board["zephyr_target"], "xiao_rp2350/rp2350a/m33")
        self.assertEqual(example["zephyr_target"], "xiao_rp2350/rp2350a/m33")

    def test_rp2350_example_enables_usb_cdc_monitor_and_bootloader_request(self) -> None:
        example_dir = seeed_zephyr._REPO_ROOT / "examples/boards/xiao_rp2350/blinky"
        prj_conf = (example_dir / "prj.conf").read_text(encoding="utf-8")
        overlay = (example_dir / "app.overlay").read_text(encoding="utf-8")
        main_c = (example_dir / "src/main.c").read_text(encoding="utf-8")

        for symbol in (
            "CONFIG_USB_DEVICE_STACK_NEXT=y",
            "CONFIG_CDC_ACM_SERIAL_INITIALIZE_AT_BOOT=y",
            "CONFIG_UART_LINE_CTRL=y",
            "CONFIG_RETENTION_BOOT_MODE=y",
            "CONFIG_REBOOT=y",
        ):
            self.assertIn(symbol, prj_conf)

        self.assertIn("rp2350-boot-mode-retention.dtsi", overlay)
        self.assertIn("zephyr,console = &cdc_acm_uart0", overlay)
        self.assertIn("compatible = \"zephyr,cdc-acm-uart\"", overlay)
        self.assertIn("UART_LINE_CTRL_BAUD_RATE", main_c)
        self.assertIn("BOOT_MODE_TYPE_BOOTLOADER", main_c)
        self.assertIn("sys_reboot(SYS_REBOOT_COLD)", main_c)

    def test_nrf52840_example_enables_usb_cdc_monitor_and_bootloader_request(self) -> None:
        example_dir = seeed_zephyr._REPO_ROOT / "examples/boards/xiao_nrf52840/blinky"
        prj_conf = (example_dir / "prj.conf").read_text(encoding="utf-8")
        main_c = (example_dir / "src/main.c").read_text(encoding="utf-8")

        for symbol in (
            "CONFIG_REBOOT=y",
            "CONFIG_SERIAL=y",
            "CONFIG_CONSOLE=y",
            "CONFIG_UART_CONSOLE=y",
            "CONFIG_UART_LINE_CTRL=y",
            "CONFIG_BOOT_DELAY=500",
        ):
            self.assertIn(symbol, prj_conf)

        self.assertIn("DT_NODELABEL(board_cdc_acm_uart)", main_c)
        self.assertIn("UART_LINE_CTRL_BAUD_RATE", main_c)
        self.assertIn("NRF52_BOOTLOADER_MAGIC", main_c)
        self.assertIn("nrf_power_gpregret_set(NRF_POWER, 0, NRF52_BOOTLOADER_MAGIC)", main_c)
        self.assertIn("sys_reboot(SYS_REBOOT_COLD)", main_c)

    def test_ra4m1_example_starts_after_dfu_bootloader(self) -> None:
        example_dir = seeed_zephyr._REPO_ROOT / "examples/boards/xiao_ra4m1/blinky"
        prj_conf = (example_dir / "prj.conf").read_text(encoding="utf-8")

        self.assertIn("CONFIG_FLASH_LOAD_OFFSET=0x4000", prj_conf)

    def test_ra4m1_example_uses_usb_cdc_console(self) -> None:
        example_dir = seeed_zephyr._REPO_ROOT / "examples/boards/xiao_ra4m1/blinky"
        prj_conf = (example_dir / "prj.conf").read_text(encoding="utf-8")
        app_overlay = (example_dir / "app.overlay").read_text(encoding="utf-8")

        self.assertIn("CONFIG_USB_DEVICE_STACK_NEXT=y", prj_conf)
        self.assertIn("CONFIG_CDC_ACM_SERIAL_INITIALIZE_AT_BOOT=y", prj_conf)
        self.assertIn("CONFIG_CDC_ACM_SERIAL_VID=0x2886", prj_conf)
        self.assertIn("CONFIG_CDC_ACM_SERIAL_PID=0x0049", prj_conf)
        self.assertIn('zephyr,console = &cdc_acm_uart0;', app_overlay)
        self.assertIn('compatible = "zephyr,cdc-acm-uart";', app_overlay)


class MonitorInteractiveTests(unittest.TestCase):
    def test_cmd_monitor_with_board_id_calls_run_monitor(self) -> None:
        args = mock.MagicMock()
        args.board_id = "xiao_esp32c6"
        args.port = None
        args.baud = None
        board = {"id": "xiao_esp32c6", "vendor": "espressif", "target": "xiao_esp32c6/esp32c6/hpcore"}
        with mock.patch.object(seeed_zephyr, "require_board", return_value=board):
            with mock.patch.object(seeed_zephyr, "run_monitor") as m:
                seeed_zephyr.cmd_monitor(args)
        m.assert_called_once_with("xiao_esp32c6", port=None, baud=115200)

    def test_cmd_monitor_without_board_id_uses_interactive_port(self) -> None:
        args = mock.MagicMock()
        args.board_id = None
        args.port = None
        args.baud = None
        with mock.patch.object(
            seeed_zephyr, "interactive_select_port", return_value="/dev/cu.test"
        ) as sel_port:
            with mock.patch.object(
                seeed_zephyr, "interactive_select_baud", return_value=115200
            ) as sel_baud:
                with mock.patch.object(seeed_zephyr, "zephyr_venv_python", return_value="python3"):
                    with mock.patch.object(seeed_zephyr, "run_command") as run:
                        seeed_zephyr.cmd_monitor(args)
        sel_port.assert_called_once()
        sel_baud.assert_called_once()
        run.assert_called_once()
        cmd = run.call_args[0][0]
        self.assertIn("/dev/cu.test", cmd)
        self.assertIn("115200", cmd)

    def test_cmd_monitor_without_board_id_skips_interactive_when_port_and_baud_given(self) -> None:
        args = mock.MagicMock()
        args.board_id = None
        args.port = "/dev/cu.manual"
        args.baud = 9600
        with mock.patch.object(seeed_zephyr, "zephyr_venv_python", return_value="python3"):
            with mock.patch.object(seeed_zephyr, "run_command") as run:
                seeed_zephyr.cmd_monitor(args)
        cmd = run.call_args[0][0]
        self.assertIn("/dev/cu.manual", cmd)
        self.assertIn("9600", cmd)

    def test_interactive_select_port_single_device_auto_selects(self) -> None:
        with mock.patch.object(
            seeed_zephyr, "list_serial_ports_detailed",
            return_value=[("/dev/cu.usb1", "XIAO Board")],
        ):
            result = seeed_zephyr.interactive_select_port()
        self.assertEqual(result, "/dev/cu.usb1")

    def test_interactive_select_port_no_devices_raises(self) -> None:
        with mock.patch.object(
            seeed_zephyr, "list_serial_ports_detailed", return_value=[],
        ):
            with self.assertRaises(seeed_zephyr.CliError):
                seeed_zephyr.interactive_select_port()

    def test_interactive_select_port_multiple_devices_prompts(self) -> None:
        ports = [("/dev/cu.usb1", "Board A"), ("/dev/cu.usb2", "Board B")]
        with mock.patch.object(
            seeed_zephyr, "list_serial_ports_detailed", return_value=ports,
        ):
            with mock.patch("builtins.input", return_value="2"):
                result = seeed_zephyr.interactive_select_port()
        self.assertEqual(result, "/dev/cu.usb2")

    def test_interactive_select_port_enter_selects_first(self) -> None:
        ports = [("/dev/cu.usb1", "Board A"), ("/dev/cu.usb2", "Board B")]
        with mock.patch.object(
            seeed_zephyr, "list_serial_ports_detailed", return_value=ports,
        ):
            with mock.patch("builtins.input", return_value=""):
                result = seeed_zephyr.interactive_select_port()
        self.assertEqual(result, "/dev/cu.usb1")

    def test_interactive_select_baud_default(self) -> None:
        with mock.patch("builtins.input", return_value=""):
            result = seeed_zephyr.interactive_select_baud()
        self.assertEqual(result, 115200)

    def test_interactive_select_baud_custom(self) -> None:
        with mock.patch("builtins.input", return_value="9600"):
            result = seeed_zephyr.interactive_select_baud()
        self.assertEqual(result, 9600)


class ExampleSelectionTests(unittest.TestCase):
    def test_select_example_single_auto_selects(self) -> None:
        example = {"demo": "blinky", "validation_status": "hardware-tested", "path": "examples/boards/xiao_ra4m1/blinky"}
        with mock.patch.object(seeed_zephyr, "require_board"):
            with mock.patch.object(seeed_zephyr, "resolve_board_examples", return_value=[example]):
                result = seeed_zephyr.select_example("xiao_ra4m1")
        self.assertEqual(result["demo"], "blinky")

    def test_select_example_by_name(self) -> None:
        ex1 = {"demo": "blinky", "validation_status": "hardware-tested", "path": "a"}
        ex2 = {"demo": "hello_world", "validation_status": "build-only", "path": "b"}
        with mock.patch.object(seeed_zephyr, "require_board"):
            with mock.patch.object(seeed_zephyr, "resolve_board_examples", return_value=[ex1, ex2]):
                result = seeed_zephyr.select_example("xiao_esp32c6", "hello_world")
        self.assertEqual(result["demo"], "hello_world")


class CreateCommandTests(unittest.TestCase):
    def _make_args(self, **kwargs) -> mock.MagicMock:
        args = mock.MagicMock()
        args.from_asset = kwargs.get("from_asset", "xiao_rp2040/blinky")
        args.board_id = kwargs.get("board_id", "xiao_rp2040")
        args.output = kwargs["output"]
        args.force = kwargs.get("force", False)
        args.pins = kwargs.get("pins", None)
        args.blank = kwargs.get("blank", False)
        return args

    def test_create_copies_example_and_writes_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "proj"
            seeed_zephyr.cmd_create(self._make_args(output=str(out)))

            # rp2040 ships an app.overlay; the whole-directory copy must include it.
            self.assertTrue((out / "CMakeLists.txt").is_file())
            self.assertTrue((out / "prj.conf").is_file())
            self.assertTrue((out / "src" / "main.c").is_file())
            self.assertTrue((out / "app.overlay").is_file())

            snapshot = json.loads((out / "snapshot.json").read_text(encoding="utf-8"))
            self.assertEqual(snapshot["generator"], "seeed-zephyr")
            self.assertEqual(snapshot["source_asset"], "examples/boards/xiao_rp2040/blinky")
            self.assertEqual(snapshot["board"], "xiao_rp2040")
            self.assertEqual(snapshot["zephyr_version"], seeed_zephyr.ZEPHYR_BASELINE)
            self.assertEqual(snapshot["validation_status"], "hardware-tested")

    def test_create_rejects_board_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            args = self._make_args(board_id="xiao_esp32c6", output=str(Path(tmp) / "proj"))
            with self.assertRaises(seeed_zephyr.CliError) as ctx:
                seeed_zephyr.cmd_create(args)
            self.assertIn("xiao_rp2040", str(ctx.exception))

    def test_create_rejects_missing_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            args = self._make_args(from_asset="xiao_rp2040/nope", output=str(Path(tmp) / "proj"))
            with self.assertRaises(seeed_zephyr.CliError):
                seeed_zephyr.cmd_create(args)

    def test_create_rejects_unsupported_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            args = self._make_args(
                from_asset="xiao_esp32c5/hello_world",
                board_id="xiao_esp32c5",
                output=str(Path(tmp) / "proj"),
            )
            with self.assertRaises(seeed_zephyr.CliError) as ctx:
                seeed_zephyr.cmd_create(args)
            self.assertIn("unsupported", str(ctx.exception).lower())

    def test_create_refuses_nonempty_output_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "proj"
            out.mkdir()
            (out / "existing.txt").write_text("keep", encoding="utf-8")
            with self.assertRaises(seeed_zephyr.CliError):
                seeed_zephyr.cmd_create(self._make_args(output=str(out)))

    def test_create_overwrites_nonempty_output_with_force(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "proj"
            out.mkdir()
            (out / "existing.txt").write_text("keep", encoding="utf-8")
            seeed_zephyr.cmd_create(self._make_args(output=str(out), force=True))
            self.assertTrue((out / "snapshot.json").is_file())

    def test_create_accepts_from_asset_path_forms(self) -> None:
        forms = [
            "xiao_esp32c6/blinky",
            "boards/xiao_esp32c6/blinky",
            "examples/boards/xiao_esp32c6/blinky",
        ]
        for form in forms:
            with self.subTest(form=form):
                with tempfile.TemporaryDirectory() as tmp:
                    out = Path(tmp) / "proj"
                    args = self._make_args(
                        from_asset=form, board_id="xiao_esp32c6", output=str(out)
                    )
                    seeed_zephyr.cmd_create(args)
                    snapshot = json.loads((out / "snapshot.json").read_text(encoding="utf-8"))
                    self.assertEqual(
                        snapshot["source_asset"], "examples/boards/xiao_esp32c6/blinky"
                    )


class CreateBlankCommandTests(unittest.TestCase):
    def _blank_args(self, output: str, **kwargs) -> seeed_zephyr.argparse.Namespace:
        return seeed_zephyr.argparse.Namespace(
            from_asset=kwargs.get("from_asset", None),
            blank=kwargs.get("blank", True),
            board_id=kwargs.get("board_id", "xiao_esp32c6"),
            output=output,
            force=kwargs.get("force", False),
            pins=kwargs.get("pins", None),
        )

    def test_create_blank_writes_minimal_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "blank"
            seeed_zephyr.cmd_create(self._blank_args(str(out)))

            self.assertTrue((out / "CMakeLists.txt").is_file())
            self.assertTrue((out / "prj.conf").is_file())
            self.assertTrue((out / "src" / "main.c").is_file())

            cmake = (out / "CMakeLists.txt").read_text(encoding="utf-8")
            self.assertIn("project(blank)", cmake)
            self.assertIn("find_package(Zephyr", cmake)

            snapshot = json.loads((out / "snapshot.json").read_text(encoding="utf-8"))
            self.assertEqual(snapshot["source_asset"], "blank")
            self.assertEqual(snapshot["board"], "xiao_esp32c6")

    def test_create_blank_rejects_from_asset(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            args = self._blank_args(str(Path(tmp) / "blank"), from_asset="xiao_esp32c6/blinky")
            with self.assertRaises(seeed_zephyr.CliError) as ctx:
                seeed_zephyr.cmd_create(args)
            self.assertIn("--blank", str(ctx.exception))

    def test_create_without_source_or_blank_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            args = self._blank_args(str(Path(tmp) / "blank"), blank=False, from_asset=None)
            with self.assertRaises(seeed_zephyr.CliError) as ctx:
                seeed_zephyr.cmd_create(args)
            self.assertIn("--from", str(ctx.exception))


class SetPinsCommandTests(unittest.TestCase):
    def _create_grove_project(
        self,
        tmp: str,
        *,
        from_asset: str = "grove/grove_ultrasonic_distance_sensor/basic_read",
        board_id: str = "xiao_nrf52840",
        pins: list[str] | None = None,
    ) -> Path:
        out = Path(tmp) / "proj"
        create_args = seeed_zephyr.argparse.Namespace(
            from_asset=from_asset,
            board_id=board_id,
            output=str(out),
            force=False,
            pins=pins,
        )
        seeed_zephyr.cmd_create(create_args)
        return out

    def _set_pins_args(
        self, app: Path, *, board_id: str = "xiao_nrf52840", pins: list[str] | None = None
    ) -> seeed_zephyr.argparse.Namespace:
        return seeed_zephyr.argparse.Namespace(
            board_id=board_id,
            app=str(app),
            pins=pins,
            as_json=False,
        )

    def test_set_pins_writes_app_overlay_when_no_board_overlay(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            # nRF52840 (xiao_ble) ships no board overlay, so the pin lands in app.overlay.
            app = self._create_grove_project(tmp)
            seeed_zephyr.cmd_set_pins(self._set_pins_args(app, pins=["signal=D3"]))

            overlay = app / "app.overlay"
            self.assertTrue(overlay.is_file())
            self.assertIn("<&xiao_d 3 GPIO_ACTIVE_HIGH>", overlay.read_text(encoding="utf-8"))

            snapshot = json.loads((app / "snapshot.json").read_text(encoding="utf-8"))
            self.assertEqual(snapshot["board"], "xiao_nrf52840")
            self.assertEqual(snapshot["pins"], {"signal": "D3"})

    def test_set_pins_merges_into_board_overlay_and_keeps_console(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            # SAMD21 ships boards/seeeduino_xiao.overlay for the USB console; the pin must
            # merge into it without dropping the console, and re-baking must not duplicate.
            app = self._create_grove_project(tmp, board_id="xiao_samd21")
            seeed_zephyr.cmd_set_pins(
                self._set_pins_args(app, board_id="xiao_samd21", pins=["signal=D3"])
            )
            overlay = app / "boards" / "seeeduino_xiao.overlay"
            text = overlay.read_text(encoding="utf-8")
            self.assertIn("cdc_acm_uart0", text)
            self.assertIn("<&xiao_d 3 GPIO_ACTIVE_HIGH>", text)

            seeed_zephyr.cmd_set_pins(
                self._set_pins_args(app, board_id="xiao_samd21", pins=["signal=D5"])
            )
            text2 = overlay.read_text(encoding="utf-8")
            self.assertIn("cdc_acm_uart0", text2)
            self.assertIn("<&xiao_d 5 GPIO_ACTIVE_HIGH>", text2)
            self.assertNotIn("<&xiao_d 3 GPIO_ACTIVE_HIGH>", text2)
            self.assertEqual(text2.count("ultrasonic-gpios"), 1)

    def test_set_pins_rejects_reserved_pin(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            app = self._create_grove_project(tmp)
            with self.assertRaises(seeed_zephyr.CliError) as ctx:
                seeed_zephyr.cmd_set_pins(self._set_pins_args(app, pins=["signal=D7"]))

            message = str(ctx.exception)
            self.assertIn("reserved", message)
            self.assertIn("console-uart", message)

    def test_set_pins_rejects_fixed_bus_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            app = self._create_grove_project(
                tmp,
                from_asset="grove/grove_scd41_co2_temperature_humidity_sensor/basic_read",
                pins=None,
            )
            with self.assertRaises(seeed_zephyr.CliError) as ctx:
                seeed_zephyr.cmd_set_pins(self._set_pins_args(app, pins=["signal=D2"]))

            self.assertIn("pin_policy=fixed-bus", str(ctx.exception))


class UpdateCommandTests(unittest.TestCase):
    def test_update_repo_checkout_runs_git_pull_no_ff(self) -> None:
        repo = Path("/tmp/seeed-zephyr-base")
        result = seeed_zephyr.subprocess.CompletedProcess([], 0, "true\n")

        with mock.patch.object(seeed_zephyr, "require_path_command") as require:
            with mock.patch.object(seeed_zephyr, "run_command_capture", return_value=result) as capture:
                with mock.patch.object(seeed_zephyr, "run_command") as run:
                    seeed_zephyr.update_repo_checkout(repo)

        require.assert_called_once_with(
            "git", "Install Git, then rerun 'seeed-zephyr update'."
        )
        capture.assert_called_once_with(
            ["git", "-C", str(repo), "rev-parse", "--is-inside-work-tree"]
        )
        run.assert_called_once_with(["git", "-C", str(repo), "pull", "--no-ff"])

    def test_update_repo_checkout_rejects_non_git_dir(self) -> None:
        repo = Path("/tmp/seeed-zephyr-base")
        result = seeed_zephyr.subprocess.CompletedProcess([], 128, "false\n")

        with mock.patch.object(seeed_zephyr, "require_path_command"):
            with mock.patch.object(seeed_zephyr, "run_command_capture", return_value=result):
                with self.assertRaises(seeed_zephyr.CliError) as ctx:
                    seeed_zephyr.update_repo_checkout(repo)

        self.assertIn("not a Git checkout", str(ctx.exception))

    def test_checkout_repo_version_requires_clean_tree(self) -> None:
        repo = Path("/tmp/seeed-zephyr-base")

        with mock.patch.object(seeed_zephyr, "require_path_command"):
            with mock.patch.object(seeed_zephyr, "repo_is_clean", return_value=False):
                with self.assertRaises(seeed_zephyr.CliError) as ctx:
                    seeed_zephyr.checkout_repo_version(repo, "0.2.0")

        self.assertIn("local changes", str(ctx.exception))

    def test_checkout_repo_version_accepts_matching_ref(self) -> None:
        repo = Path("/tmp/seeed-zephyr-base")
        missing = seeed_zephyr.subprocess.CompletedProcess([], 1, "")
        found = seeed_zephyr.subprocess.CompletedProcess([], 0, "abc123\n")

        with mock.patch.object(seeed_zephyr, "require_path_command"):
            with mock.patch.object(seeed_zephyr, "repo_is_clean", return_value=True):
                with mock.patch.object(
                    seeed_zephyr, "run_command_capture", side_effect=[missing, found]
                ) as capture:
                    with mock.patch.object(seeed_zephyr, "run_command") as run:
                        seeed_zephyr.checkout_repo_version(repo, "0.2.0")

        run.assert_any_call(["git", "-C", str(repo), "fetch", "--tags", "--force"])
        run.assert_any_call(["git", "-C", str(repo), "checkout", "v0.2.0"])
        self.assertEqual(capture.call_count, 2)

    def test_installed_package_update_prefers_homebrew(self) -> None:
        with mock.patch.object(seeed_zephyr, "is_homebrew_install", return_value=True):
            with mock.patch.object(seeed_zephyr, "is_pipx_install", return_value=True):
                with mock.patch.object(seeed_zephyr.shutil, "which", return_value="/opt/homebrew/bin/brew"):
                    source, commands = seeed_zephyr.installed_package_update_commands()

        self.assertEqual(source, "Homebrew")
        self.assertEqual(commands, [["brew", "update"], ["brew", "upgrade", "seeed-zephyr"]])

    def test_installed_package_update_uses_pipx_when_detected(self) -> None:
        def fake_which(command: str) -> str | None:
            return "/Users/test/.local/bin/pipx" if command == "pipx" else None

        with mock.patch.object(seeed_zephyr, "is_homebrew_install", return_value=False):
            with mock.patch.object(seeed_zephyr, "is_pipx_install", return_value=True):
                with mock.patch.object(seeed_zephyr.shutil, "which", side_effect=fake_which):
                    source, commands = seeed_zephyr.installed_package_update_commands()

        self.assertEqual(source, "pipx")
        self.assertEqual(commands, [["pipx", "upgrade", "seeed-zephyr"]])

    def test_installed_package_update_uses_pipx_for_specific_version(self) -> None:
        with mock.patch.object(seeed_zephyr, "is_homebrew_install", return_value=False):
            with mock.patch.object(seeed_zephyr, "is_pipx_install", return_value=True):
                with mock.patch.object(seeed_zephyr.shutil, "which", return_value="/usr/bin/pipx"):
                    source, commands = seeed_zephyr.installed_package_update_commands("0.2.0")

        self.assertEqual(source, "pipx")
        self.assertEqual(commands, [["pipx", "install", "--force", "seeed-zephyr==0.2.0"]])

    def test_homebrew_specific_version_raises(self) -> None:
        with mock.patch.object(seeed_zephyr, "is_homebrew_install", return_value=True):
            with self.assertRaises(seeed_zephyr.CliError) as ctx:
                seeed_zephyr.installed_package_update_commands("0.2.0")

        self.assertIn("Homebrew-managed", str(ctx.exception))

    def test_installed_package_update_falls_back_to_pip(self) -> None:
        with mock.patch.object(seeed_zephyr, "is_homebrew_install", return_value=False):
            with mock.patch.object(seeed_zephyr, "is_pipx_install", return_value=False):
                source, commands = seeed_zephyr.installed_package_update_commands()

        self.assertEqual(source, "pip")
        self.assertEqual(
            commands,
            [[seeed_zephyr.sys.executable, "-m", "pip", "install", "--upgrade", "seeed-zephyr"]],
        )

    def test_installed_package_update_falls_back_to_pip_specific_version(self) -> None:
        with mock.patch.object(seeed_zephyr, "is_homebrew_install", return_value=False):
            with mock.patch.object(seeed_zephyr, "is_pipx_install", return_value=False):
                source, commands = seeed_zephyr.installed_package_update_commands("0.2.0")

        self.assertEqual(source, "pip")
        self.assertEqual(
            commands,
            [
                [
                    seeed_zephyr.sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--upgrade",
                    "seeed-zephyr==0.2.0",
                ]
            ],
        )

    def test_cmd_update_uses_repo_root_when_available(self) -> None:
        repo = Path("/tmp/seeed-zephyr-base")
        args = mock.MagicMock()
        args.version = None
        with mock.patch.object(seeed_zephyr, "_REPO_ROOT", repo):
            with mock.patch.object(seeed_zephyr, "update_repo_checkout") as update_repo:
                with mock.patch.object(seeed_zephyr, "update_installed_package") as update_package:
                    seeed_zephyr.cmd_update(args)

        update_repo.assert_called_once_with(repo)
        update_package.assert_not_called()

    def test_cmd_update_uses_repo_version_when_requested(self) -> None:
        repo = Path("/tmp/seeed-zephyr-base")
        args = mock.MagicMock()
        args.version = "0.2.0"
        with mock.patch.object(seeed_zephyr, "_REPO_ROOT", repo):
            with mock.patch.object(seeed_zephyr, "checkout_repo_version") as checkout:
                seeed_zephyr.cmd_update(args)

        checkout.assert_called_once_with(repo, "0.2.0")

    def test_cmd_update_uses_package_update_without_repo_root(self) -> None:
        args = mock.MagicMock()
        args.version = None
        with mock.patch.object(seeed_zephyr, "_REPO_ROOT", None):
            with mock.patch.object(seeed_zephyr, "update_repo_checkout") as update_repo:
                with mock.patch.object(seeed_zephyr, "update_installed_package") as update_package:
                    seeed_zephyr.cmd_update(args)

        update_repo.assert_not_called()
        update_package.assert_called_once_with(None)


class InfoCommandTests(unittest.TestCase):
    def test_current_info_contains_traceability_fields(self) -> None:
        with mock.patch.object(seeed_zephyr, "cli_version", return_value="0.3.0"):
            with mock.patch.object(seeed_zephyr, "package_source", return_value="pip"):
                with mock.patch.object(seeed_zephyr, "_REPO_ROOT", None):
                    with mock.patch.object(seeed_zephyr, "package_build_commit", return_value="abc123"):
                        data = seeed_zephyr.current_info()

        self.assertEqual(data["cli_version"], "0.3.0")
        self.assertEqual(data["install_mode"], "package")
        self.assertEqual(data["package_source"], "pip")
        self.assertEqual(data["data_source"], "bundled")
        self.assertEqual(data["git_commit"], "abc123")
        self.assertEqual(data["zephyr_baseline"], seeed_zephyr.ZEPHYR_BASELINE)

    def test_cmd_info_json_outputs_machine_readable_data(self) -> None:
        args = mock.MagicMock()
        args.as_json = True
        payload = {"cli_version": "0.3.0", "install_mode": "package"}
        buffer = io.StringIO()

        with mock.patch.object(seeed_zephyr, "current_info", return_value=payload):
            with contextlib.redirect_stdout(buffer):
                seeed_zephyr.cmd_info(args)

        self.assertEqual(json.loads(buffer.getvalue()), payload)


class JsonOutputTests(unittest.TestCase):
    def _run_json(self, func, **args) -> object:
        ns = mock.MagicMock()
        ns.as_json = True
        for key, value in args.items():
            setattr(ns, key, value)
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            func(ns)
        return json.loads(buffer.getvalue())

    def test_list_boards_json_has_all_boards(self) -> None:
        data = self._run_json(seeed_zephyr.cmd_list_boards)
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 11)
        for item in data:
            self.assertIn("id", item)
            self.assertIn("status", item)
            self.assertIn("target", item)

    def test_list_examples_json_rows(self) -> None:
        data = self._run_json(seeed_zephyr.cmd_list_examples)
        self.assertIsInstance(data, list)
        self.assertTrue(all("board_id" in row for row in data))

    def test_show_example_json_merges_metadata_and_files(self) -> None:
        data = self._run_json(
            seeed_zephyr.cmd_show_example, board_id="xiao_esp32c6", demo="blinky"
        )
        self.assertEqual(data["board_id"], "xiao_esp32c6")
        self.assertEqual(data["demo"], "blinky")
        self.assertIn("example.yaml", data["files"])

    def test_show_board_json_includes_examples(self) -> None:
        data = self._run_json(seeed_zephyr.cmd_show_board, board_id="xiao_esp32c6")
        self.assertEqual(data["id"], "xiao_esp32c6")
        self.assertGreaterEqual(len(data["examples"]), 1)

    def test_list_grove_json(self) -> None:
        data = self._run_json(seeed_zephyr.cmd_list_grove)
        ids = {module["id"] for module in data}
        self.assertEqual(
            ids,
            {
                "grove_ultrasonic_distance_sensor",
                "grove_soil_moisture_sensor",
                "grove_temperature_humidity_sensor_v2_dht20",
                "grove_scd41_co2_temperature_humidity_sensor",
                "lcd_1_47inch_display_module",
            },
        )
        skus = {module["id"]: module["sku"] for module in data}
        self.assertEqual(skus["grove_scd41_co2_temperature_humidity_sensor"], "101020952")
        self.assertEqual(skus["lcd_1_47inch_display_module"], "104990803")
        self.assertTrue(all("interface" in module for module in data))

    def test_list_expansion_json(self) -> None:
        data = self._run_json(seeed_zephyr.cmd_list_expansion)
        self.assertGreaterEqual(len(data), 3)
        self.assertTrue(all("id" in board for board in data))

    def test_list_ports_json(self) -> None:
        with mock.patch.object(
            seeed_zephyr,
            "list_serial_ports_detailed",
            return_value=[("/dev/cu.usb1", "Board A"), ("/dev/cu.usb2", "Board B")],
        ):
            data = self._run_json(seeed_zephyr.cmd_list_ports)
        self.assertEqual(
            data,
            [
                {"device": "/dev/cu.usb1", "description": "Board A"},
                {"device": "/dev/cu.usb2", "description": "Board B"},
            ],
        )

    def test_select_example_unknown_name_raises(self) -> None:
        ex1 = {"demo": "blinky", "validation_status": "hardware-tested", "path": "a"}
        with mock.patch.object(seeed_zephyr, "require_board"):
            with mock.patch.object(seeed_zephyr, "resolve_board_examples", return_value=[ex1]):
                with self.assertRaises(seeed_zephyr.CliError) as ctx:
                    seeed_zephyr.select_example("xiao_esp32c6", "nonexistent")
        self.assertIn("nonexistent", str(ctx.exception))

    def test_select_example_skips_unsupported(self) -> None:
        ex1 = {"demo": "hello_world", "validation_status": "unsupported", "path": "a"}
        ex2 = {"demo": "blinky", "validation_status": "build-only", "path": "b"}
        with mock.patch.object(seeed_zephyr, "require_board"):
            with mock.patch.object(seeed_zephyr, "resolve_board_examples", return_value=[ex1, ex2]):
                result = seeed_zephyr.select_example("test_board")
        self.assertEqual(result["demo"], "blinky")

    def test_select_example_multiple_prompts(self) -> None:
        ex1 = {"demo": "blinky", "validation_status": "build-only", "path": "a"}
        ex2 = {"demo": "hello_world", "validation_status": "build-only", "path": "b"}
        with mock.patch.object(seeed_zephyr, "require_board"):
            with mock.patch.object(seeed_zephyr, "resolve_board_examples", return_value=[ex1, ex2]):
                with mock.patch("builtins.input", return_value="2"):
                    result = seeed_zephyr.select_example("test_board")
        self.assertEqual(result["demo"], "hello_world")

    def test_select_example_no_examples_raises(self) -> None:
        with mock.patch.object(seeed_zephyr, "require_board"):
            with mock.patch.object(seeed_zephyr, "resolve_board_examples", return_value=[]):
                with self.assertRaises(seeed_zephyr.CliError):
                    seeed_zephyr.select_example("test_board")

    def test_resolve_app_example_valid_dir(self) -> None:
        board = {"id": "xiao_esp32c6", "vendor": "espressif", "target": "xiao_esp32c6/esp32c6/hpcore"}
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "CMakeLists.txt").write_text("cmake_minimum_required(VERSION 3.20)")
            (Path(tmpdir) / "prj.conf").write_text("CONFIG_PRINTK=y")
            with mock.patch.object(seeed_zephyr, "require_board", return_value=board):
                result = seeed_zephyr.resolve_app_example("xiao_esp32c6", tmpdir)
        self.assertEqual(result["zephyr_target"], "xiao_esp32c6/esp32c6/hpcore")
        self.assertTrue(Path(result["path"]).is_absolute())

    def test_resolve_app_example_missing_cmakelists_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "prj.conf").write_text("CONFIG_PRINTK=y")
            with self.assertRaises(seeed_zephyr.CliError) as ctx:
                seeed_zephyr.resolve_app_example("xiao_esp32c6", tmpdir)
        self.assertIn("CMakeLists.txt", str(ctx.exception))

    def test_resolve_app_example_missing_dir_raises(self) -> None:
        with self.assertRaises(seeed_zephyr.CliError):
            seeed_zephyr.resolve_app_example("xiao_esp32c6", "/nonexistent/path")

    def test_cmd_build_with_app_uses_external_path(self) -> None:
        args = mock.MagicMock()
        args.board_id = "xiao_esp32c6"
        args.example = None
        args.app = "/tmp/my_app"
        ext_example = {"path": "/tmp/my_app", "demo": "my_app", "zephyr_target": "t"}
        with mock.patch.object(seeed_zephyr, "resolve_app_example", return_value=ext_example) as resolve:
            with mock.patch.object(seeed_zephyr, "run_west_build") as build:
                seeed_zephyr.cmd_build(args)
        resolve.assert_called_once_with("xiao_esp32c6", "/tmp/my_app")
        build.assert_called_once_with("xiao_esp32c6", ext_example, extra_overlay=None)


if __name__ == "__main__":
    unittest.main()
