import * as vscode from "vscode";
import { CatalogTreeProvider } from "./views/catalogTreeProvider";
import { DetailPanel, DetailTarget } from "./panels/detailPanel";
import { BoardNode, ExampleNode } from "./views/treeItems";
import { createProject } from "./commands/createProject";
import { openGenerated } from "./commands/openGenerated";
import { updateRepository } from "./commands/updateRepository";
import { Action, runAction, runProjectAction } from "./cli/terminalRunner";
import { ProjectStatusBar } from "./statusBar";

export function activate(context: vscode.ExtensionContext): void {
  const catalog = new CatalogTreeProvider();
  const statusBar = new ProjectStatusBar(context);
  statusBar.refresh();

  const action = (name: Action) => (node?: unknown) => runActionFromNode(catalog, name, node);
  const projectAction =
    (name: Action) => () => runProjectActionCmd(catalog, statusBar, context, name);

  context.subscriptions.push(
    vscode.window.registerTreeDataProvider("seeedZephyrCatalog", catalog),
    vscode.commands.registerCommand("seeedZephyr.refreshCatalog", () => catalog.refresh()),
    vscode.commands.registerCommand("seeedZephyr.updateRepository", () =>
      updateRepository(catalog.getRepoRoot(), () => catalog.refresh()),
    ),
    vscode.commands.registerCommand("seeedZephyr.setRepoRoot", () => setRepoRoot(catalog)),
    vscode.commands.registerCommand("seeedZephyr.showDetail", (target: DetailTarget) =>
      DetailPanel.show(target),
    ),
    vscode.commands.registerCommand("seeedZephyr.createProject", (node?: unknown) =>
      createProject(catalog.getRepoRoot(), catalog.getCatalog(), presetFromNode(node)),
    ),
    vscode.commands.registerCommand("seeedZephyr.openGenerated", () => openGenerated()),
    vscode.commands.registerCommand("seeedZephyr.build", action("build")),
    vscode.commands.registerCommand("seeedZephyr.flash", action("flash")),
    vscode.commands.registerCommand("seeedZephyr.monitor", action("monitor")),
    vscode.commands.registerCommand("seeedZephyr.debug", action("debug")),
    vscode.commands.registerCommand("seeedZephyr.projectBuild", projectAction("build")),
    vscode.commands.registerCommand("seeedZephyr.projectFlash", projectAction("flash")),
    vscode.commands.registerCommand("seeedZephyr.projectMonitor", projectAction("monitor")),
    vscode.workspace.onDidChangeWorkspaceFolders(() => statusBar.refresh()),
  );
}

// Runs a build/flash/monitor action against the current project from a status bar button.
// 从状态栏按钮对当前工程运行 build/flash/monitor 操作。
async function runProjectActionCmd(
  catalog: CatalogTreeProvider,
  statusBar: ProjectStatusBar,
  context: vscode.ExtensionContext,
  name: Action,
): Promise<void> {
  const project = statusBar.getProject();
  if (!project) {
    void vscode.window.showErrorMessage("No Zephyr project detected in this workspace.");
    return;
  }
  const board = await resolveProjectBoard(project.board, context);
  if (!board) {
    return;
  }
  runProjectAction(projectRepoRoot(catalog), name, board, project.appDir);
}

// Resolves the project board: from snapshot, remembered choice, or a one-time prompt.
// 解析工程板子:来自 snapshot、记住的选择,或一次性提示输入。
async function resolveProjectBoard(
  known: string | undefined,
  context: vscode.ExtensionContext,
): Promise<string | undefined> {
  if (known) {
    return known;
  }
  const remembered = context.workspaceState.get<string>("seeedZephyr.board");
  if (remembered) {
    return remembered;
  }
  const input = await vscode.window.showInputBox({
    prompt: "Board id for this project",
    placeHolder: "xiao_esp32c6",
  });
  if (input) {
    await context.workspaceState.update("seeedZephyr.board", input);
  }
  return input || undefined;
}

function projectRepoRoot(catalog: CatalogTreeProvider): string | undefined {
  return (
    catalog.getRepoRoot() ??
    vscode.workspace.getConfiguration("seeedZephyr").get<string>("repoRoot") ??
    undefined
  );
}

// Runs a build/flash/monitor/debug action from a clicked tree node.
// 从被点击的树节点运行 build/flash/monitor/debug 操作。
function runActionFromNode(catalog: CatalogTreeProvider, name: Action, node: unknown): void {
  const target = actionTarget(node);
  if (!target) {
    void vscode.window.showErrorMessage("Select a board or example first.");
    return;
  }
  runAction(catalog.getRepoRoot(), name, target.board, target.demo);
}

function actionTarget(node: unknown): { board: string; demo?: string } | undefined {
  if (node instanceof ExampleNode) {
    return { board: node.board.id, demo: node.example.demo };
  }
  if (node instanceof BoardNode) {
    return { board: node.board.id, demo: node.board.examples[0]?.demo };
  }
  return undefined;
}

// Derives a create-project preset from a clicked tree node, if any.
// 从被点击的树节点推导创建项目的预设(若有)。
function presetFromNode(
  node: unknown,
): { board: BoardNode["board"]; example?: ExampleNode["example"] } | undefined {
  if (node instanceof ExampleNode) {
    return { board: node.board, example: node.example };
  }
  if (node instanceof BoardNode) {
    return { board: node.board };
  }
  return undefined;
}

export function deactivate(): void {
  // No teardown required.
  // 不需要清理。
}

// Prompts for a repository folder and stores it in configuration.
// 提示选择仓库目录并存入配置。
async function setRepoRoot(catalog: CatalogTreeProvider): Promise<void> {
  const picked = await vscode.window.showOpenDialog({
    canSelectFolders: true,
    canSelectFiles: false,
    canSelectMany: false,
    openLabel: "Select seeed-zephyr repository",
  });
  if (!picked || picked.length === 0) {
    return;
  }
  await vscode.workspace
    .getConfiguration("seeedZephyr")
    .update("repoRoot", picked[0].fsPath, vscode.ConfigurationTarget.Global);
  catalog.refresh();
}
