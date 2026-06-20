# tools/build_matrix

## English

This directory contains the build matrix runner and its latest result record.

The build matrix proves which board targets and repository-owned baseline
examples compile against the pinned Zephyr baseline.

Use `tools/build_matrix/run.sh` from the repository root to rebuild every board
demo listed in `metadata/boards/`.

## 中文

这个目录保存构建矩阵运行器和最近一次结果记录。

构建矩阵用于证明哪些 board target 和本仓库基线示例能在固定 Zephyr 基线下编译。

在仓库根目录运行 `tools/build_matrix/run.sh`，即可重新构建 `metadata/boards/` 中列出的每块开发板 demo。
