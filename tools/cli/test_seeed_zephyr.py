#!/usr/bin/env python3

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
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

    def test_xiao_mg24_flash_requires_debug_mate_openocd_package(self) -> None:
        board = {"id": "xiao_mg24", "vendor": "silabs", "target": "xiao_mg24"}

        with mock.patch.object(seeed_zephyr, "require_board", return_value=board):
            with mock.patch.object(seeed_zephyr, "resolve_mg24_openocd_tools", return_value=None):
                with self.assertRaises(seeed_zephyr.CliError) as context:
                    seeed_zephyr.run_west_flash("xiao_mg24")

        message = str(context.exception)
        self.assertIn("Seeed Debug Mate OpenOCD package", message)
        self.assertIn("SEEED_ZEPHYR_MG24_OPENOCD", message)
        self.assertIn("XIAO_MG24_Mac_Linux_OpenOCD-v0.12.0", message)

    def test_xiao_mg24_flash_uses_debug_mate_openocd_package(self) -> None:
        board = {"id": "xiao_mg24", "vendor": "silabs", "target": "xiao_mg24"}
        openocd = Path("/tmp/XIAO_MG24_Mac_Linux_OpenOCD-v0.12.0/bin/openocd")
        scripts = Path("/tmp/XIAO_MG24_Mac_Linux_OpenOCD-v0.12.0/scripts")

        with mock.patch.object(seeed_zephyr, "require_board", return_value=board):
            with mock.patch.object(
                seeed_zephyr, "require_mg24_openocd_tools", return_value=(openocd, scripts)
            ):
                with mock.patch.object(seeed_zephyr, "run_west") as run_west:
                    selected_port = seeed_zephyr.run_west_flash("xiao_mg24")

        self.assertIsNone(selected_port)
        run_west.assert_called_once_with(
            [
                "flash",
                "--runner",
                "openocd",
                "--openocd",
                str(openocd),
                "--openocd-search",
                str(scripts),
            ]
        )

    def test_xiao_mg24_detects_debug_mate_openocd_package_layout(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "XIAO_MG24_Mac_Linux_OpenOCD-v0.12.0"
            openocd = root / "bin" / "openocd"
            target_cfg = root / "scripts" / "target" / "efm32s2_g23.cfg"
            interface_cfg = root / "scripts" / "interface" / "cmsis-dap.cfg"
            target_cfg.parent.mkdir(parents=True)
            interface_cfg.parent.mkdir(parents=True)
            openocd.parent.mkdir(parents=True)
            openocd.write_text("", encoding="utf-8")
            openocd.chmod(0o755)
            target_cfg.write_text("", encoding="utf-8")
            interface_cfg.write_text("", encoding="utf-8")

            tools = seeed_zephyr.find_mg24_openocd_tools(root)

        self.assertEqual(tools, (openocd, root / "scripts"))

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
            board_id="xiao_nrf52840", port=None, monitor=True, baud=115200
        )
        board = {"id": "xiao_nrf52840", "vendor": "nordic", "target": "xiao_ble"}

        with mock.patch.object(seeed_zephyr, "require_supported_example", return_value={"path": "example"}):
            with mock.patch.object(seeed_zephyr, "require_flash_tools"):
                with mock.patch.object(seeed_zephyr, "run_west_build"):
                    with mock.patch.object(seeed_zephyr, "run_west_flash", return_value="/dev/cu.usbmodem1101"):
                        with mock.patch.object(seeed_zephyr, "require_board", return_value=board):
                            with mock.patch.object(seeed_zephyr, "wait_for_uf2_detach") as wait_detach:
                                with mock.patch.object(seeed_zephyr, "run_monitor") as run_monitor:
                                    seeed_zephyr.cmd_flash(args)

        wait_detach.assert_called_once_with()
        run_monitor.assert_called_once_with("xiao_nrf52840", port=None, baud=115200)

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


if __name__ == "__main__":
    unittest.main()
