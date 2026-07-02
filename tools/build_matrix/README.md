# tools/build_matrix

## English

This directory contains the build matrix runner and its latest result record.

The build matrix proves which board targets and repository-owned baseline
examples compile against the pinned Zephyr baseline.

Use `tools/build_matrix/run.sh` from the repository root to rebuild every board
demo listed in `metadata/boards/`.

`tools/build_matrix/run_grove.py` extends the matrix to the Grove framework: it
builds each Grove example on every supported XIAO board and writes the
example x board status matrix into `metadata/status/<example_id>.yaml`.

## 中文

这个目录保存构建矩阵运行器和最近一次结果记录。

构建矩阵用于证明哪些 board target 和本仓库基线示例能在固定 Zephyr 基线下编译。

在仓库根目录运行 `tools/build_matrix/run.sh`，即可重新构建 `metadata/boards/` 中列出的每块开发板 demo。

`tools/build_matrix/run_grove.py` 将矩阵扩展到 Grove 框架:对每个 Grove 示例在所有支持的 XIAO 板上构建,
并将"示例 x 板子"状态矩阵写入 `metadata/status/<example_id>.yaml`。
