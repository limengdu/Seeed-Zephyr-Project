# AI Work Log / AI 工作记录

## Purpose / 用途

English: This file records meaningful AI work on this repository. It is not a
chat transcript. It is a factual handoff log so a future AI agent can understand
what changed, why it changed, how it was verified, and what remains.

中文: 本文件记录 AI 在本仓库中完成的重要工作。它不是聊天记录，而是事实性交接日志，
帮助未来 AI 明确改了什么、为什么改、如何验证、还剩什么。

## Required Entry Format / 必填记录格式

```text
## YYYY-MM-DD - short title

Scope:
- Files or directories changed.

Reason:
- Product or technical reason for the change.

Result:
- What changed in user-visible or maintainer-visible behavior.

Verification:
- Commands run and results.

Remaining:
- Follow-up work, known limits, or open questions.
```

## 2026-06-20 - Align AI charter with examples and projects mission

Scope:
- Reframed `AI use/` as the AI-facing project charter folder.
- Added the requirement that AI constraints, AI handoff notes, and AI work logs
  live under `AI use/`.
- Reoriented the strategic documents toward examples, projects, capability
  coverage, validation evidence, and community contributions as the primary
  product assets.
- Added bilingual README files to project directories.

Reason:
- Future AI agents need a clear mission without relying on private conversation context.
- The project direction should be stated as reusable examples, projects,
  validation evidence, and contribution workflow.

Result:
- The project direction now starts from user-facing examples and complete projects.
- CLI, VS Code plugin, setup scripts, and metadata are framed as support systems
  around the example/project catalog.

Verification:
- `bash -n scripts/setup-macos.sh`: passed.
- `bash -n tools/build_matrix/run.sh`: passed.
- `/Users/mengdu/zephyrproject/.venv/bin/python tools/validate_metadata/validate.py`:
  18 passed, 0 failed.
- `git diff --check`: passed.
- Sensitive keyword scan over README, docs, scripts, tools, metadata, `AI use/`,
  and `.github`: no matches.
- Directory README coverage check: no project directory missing `README.md`.
- Corrective negative-direction keyword scan: no matches outside factual
  validation/status wording.

Remaining:
- Create the first repository-owned examples under `examples/`.
- Add contribution rules for community examples and projects.
