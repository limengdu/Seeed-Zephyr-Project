# Seeed XIAO Zephyr Assistant (VS Code extension)

Browse XIAO boards, Grove modules, and expansion boards; preview verified
examples; create a project from an example; then hand build/flash/monitor/debug
to Zephyr tooling.

The extension reads repository metadata directly, so browsing works offline
without a Zephyr toolchain installed. Create and execute actions call the
`seeed-zephyr` CLI.

浏览 XIAO 板子、Grove 模块和扩展板;预览验证过的示例;从示例创建项目;再把
构建/烧录/监视/调试交给 Zephyr 工具链。浏览直接读取仓库元数据,因此无需安装
Zephyr 工具链也能离线浏览;创建和执行操作会调用 `seeed-zephyr` CLI。

## Install

Search **Seeed XIAO Zephyr** in the Extensions view of Cursor, Windsurf,
VSCodium, Gitpod, or Eclipse Theia, or install from the
[Open VSX listing](https://open-vsx.org/extension/seeed-studio/seeed-xiao-zephyr-assistant).

Build, flash, and monitor actions call the `seeed-zephyr` CLI. Install it with
`pip install seeed-zephyr`, and for the full Zephyr toolchain (SDK + `west`
workspace) use the one-line installer in the
[project README](https://github.com/limengdu/Seeed-Zephyr-Project#quick-start).

在 Cursor、Windsurf、VSCodium、Gitpod 或 Eclipse Theia 的扩展面板搜索
**Seeed XIAO Zephyr** 安装,或从
[Open VSX 页面](https://open-vsx.org/extension/seeed-studio/seeed-xiao-zephyr-assistant)安装。
构建/烧录/监视会调用 `seeed-zephyr` CLI,用 `pip install seeed-zephyr` 安装即可。

## Develop

```sh
cd tools/vscode-extension
npm install
npm run watch      # bundle in watch mode
```

Press `F5` in VS Code with this folder open to launch an Extension Development
Host. Open the repository root as a workspace folder so the catalog populates.

按 `F5` 启动扩展开发宿主;把仓库根作为工作区文件夹打开,目录就会填充。

## Build and package

```sh
npm run check-types   # type-check only
npm run build         # production bundle to dist/
npm run package       # produce a .vsix with vsce
```

## Publish

Publishing runs from GitHub Actions (`.github/workflows/release-vscode.yml`) and
targets both the VS Code Marketplace and Open VSX. Bump `version` in
`package.json`, commit, then push a matching tag:

```sh
git tag ext-v0.1.1 && git push origin ext-v0.1.1
```

The workflow publishes to each registry whose token secret is set: `VSCE_PAT`
for the VS Code Marketplace and `OVSX_PAT` for Open VSX. A missing token skips
that registry. Publishing a higher version updates the extension for installed
users automatically.

## Configuration

| Setting | Purpose |
| --- | --- |
| `seeedZephyr.repoRoot` | Repository path (auto-detected from the workspace when empty). |
| `seeedZephyr.cliPath` | Override the `seeed-zephyr` CLI command. |
| `seeedZephyr.pythonPath` | Python interpreter used to run the CLI from source. |
