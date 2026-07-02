# examples

## English

This directory contains repository-owned Zephyr examples for Seeed XIAO boards,
Grove modules, and expansion boards.

Examples here are the user-facing assets that scripts, metadata, docs, and
future generators should build from. Build commands should point directly to
these examples.

- `examples/boards/<board_id>/<demo>/` — one minimum demo per XIAO board.
- `examples/grove/<module_id>/<demo>/` — board-agnostic Grove module examples that
  build for every XIAO board via the `seeed_xiao_connector` abstraction.

## 中文

这个目录保存本仓库自己的 Zephyr 示例，覆盖 Seeed XIAO 开发板、Grove 模块和扩展板。

这里的示例是用户真正会打开、构建和学习的资产。脚本、metadata、文档和未来生成器都应围绕这些示例工作，并直接指向这些示例。

- `examples/boards/<board_id>/<demo>/`——每块 XIAO 板一个最小 demo。
- `examples/grove/<module_id>/<demo>/`——板级无关的 Grove 模块示例，通过 `seeed_xiao_connector`
  抽象在所有 XIAO 板上构建。
