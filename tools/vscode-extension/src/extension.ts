import * as vscode from "vscode";
import { CatalogTreeProvider } from "./views/catalogTreeProvider";
import { DetailPanel, DetailTarget } from "./panels/detailPanel";
import { BoardNode, ExampleNode, GroveExampleNode } from "./views/treeItems";
import { createProject, CreatePreset } from "./commands/createProject";
import { openGenerated } from "./commands/openGenerated";
import { updateRepository } from "./commands/updateRepository";
import {
  installManagedCli,
  selectCliPath,
  setupEnvironment,
  useExistingCli,
} from "./commands/environmentCommands";
import {
  getEffectiveBoard,
  resolveProjectPort,
  selectProjectBoard,
  selectProjectPort,
} from "./commands/projectSettings";
import { Action, runAction, runProjectAction } from "./cli/terminalRunner";
import { ProjectStatusBar } from "./statusBar";
import type { ProjectInfo } from "./statusBar";

export function activate(context: vscode.ExtensionContext): void {
  const catalog = new CatalogTreeProvider(context);
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
    vscode.commands.registerCommand("seeedZephyr.setupEnvironment", () => setupEnvironment()),
    vscode.commands.registerCommand("seeedZephyr.useExistingCli", () =>
      useExistingCli(() => catalog.refresh()),
    ),
    vscode.commands.registerCommand("seeedZephyr.installManagedCli", () =>
      installManagedCli(context, () => catalog.refresh()),
    ),
    vscode.commands.registerCommand("seeedZephyr.selectCliVersion", () =>
      installManagedCli(context, () => catalog.refresh()),
    ),
    vscode.commands.registerCommand("seeedZephyr.selectCliPath", () =>
      selectCliPath(() => catalog.refresh()),
    ),
    vscode.commands.registerCommand("seeedZephyr.recheckEnvironment", () => catalog.refresh()),
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
    vscode.commands.registerCommand("seeedZephyr.selectProjectBoard", () =>
      selectProjectBoardCmd(catalog, statusBar, context),
    ),
    vscode.commands.registerCommand("seeedZephyr.selectProjectPort", () =>
      selectProjectPortCmd(catalog, statusBar, context),
    ),
    vscode.commands.registerCommand("seeedZephyr.projectBuild", projectAction("build")),
    vscode.commands.registerCommand("seeedZephyr.projectFlash", projectAction("flash")),
    vscode.commands.registerCommand("seeedZephyr.projectMonitor", projectAction("monitor")),
    vscode.workspace.onDidChangeWorkspaceFolders(() => {
      statusBar.refresh();
      catalog.refresh();
    }),
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
  const board = await resolveProjectBoard(project, catalog, context);
  if (!board) {
    return;
  }
  const needsPort = name === "flash" || name === "monitor";
  const port = needsPort
    ? await resolveProjectPort(context, project, projectRepoRoot(catalog))
    : undefined;
  if (needsPort && !port) {
    return;
  }
  runProjectAction(projectRepoRoot(catalog), name, board, project.appDir, { port });
}

// Resolves the project board from snapshot or saved selection, then prompts from catalog.
// 从 snapshot 或已保存选择解析板子,必要时从 catalog 弹窗选择。
async function resolveProjectBoard(
  project: ProjectInfo,
  catalog: CatalogTreeProvider,
  context: vscode.ExtensionContext,
): Promise<string | undefined> {
  const known = getEffectiveBoard(context, project);
  if (known) {
    return known;
  }
  return selectProjectBoard(context, project, catalog.getCatalog());
}

async function selectProjectBoardCmd(
  catalog: CatalogTreeProvider,
  statusBar: ProjectStatusBar,
  context: vscode.ExtensionContext,
): Promise<void> {
  const project = requireCurrentProject(statusBar);
  if (!project) {
    return;
  }
  await selectProjectBoard(context, project, catalog.getCatalog());
  statusBar.refresh();
  catalog.refresh();
}

async function selectProjectPortCmd(
  catalog: CatalogTreeProvider,
  statusBar: ProjectStatusBar,
  context: vscode.ExtensionContext,
): Promise<void> {
  const project = requireCurrentProject(statusBar);
  if (!project) {
    return;
  }
  await selectProjectPort(context, project, projectRepoRoot(catalog));
  statusBar.refresh();
  catalog.refresh();
}

function requireCurrentProject(statusBar: ProjectStatusBar) {
  const project = statusBar.getProject();
  if (!project) {
    void vscode.window.showErrorMessage("No Zephyr project detected in this workspace.");
  }
  return project;
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
): CreatePreset | undefined {
  if (node instanceof ExampleNode) {
    return { board: node.board, example: node.example };
  }
  if (node instanceof GroveExampleNode) {
    return { groveExample: node.example };
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
