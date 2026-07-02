# Seeed XIAO Zephyr Assistant (VS Code extension)

Create and open XIAO Zephyr projects, manage the extension environment, browse
XIAO boards, Grove modules, and expansion boards, then hand build/flash/monitor
actions to Zephyr tooling.

The extension reads repository metadata directly, so browsing works offline
without a Zephyr toolchain installed. Create and execute actions call the
`seeed-zephyr` CLI. Grove modules expand to the examples and board matrix
recorded in the repository.

创建和打开 XIAO Zephyr 项目,管理插件环境,浏览 XIAO 板子、Grove 模块和扩展板,
再把构建/烧录/监视操作交给 Zephyr 工具链。浏览直接读取仓库元数据,因此无需安装
Zephyr 工具链也能离线浏览;创建和执行操作会调用 `seeed-zephyr` CLI。Grove 模块
会展开显示仓库中记录的示例和板级矩阵。

## Install

Search **Seeed XIAO Zephyr** in the Extensions view of Cursor, Windsurf,
VSCodium, Gitpod, or Eclipse Theia, or install from the
[Open VSX listing](https://open-vsx.org/extension/seeed-studio/seeed-xiao-zephyr-assistant).

Build, flash, and monitor actions call the `seeed-zephyr` CLI. Install it with
`pip install seeed-zephyr`, and for the full Zephyr toolchain (SDK + `west`
workspace) use the one-line installer in the
[project README](https://github.com/limengdu/Seeed-Zephyr-Project#quick-start).
The sidebar is organized into **Projects**, **Extension Setup**, and **Catalog**.
Use **Projects** to create a generated project, open a generated project or
Zephyr app in a new window, or add it to the current workspace. Use **Extension Setup** for existing CLI
detection, extension-managed CLI installation, CLI version selection, manual CLI
path selection, repository folder selection, and repository updates.

在 Cursor、Windsurf、VSCodium、Gitpod 或 Eclipse Theia 的扩展面板搜索
**Seeed XIAO Zephyr** 安装,或从
[Open VSX 页面](https://open-vsx.org/extension/seeed-studio/seeed-xiao-zephyr-assistant)安装。
构建/烧录/监视会调用 `seeed-zephyr` CLI,用 `pip install seeed-zephyr` 安装即可。
左侧栏分为 **Projects**、**Extension Setup** 和 **Catalog**。在 **Projects** 里创建
生成项目、打开生成项目或 Zephyr app，或把项目加入当前工作区。在 **Extension Setup** 里
检测已有 CLI、安装插件托管 CLI、选择 CLI 版本、手动选择 CLI 路径、选择仓库目录和
更新仓库内容。

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
`package.json`, commit, then push to `main`:

```sh
git commit -am "release: extension 0.2.0" && git push
```

The workflow reads the new `version`, sees it is not on Open VSX yet, and
publishes it. An unchanged version is detected as already released and skipped.

The workflow publishes to each registry whose token secret is set: `VSCE_PAT`
for the VS Code Marketplace and `OVSX_PAT` for Open VSX. A missing token skips
that registry. Publishing a higher version updates the extension for installed
users automatically.

## Configuration

| Setting | Purpose |
| --- | --- |
| `seeedZephyr.repoRoot` | Repository path (auto-detected from the workspace when empty). |
| `seeedZephyr.cliPath` | Override the `seeed-zephyr` CLI command. |
| `seeedZephyr.managedCliVersion` | Version of the extension-managed CLI. |
| `seeedZephyr.pythonPath` | Python interpreter used to run the CLI from source. |
