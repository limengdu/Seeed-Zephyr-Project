#!/usr/bin/env python3
#
# Purpose:
#   Build the Grove example x board matrix: for each Grove example, build it on every
#   supported XIAO board and record per-board status into metadata/status/<example_id>.yaml.
#
# Usage:
#   python3 tools/build_matrix/run_grove.py [--example grove/<module>/<demo>] [--board <id> ...]
#                                          [--zephyr-workspace ~/zephyrproject] [--no-build]
#
# --no-build emits the matrix skeleton from metadata only (statuses: pending / excluded),
# useful for seeding a new example before a full CI run. Without --no-build, selected
# boards are built for real and recorded as build-verified / build-failed.
#
# Env:
#   ZEPHYR_WORKSPACE defaults to ~/zephyrproject (forwarded to the CLI for west builds).

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CLI = REPO_ROOT / "tools" / "cli" / "seeed_zephyr.py"
STATUS_DIR = REPO_ROOT / "metadata" / "status"

# Status values written into metadata/status/*.yaml.
# 写入 metadata/status/*.yaml 的状态取值。
STATUS_BUILD_VERIFIED = "build-verified"
STATUS_BUILD_FAILED = "build-failed"
STATUS_HARDWARE_TESTED = "hardware-tested"
STATUS_PENDING = "pending"
STATUS_EXCLUDED = "excluded"


def run_cli(args: list[str], workspace: Path) -> tuple[int, str]:
    env = dict(os.environ)
    env["ZEPHYR_WORKSPACE"] = str(workspace)
    proc = subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
    )
    return proc.returncode, (proc.stdout + proc.stderr)


def list_grove_examples() -> list[dict[str, object]]:
    code, out = run_cli(["list", "grove", "--json"], Path(os.environ.get("ZEPHYR_WORKSPACE", "")))
    if code != 0:
        print(out, file=sys.stderr)
        return []
    rows = json.loads(out)
    examples: list[dict[str, object]] = []
    for row in rows:
        module_id = str(row.get("id", ""))
        for ex in row.get("examples", []) or []:
            examples.append({"module_id": module_id, "demo": ex.get("demo")})
    return examples


def show_example(module_id: str, demo: str) -> dict[str, object] | None:
    code, out = run_cli(
        ["show", "example", f"grove/{module_id}/{demo}", "--json"],
        Path(os.environ.get("ZEPHYR_WORKSPACE", "")),
    )
    if code != 0:
        print(out, file=sys.stderr)
        return None
    return json.loads(out)


def _yaml_scalar(value: str) -> str:
    # Double-quoted YAML scalar: safely encodes newlines, quotes, and colons that
    # would otherwise corrupt the flat "key: value" emitter below.
    # 双引号 YAML 标量：安全编码换行、引号与冒号，避免破坏下面的扁平 "key: value" 输出。
    escaped = value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{escaped}"'


def emit_yaml(payload: dict[str, object]) -> str:
    # Tiny fixed-schema YAML emitter (no third-party dependency).
    # 极简固定 schema YAML 输出器(无第三方依赖)。
    lines: list[str] = []
    for key in ("example_id", "example_ref", "zephyr_version", "generated_on"):
        lines.append(f"{key}: {payload[key]}")
    lines.append("boards:")
    for board in payload["boards"]:
        lines.append(f"  - board_id: {board['board_id']}")
        lines.append(f"    status: {board['status']}")
        if board.get("target"):
            lines.append(f"    target: {board['target']}")
        if board.get("reason"):
            lines.append(f"    reason: {_yaml_scalar(str(board['reason']))}")
        if board.get("evidence"):
            lines.append(f"    evidence: {_yaml_scalar(str(board['evidence']))}")
    return "\n".join(lines) + "\n"


def build_example_matrix(
    example: dict[str, object],
    detail: dict[str, object],
    board_filter: list[str] | None,
    workspace: Path,
    no_build: bool,
    zephyr_version: str,
) -> dict[str, object]:
    module_id = str(example["module_id"])
    demo = str(example["demo"])
    example_ref = f"grove/{module_id}/{demo}"
    excluded = set(detail.get("excluded_boards", []) or [])
    board_rows: list[dict[str, object]] = []
    for entry in detail.get("board_matrix", []) or []:
        board_id = str(entry["board_id"])
        supported = bool(entry.get("supported"))
        if not supported or board_id in excluded:
            board_rows.append(
                {"board_id": board_id, "status": STATUS_EXCLUDED, "reason": "listed in excluded_boards"}
            )
            continue
        # Boards outside the --board filter (and the --no-build case) stay pending so the
        # full matrix is always written; only filtered boards are built for real.
        # --board 过滤之外的板子(以及 --no-build 情形)保持 pending,使完整矩阵始终写入;
        # 仅过滤内的板子真正构建。
        if no_build or (board_filter and board_id not in board_filter):
            board_rows.append({"board_id": board_id, "status": STATUS_PENDING})
            continue
        print(f"Building {example_ref} on {board_id}...", flush=True)
        code, out = run_cli(["build", board_id, example_ref], workspace)
        if code == 0:
            board_rows.append(
                {
                    "board_id": board_id,
                    "status": STATUS_BUILD_VERIFIED,
                    "evidence": f"seeed-zephyr build (local, {dt.date.today().isoformat()})",
                }
            )
        else:
            tail = "\n".join(out.splitlines()[-3:])
            board_rows.append(
                {
                    "board_id": board_id,
                    "status": STATUS_BUILD_FAILED,
                    "evidence": tail,
                }
            )
    return {
        "example_id": detail.get("id"),
        "example_ref": example_ref,
        "zephyr_version": zephyr_version,
        "generated_on": dt.date.today().isoformat(),
        "boards": board_rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the Grove example x board matrix.")
    parser.add_argument("--example", help="Grove reference grove/<module>/<demo> (default: all).")
    parser.add_argument("--board", action="append", help="Limit builds to these board ids (repeatable).")
    parser.add_argument("--zephyr-workspace", default=os.path.expanduser("~/zephyrproject"))
    parser.add_argument("--zephyr-version", default="v4.4.0")
    parser.add_argument("--no-build", action="store_true", help="Emit the skeleton without building.")
    args = parser.parse_args()

    workspace = Path(args.zephyr_workspace)
    examples = list_grove_examples()
    if args.example:
        parts = [p for p in args.example.strip("/").split("/") if p]
        if len(parts) != 3 or parts[0] != "grove":
            print("Error: --example must look like grove/<module>/<demo>", file=sys.stderr)
            return 2
        examples = [e for e in examples if e["module_id"] == parts[1] and e["demo"] == parts[2]]
    if not examples:
        print("No Grove examples found.", file=sys.stderr)
        return 1

    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    for example in examples:
        detail = show_example(str(example["module_id"]), str(example["demo"]))
        if not detail:
            continue
        matrix = build_example_matrix(
            example, detail, args.board, workspace, args.no_build, args.zephyr_version
        )
        if not matrix["boards"]:
            continue
        out_path = STATUS_DIR / f"{matrix['example_id']}.yaml"
        out_path.write_text(emit_yaml(matrix), encoding="utf-8")
        verified = sum(1 for b in matrix["boards"] if b["status"] == STATUS_BUILD_VERIFIED)
        failed = sum(1 for b in matrix["boards"] if b["status"] == STATUS_BUILD_FAILED)
        pending = sum(1 for b in matrix["boards"] if b["status"] == STATUS_PENDING)
        excluded = sum(1 for b in matrix["boards"] if b["status"] == STATUS_EXCLUDED)
        print(
            f"{matrix['example_id']}: verified={verified} failed={failed} "
            f"pending={pending} excluded={excluded} -> {out_path.relative_to(REPO_ROOT)}",
            flush=True,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
