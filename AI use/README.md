# AI Use / AI 使用说明

## English

This folder is the project charter for AI agents working on Seeed Zephyr Base.
Every AI agent must read this folder before making product, architecture,
documentation, example, tooling, or roadmap changes.

The project mission is:

```text
Build the Seeed XIAO + Grove Zephyr example library, project collection,
capability catalog, validation knowledge base, and future project-generation
foundation.
```

The repository should be evaluated by the quality of its reusable assets:
examples, projects, metadata, validation evidence, and contribution workflow.
Setup scripts, generators, and plugins are delivery mechanisms for those assets.

Priority order:

1. Real XIAO and Grove examples that users can find, build, flash, modify, and
   learn from.
2. Complete projects that combine boards, Grove modules, expansion boards, and
   real scenarios.
3. Metadata and validation evidence that prove what works, what is build-only,
   what is hardware-tested, and what is unsupported.
4. Community contribution paths for examples and projects.
5. CLI and plugin tooling that make the above assets easier to discover,
   generate, build, and validate.

AI constraints:

- All AI-facing strategy, constraints, handoff notes, and work logs belong under
  this `AI use/` folder.
- Do not create AI planning logs, hidden prompts, agent notes, or agent
  constraints in unrelated project folders.
- After a meaningful AI work session, append a detailed, factual entry to
  `AI use/WORKLOG.md`.
- Do not write private conversation details into source code, examples, README
  files, commit messages, or user-facing project assets.
- When unsure whether a task supports the mission, choose the path that creates
  or improves examples, projects, validation evidence, or contribution quality.

One-sentence summary: this folder keeps AI agents aligned with the reusable
example and project ecosystem this repository is building.

## 中文

这个文件夹是 AI 参与 Seeed Zephyr Base 项目时必须先读的纲领文件夹。任何 AI
在修改产品定位、架构、文档、示例、工具或路线图之前，都必须先理解这里的内容。

本项目使命是:

```text
建设 Seeed XIAO + Grove 的 Zephyr 示例库、项目合集、能力目录、验证知识库，
以及未来项目生成工具的基础设施。
```

评估这个仓库时，应看它的可复用资产质量: 示例、项目、metadata、验证证据和贡献流程。
Setup 脚本、生成器和插件都是这些资产的交付方式。

价值优先级:

1. 用户能找到、构建、烧录、修改、学习的真实 XIAO 和 Grove 示例。
2. 组合开发板、Grove 模块、扩展板和真实场景的完整项目。
3. 证明什么可用、什么只是 build-only、什么经过硬件测试、什么不支持的 metadata
   和验证证据。
4. 外部社区贡献示例和项目的入口。
5. 让上述资产更容易发现、生成、构建和验证的 CLI 与插件工具。

AI 约束:

- 所有面向 AI 的战略、约束、交接说明和工作日志，都必须放在 `AI use/` 文件夹下。
- 不要在其他项目目录中创建 AI planning logs、隐藏 prompt、agent notes 或 agent
  constraints。
- 每次完成有意义的 AI 工作后，必须向 `AI use/WORKLOG.md` 追加详细、客观的记录。
- 不要把私人对话细节写入源代码、示例、README、commit message 或面向用户的项目资产。
- 当不确定一个任务是否支持项目使命时，优先选择能创建或改善示例、项目、验证证据、
  贡献质量的路径。

一句话总结: 这个文件夹确保 AI 围绕可复用示例和项目生态来工作。
