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

## Configuration

| Setting | Purpose |
| --- | --- |
| `seeedZephyr.repoRoot` | Repository path (auto-detected from the workspace when empty). |
| `seeedZephyr.cliPath` | Override the `seeed-zephyr` CLI command. |
| `seeedZephyr.pythonPath` | Python interpreter used to run the CLI from source. |
