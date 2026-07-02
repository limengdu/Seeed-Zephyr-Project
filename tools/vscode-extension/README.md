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
The sidebar is organized into **Welcome**, **Projects**, **Environment**, and
**Catalog** views. Use **Welcome** for common setup and project actions. Use
**Projects** to create or open a project, select the project board and serial
port, and run project actions. Use **Environment** to check **Status**, update
repository content from the **Repository** group, and manage the selected
`seeed-zephyr` command from the **CLI** group. **Install Latest CLI** installs
the newest published CLI into extension storage and selects it automatically;
**Reinstall CLI** force-installs the newest package again; **Verify CLI** checks
the selected CLI version and required plugin commands; **Choose CLI Version**
installs a specific published version. Managed CLI installation uses Python 3.12
or newer and searches for a suitable Python before creating its venv. Install
and reinstall actions verify `info --json`, `list ports --json`, and
`create --help` before saving the managed CLI version. Serial port detection is
provided by the selected CLI; **Auto Port** uses the detected serial port when
no port has been selected yet, and **Select Port** opens the detected-port
picker. In that picker, **Auto Detector** keeps automatic detection enabled, and
a concrete port saves the user's selection for later upload and monitor actions.
When testing from a source checkout, select the checkout's `scripts/seeed-zephyr`
command. **Catalog** is visible by default, with Boards, Grove Modules, and
Expansion Boards collapsed until opened.

在 Cursor、Windsurf、VSCodium、Gitpod 或 Eclipse Theia 的扩展面板搜索
**Seeed XIAO Zephyr** 安装,或从
[Open VSX 页面](https://open-vsx.org/extension/seeed-studio/seeed-xiao-zephyr-assistant)安装。
构建/烧录/监视会调用 `seeed-zephyr` CLI,用 `pip install seeed-zephyr` 安装即可。
左侧栏分为 **Welcome**、**Projects**、**Environment** 和 **Catalog**。在 **Welcome**
里放常用入口。在 **Projects** 里创建或打开项目、选择项目开发板和串口，并运行项目操作。
在 **Environment** 里查看 **Status**，仓库内容放在 **Repository** 分组，CLI 工具版本
放在 **CLI** 分组。**Install Latest CLI** 会安装最新发布的 CLI，并自动切换插件使用它；
**Reinstall CLI** 会强制重新安装最新版；**Verify CLI** 会检查当前 CLI 版本和插件依赖的
基础命令；**Choose CLI Version** 用于指定发布版本。插件托管 CLI 使用 Python 3.12 或更新
版本，并会先查找可用 Python 再创建 venv。安装和重新安装会先验证 `info --json`、
`list ports --json` 和 `create --help`，通过后才保存托管 CLI 版本。串口检测由当前选择的
CLI 提供；没有手动选择串口时，**Auto Port** 会使用检测到的串口；点击 **Select Port**
会打开检测结果选择框，其中 **Auto Detector** 会保持自动检测，选择具体端口则会保存给后续
Upload 和 Monitor 使用。从源码测试时，选择当前仓库里的 `scripts/seeed-zephyr`。
**Catalog** 默认显示，Boards、Grove Modules、Expansion Boards 默认收起。

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
| `seeedZephyr.pythonPath` | Python interpreter used for managed CLI installation and CLI helper commands. |
