# 入门和分发设计

本文档定义外部用户如何安装和使用 Seeed Zephyr Base。读者是 macOS、Windows 和 Linux 上的每一位 XIAO 产品用户，其中很多人并不是嵌入式专家。设计目标是把入门流程减少到尽可能少、尽可能快、尽可能可靠的步骤，并由项目吸收设置复杂性，而不是把它暴露给每个用户。

## 1. 要移除的摩擦

从零开始的手动设置流程（记录在 `AI use/en/validation-log.md` 中）会暴露三个外部用户原本会遇到的摩擦:

- **步骤分散。** Homebrew、Python venv、`west`、workspace init 和 update、SDK install 之间有十多个命令。
- **占用空间大。** 完整的 `west update` 会获取每个供应商 HAL，大约 5.4 GB，其中大部分不会被任何单块 XIAO 开发板使用。
- **版本协调。** Zephyr release、Python、SDK 和 module revisions 都必须对齐。验证过程中，只漏掉一次 venv 激活就已经导致首次尝试失败。

一句话总结: 手动路径又长、又重、又依赖版本，这些成本都应由项目承担，而不是由用户承担。

## 2. 设计原则

- **集中吸收一次复杂性。** 版本和依赖决策由项目制定和测试，绝不让每个用户重新推导。
- **每个平台采用最简单可行路径。** 覆盖 macOS、Windows 和 Linux；优先用一个命令，而不是多个命令。
- **建立在证据之上。** 每条自动化路径都从一次手动验证过的运行中冻结下来，而不是凭空假设。验证记录保存在 `AI use/en/validation-log.md` 中。

一句话总结: 在中心基于真实证据支付一次设置成本，让用户几乎不用付出成本。

## 3. 分层入门模型

入门流程设计为四层，每一层都比上一层移除更多摩擦。

| 层级 | 内容 | 移除的摩擦 | 用户操作 |
| --- | --- | --- | --- |
| L1 | 单命令 setup script（每个平台一份） | 分散步骤 | 运行一个 script |
| L2 | 项目 `west.yml` manifest | 占用空间大、版本协调 | `west init -m <repo>` + `west update` |
| L3 | Container image（可选） | 完整本地安装 | `docker run` / open dev container |
| L4 | VS Code plugin（阶段 2/3） | 完全不需要命令 | 在 IDE 中选择并点击 |

- **L1 — 单命令 setup script.** 每个平台的脚本（macOS 和 Linux 使用 shell，Windows 使用 PowerShell 或 WSL2）会检测已有工具、安装构建依赖和 SDK，并配置 mirrors。它移除的是分散步骤的摩擦。
- **L2 — 项目 west manifest.** 本仓库会携带一个 `west.yml`（目前尚未存在）。用户运行 `west init -m <this repo>`，再运行 `west update`，以获取被固定版本的 Zephyr、本项目，以及只有 XIAO 开发板需要的 modules。这是消费本项目的主要预期方式。
- **L3 — Container image（可选）.** 预构建的 Docker / Dev Container，内部已安装 toolchain，面向希望零本地安装的用户或 CI。从 container 烧录真实开发板会受 USB passthrough 限制，因此它面向构建和 CI，而不是板上调试。
- **L4 — VS Code plugin.** 阶段 2/3 的最终状态: 在 IDE 中选择开发板、模块和场景，环境、生成、构建和烧录都在 UI 背后交接完成。用户完全不输入命令。

一句话总结: 同一个产品可以通过 script、manifest、container 或点击来使用，每一层都会隐藏更多底层机制。

## 4. 版本管理

版本协调的复杂性由项目承担一次，而不是由每个用户承担。`west.yml` manifest 扮演 lockfile 的角色: 它固定 Zephyr revision 和每个 module 的准确 commit。项目维护这个单一文件，测试这组组合，然后发布它；每个用户的 `west update` 都会复现同一组已测试内容。升级 Zephyr 是项目动作：编辑 manifest、重新验证、发布；之后用户只需用普通的 `west update` 向前移动。

这与 `AI use/zh/01-phase-one-zephyr-base.md` 中的元数据模型一致: authored `version_policy` (`latest_stable`) 声明意图，derived `validated_zephyr_version` 记录 CI 已证明的准确 release。manifest 是让这个固定版本在每个用户机器上变成现实的机制。

一句话总结: 一个由项目维护的 lockfile，让每个用户都获得项目测试过的准确版本组合，用户自己无需做任何版本决策。

## 5. 占用空间和速度优化

- **Module scope.** manifest 用 name-allowlist 导入上游 Zephyr，因此只获取与 XIAO 相关的 HALs，大幅减少约 5.4 GB 的基线体积。
- **SDK scope.** 只安装 XIAO 使用的 toolchain architectures（Xtensa、RISC-V、Arm），而不是完整集合。
- **Mirrors.** Setup scripts 为 GitHub、pip 和 Zephyr SDK 提供 regional mirrors，以缩短首次下载时间。

一句话总结: 只获取 XIAO 需要的内容，并从最快的可用来源获取。

## 6. 目标用户体验

```text
Today (manual, validation phase):
  ten-plus steps, ~5.4 GB, user tracks versions          <- high barrier

L1 + L2 (scripted + manifest):
  1) run one setup script
  2) west init -m <this repo> && west update             <- two commands, versions pinned

L4 (plugin):
  select board, module, scenario, then click             <- no commands
```

一句话总结: 目标是命令行用户只需两个命令，plugin 用户不需要任何命令。

## 7. 实现路径

1. **先在 macOS 上手动验证。** 在 `AI use/en/validation-log.md` 中记录真实命令、耗时和坑点。（进行中）
2. **把已验证步骤冻结下来**，形成 macOS setup script、项目 `west.yml` 和分步骤文档（英文和简体中文）。
3. **为 Windows (WSL2) 和 Linux 复现。** 在对应平台或 CI 中完成测试前，把每个平台标记为未验证。

尚未存在，跟踪用于实现:

- `// TODO(manifest): add west.yml exposing this repo as the manifest repository`
- `// TODO(scripts): add per-platform setup scripts (macOS, Linux, Windows/WSL2)`
- `// TODO(samples): add baseline samples so the manifest has buildable targets`
- `// TODO(shields): add boards/shields for expansion boards`
- `// TODO(container): evaluate a Docker / dev container image for build and CI`

一句话总结: 在 macOS 上验证，把结果冻结成 script、manifest 和 docs，然后带着诚实的验证状态扩展到其他平台。

## 8. 待解决问题

- **Windows baseline.** WSL2（复用 Linux 路径）还是原生 Windows 支持。
- **Manifest topology.** 确认本仓库作为 manifest（T2 "star"）仓库，导入上游 Zephyr。
- **Mirror selection.** 默认使用哪些 regional mirrors，以及如何让用户选择加入或退出。

一句话总结: 在 scripts 和 manifest 最终确定前，仍需决定平台基线、manifest topology 和 mirror 默认值。
