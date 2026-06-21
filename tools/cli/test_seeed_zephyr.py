#!/usr/bin/env python3

from __future__ import annotations

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
            seeed_zephyr.REPO_ROOT
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
                "-m",
                "serial.tools.miniterm",
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
        build.assert_called_once_with("xiao_ra4m1", {"path": "example"})
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
        build.assert_called_once_with("xiao_ra4m1", {"path": "example"})
        west_flash.assert_called_once_with("xiao_ra4m1", port=None)
        rom_flash.assert_not_called()

    def test_wait_for_uf2_detach_returns_after_volume_disappears(self) -> None:
        with mock.patch.object(seeed_zephyr, "uf2_mounts", side_effect=[["/Volumes/XIAO-SENSE"], []]):
            with mock.patch.object(seeed_zephyr.time, "sleep"):
                seeed_zephyr.wait_for_uf2_detach(timeout_seconds=1)


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


class ExampleConfigTests(unittest.TestCase):
    def test_rp2350_defaults_to_m33_target(self) -> None:
        board_file = seeed_zephyr.REPO_ROOT / "metadata/boards/xiao_rp2350.yaml"
        example_file = (
            seeed_zephyr.REPO_ROOT / "examples/boards/xiao_rp2350/blinky/example.yaml"
        )
        board = seeed_zephyr.read_flat_yaml(board_file)
        example = seeed_zephyr.read_flat_yaml(example_file)

        self.assertEqual(board["zephyr_target"], "xiao_rp2350/rp2350a/m33")
        self.assertEqual(example["zephyr_target"], "xiao_rp2350/rp2350a/m33")

    def test_rp2350_example_enables_usb_cdc_monitor_and_bootloader_request(self) -> None:
        example_dir = seeed_zephyr.REPO_ROOT / "examples/boards/xiao_rp2350/blinky"
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
        example_dir = seeed_zephyr.REPO_ROOT / "examples/boards/xiao_nrf52840/blinky"
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
        example_dir = seeed_zephyr.REPO_ROOT / "examples/boards/xiao_ra4m1/blinky"
        prj_conf = (example_dir / "prj.conf").read_text(encoding="utf-8")

        self.assertIn("CONFIG_FLASH_LOAD_OFFSET=0x4000", prj_conf)

    def test_ra4m1_example_uses_usb_cdc_console(self) -> None:
        example_dir = seeed_zephyr.REPO_ROOT / "examples/boards/xiao_ra4m1/blinky"
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
        build.assert_called_once_with("xiao_esp32c6", ext_example)


if __name__ == "__main__":
    unittest.main()
