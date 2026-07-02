#!/usr/bin/env python3
#
# Purpose:
#   Seed each board's pin_map (Dn -> chip pin) as a PROVISIONAL baseline derived from the
#   upstream Zephyr seeed_xiao_connector.dtsi gpio-map. pin_map_source points at that dtsi.
#
#   This is a transitional baseline: the long-term goal is to verify every chip_pin against
#   the official Seeed schematic and replace pin_map_source with the Wiki/schematic URL, so
#   that validate.py's pinmap audit compares an independent source against the upstream dtsi.
#
# Usage:
#   python3 tools/pin_map/seed_from_dtsi.py [--zephyr-workspace ~/zephyrproject]
#
# chip_pin format: the raw dtsi reference as "<controller>.<pin>" (e.g. gpio0.2, porta.2,
# ioport0.14, gpioc.0), faithful to the upstream dtsi with no vendor-name translation.

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BOARD_DIR = REPO_ROOT / "metadata" / "boards"
GPIO_MAP_RE = re.compile(r"<\s*(\d+)\s+0\s+&(\w+)\s+(\d+)\s+0\s*>")
PIN_MAP_HEADER_RE = re.compile(r"^#?\s*pin_map:\s*$", re.MULTILINE)
PIN_MAP_SOURCE_RE = re.compile(r"^pin_map_source:.*$\n?", re.MULTILINE)


def find_connector_dtsi(workspace: Path, zephyr_target: str) -> Path | None:
    first_seg = zephyr_target.split("/", 1)[0]
    candidate = workspace / "zephyr" / "boards" / "seeed" / first_seg / "seeed_xiao_connector.dtsi"
    if candidate.is_file():
        return candidate
    hits = list((workspace / "zephyr" / "boards").glob(f"*/{first_seg}/seeed_xiao_connector.dtsi"))
    return hits[0] if hits else None


def parse_gpio_map(dtsi: Path) -> dict[int, str]:
    text = dtsi.read_text(encoding="utf-8")
    mapping: dict[int, str] = {}
    for match in GPIO_MAP_RE.finditer(text):
        index, controller, pin = int(match.group(1)), match.group(2), match.group(3)
        mapping[index] = f"{controller}.{pin}"
    return mapping


def strip_existing_pin_map(text: str) -> str:
    # Remove a prior pin_map: block (the key plus its following indented lines) and any
    # pin_map_source line, so the script is idempotent.
    # 移除既有 pin_map: 块(键及其后续缩进行)与 pin_map_source 行,保证脚本可重复运行。
    lines = text.splitlines()
    out: list[str] = []
    skipping = False
    for line in lines:
        if re.match(r"^pin_map:\s*$", line):
            skipping = True
            continue
        if skipping:
            if line.startswith(" ") or line.startswith("\t") or line.strip() == "":
                # keep trailing blank line handling: stop skipping on a non-indented non-empty line
                if line.strip() == "":
                    continue
                continue
            skipping = False
        if re.match(r"^pin_map_source:.*$", line):
            continue
        out.append(line)
    return "\n".join(out).rstrip() + "\n"


def build_pin_map_block(mapping: dict[int, str], source_rel: str) -> str:
    lines = [
        "# Provisional baseline derived from the upstream Zephyr connector dtsi.",
        "# Replace with official Seeed schematic values and update pin_map_source to the Wiki URL.",
        "# 过渡基线,派生自上游 Zephyr connector dtsi。",
        "# 请以 Seeed 官方原理图为准替换,并将 pin_map_source 更新为 Wiki 链接。",
        f"pin_map_source: {source_rel}",
        "pin_map:",
    ]
    for index in sorted(mapping):
        lines.append(f"  - pin: D{index}")
        lines.append(f"    chip_pin: {mapping[index]}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed board pin_map from upstream connector dtsi.")
    parser.add_argument("--zephyr-workspace", default=os.path.expanduser("~/zephyrproject"))
    args = parser.parse_args()
    workspace = Path(args.zephyr_workspace)

    updated = 0
    for board_file in sorted(BOARD_DIR.glob("*.yaml")):
        text = board_file.read_text(encoding="utf-8")
        target_match = re.search(r"^zephyr_target:\s*(\S+)", text, re.MULTILINE)
        if not target_match:
            print(f"skip {board_file.name}: no zephyr_target", file=sys.stderr)
            continue
        zephyr_target = target_match.group(1)
        dtsi = find_connector_dtsi(workspace, zephyr_target)
        if not dtsi:
            print(f"skip {board_file.name}: no connector dtsi for {zephyr_target}", file=sys.stderr)
            continue
        mapping = parse_gpio_map(dtsi)
        if not mapping:
            print(f"skip {board_file.name}: no gpio-map entries in {dtsi}", file=sys.stderr)
            continue
        try:
            source_rel = str(dtsi.relative_to(workspace))
        except ValueError:
            source_rel = str(dtsi)
        cleaned = strip_existing_pin_map(text)
        block = build_pin_map_block(mapping, source_rel)
        board_file.write_text(cleaned.rstrip() + "\n\n" + block, encoding="utf-8")
        print(f"seeded {board_file.name}: {len(mapping)} pins <- {source_rel}")
        updated += 1
    print(f"\nDone. Updated {updated} board files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
