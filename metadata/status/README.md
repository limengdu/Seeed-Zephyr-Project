# Validation Status Matrix

This directory records the build and hardware verification status for examples that
span multiple boards, expressed as an **example x board** matrix.

The Grove framework writes one file per Grove example here
(`tools/build_matrix/run_grove.py` is the generator). Board-bound examples keep
their single `validation_status` field in `examples/boards/<board>/<demo>/example.yaml`.

## File schema

Each `<example_id>.yaml` file:

```yaml
example_id: grove_scd41_basic_read
example_ref: grove/<module>/<demo>
zephyr_version: v4.4.0
generated_on: 2026-07-02
boards:
  - board_id: xiao_esp32c6
    status: build-verified
    evidence: seeed-zephyr build (local, 2026-07-02)
  - board_id: xiao_esp32c5
    status: excluded
    reason: listed in excluded_boards
  - board_id: xiao_esp32s3
    status: pending
```

## Status values

| status           | meaning                                                        |
| ---------------- | ------------------------------------------------------------- |
| `build-verified` | Compiled successfully with `seeed-zephyr build` on this board. |
| `build-failed`   | The build failed; `evidence` holds the error excerpt.         |
| `hardware-tested`| Built and run on physical hardware with the expected output.  |
| `pending`        | Not yet built on this board.                                  |
| `excluded`       | The example declares this board in `excluded_boards`.         |

## Regenerating

```bash
# Build every Grove example on every supported board (full CI pass):
python3 tools/build_matrix/run_grove.py

# Build one example on a few boards (others stay pending):
python3 tools/build_matrix/run_grove.py \
  --example grove/grove_scd41_co2_temperature_humidity_sensor/basic_read \
  --board xiao_esp32c6 --board xiao_nrf52840

# Emit the skeleton from metadata without building:
python3 tools/build_matrix/run_grove.py --no-build
```

After a hardware run, promote a board from `build-verified` to `hardware-tested`
and record the evidence in `AI use/HARDWARE_VERIFICATION.md`.
