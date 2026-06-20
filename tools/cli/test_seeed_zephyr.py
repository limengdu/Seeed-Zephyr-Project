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
                with mock.patch.object(seeed_zephyr, "run_west", side_effect=west_error):
                    with self.assertRaises(seeed_zephyr.CliError) as context:
                        seeed_zephyr.run_west_flash(board_id)

                message = str(context.exception)
                self.assertIn("Command failed with status 1: west flash", message)
                self.assertIn("BOOTSEL", message)
                self.assertIn("UF2 mass storage", message)


if __name__ == "__main__":
    unittest.main()
