import * as vscode from "vscode";
import * as path from "path";
import { detectEnvironment, EnvironmentState } from "../env/environment";
import { readCatalog } from "../repo/dataReader";
import { locateRepoRoot } from "../repo/repoLocator";
import { Catalog } from "../model/types";
import { detectProject } from "../statusBar";
import type { ProjectInfo } from "../statusBar";
import { displayBoard, displayPort } from "../commands/projectSettings";
import {
  ActionNode,
  BoardNode,
  CatalogNode,
  ExampleNode,
  ExpansionNode,
  GroveExampleNode,
  GroupNode,
  MessageNode,
  ModuleNode,
  ProjectNode,
} from "./treeItems";

export class CatalogTreeProvider implements vscode.TreeDataProvider<CatalogNode> {
  private readonly _onDidChangeTreeData = new vscode.EventEmitter<void>();
  readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

  private repoRoot: string | undefined;
  private catalog: Catalog | undefined;
  private environment: EnvironmentState | undefined;
  private project: ProjectInfo | undefined;

  constructor(private readonly context: vscode.ExtensionContext) {
    this.load();
  }

  // Reloads the catalog from disk and refreshes the tree.
  // 从磁盘重新加载目录并刷新树。
  refresh(): void {
    this.load();
    this._onDidChangeTreeData.fire();
  }

  // Returns the located repository root, if any.
  // 返回定位到的仓库根(若有)。
  getRepoRoot(): string | undefined {
    return this.repoRoot;
  }

  // Returns the loaded catalog, if any.
  // 返回已加载的目录(若有)。
  getCatalog(): Catalog | undefined {
    return this.catalog;
  }

  // Returns the current environment state used by the welcome screen.
  // 返回欢迎页使用的当前环境状态。
  getEnvironment(): EnvironmentState | undefined {
    return this.environment;
  }

  private load(): void {
    this.repoRoot = locateRepoRoot();
    this.environment = detectEnvironment(this.repoRoot, this.context.globalStorageUri.fsPath);
    this.project = detectProject();
    try {
      this.catalog = this.repoRoot ? readCatalog(this.repoRoot) : undefined;
    } catch (error) {
      this.catalog = undefined;
      void vscode.window.showErrorMessage(`Failed to read catalog: ${String(error)}`);
    }
  }

  getTreeItem(node: CatalogNode): vscode.TreeItem {
    return node;
  }

  getChildren(node?: CatalogNode): CatalogNode[] {
    if (!node) {
      return [
        new GroupNode("Projects", "projects"),
        new GroupNode("Extension Setup", "setup", this.environment?.ready ? "ready" : "setup needed"),
        new GroupNode("Catalog", "catalog", this.catalog ? "ready" : "not loaded"),
      ];
    }
    if (node instanceof GroupNode) {
      if (node.group === "projects") {
        return this.projectNodes();
      }
      if (node.group === "setup") {
        return this.setupNodes();
      }
      if (node.group === "catalog") {
        return this.catalogNodes();
      }
      if (!this.catalog) {
        return [];
      }
      if (node.group === "boards") {
        return this.catalog.boards.map((board) => new BoardNode(board));
      }
      if (node.group === "modules") {
        return this.catalog.modules.map((module) => new ModuleNode(module));
      }
      return this.catalog.expansions.map((expansion) => new ExpansionNode(expansion));
    }
    if (node instanceof BoardNode) {
      return node.board.examples.map((example) => new ExampleNode(example, node.board));
    }
    if (node instanceof ModuleNode) {
      return node.module.examples.map((example) => new GroveExampleNode(example, node.module));
    }
    if (node instanceof ProjectNode) {
      const board = displayBoard(this.context, node.project);
      const port = displayPort(this.context, node.project);
      return [
        new ActionNode("Select Board", "seeedZephyr.selectProjectBoard", "circuit-board", board),
        new ActionNode("Build Project", "seeedZephyr.projectBuild", "check"),
        new ActionNode("Upload Project", "seeedZephyr.projectFlash", "arrow-up"),
        new ActionNode("Select Port", "seeedZephyr.selectProjectPort", "plug", port),
        new ActionNode("Monitor Project", "seeedZephyr.projectMonitor", "terminal"),
      ];
    }
    return [];
  }

  private projectNodes(): CatalogNode[] {
    const nodes: CatalogNode[] = [
      new ActionNode("Create Project", "seeedZephyr.createProject", "new-folder"),
      new ActionNode("Open Project", "seeedZephyr.openGenerated", "folder-opened"),
    ];
    if (this.project) {
      nodes.push(
        new ProjectNode(
          path.basename(this.project.appDir),
          this.project,
          displayBoard(this.context, this.project),
          displayPort(this.context, this.project),
        ),
      );
    } else {
      nodes.push(new MessageNode("No project in the current workspace."));
    }
    return nodes;
  }

  private setupNodes(): CatalogNode[] {
    const nodes: CatalogNode[] = [
      new MessageNode(this.environment?.ready ? "Environment ready." : "Set up the extension environment."),
    ];
    if (this.environment) {
      nodes.push(
        new MessageNode(`Repository: ${this.environment.repoRoot ?? "not selected"}`),
        new MessageNode(`CLI: ${this.environment.cli.display}`),
      );
    }
    nodes.push(
      new ActionNode("Update Repository", "seeedZephyr.updateRepository", "sync"),
      new ActionNode("Set Up Environment", "seeedZephyr.setupEnvironment", "rocket"),
      new ActionNode("Use Existing CLI", "seeedZephyr.useExistingCli", "terminal"),
      new ActionNode("Install Managed CLI", "seeedZephyr.installManagedCli", "cloud-download"),
      new ActionNode("Select CLI Version", "seeedZephyr.selectCliVersion", "versions"),
      new ActionNode("Select CLI Path", "seeedZephyr.selectCliPath", "folder-opened"),
      new ActionNode("Select Repository Folder", "seeedZephyr.setRepoRoot", "repo"),
      new ActionNode("Recheck Environment", "seeedZephyr.recheckEnvironment", "refresh"),
    );
    return nodes;
  }

  private catalogNodes(): CatalogNode[] {
    if (!this.catalog) {
      return [
        new MessageNode(
          "No catalog loaded. Select a repository folder or finish extension setup.",
        ),
      ];
    }
    return [
      new GroupNode("Boards", "boards", this.catalog.boards.length),
      new GroupNode("Grove Modules", "modules", this.catalog.modules.length),
      new GroupNode("Expansion Boards", "expansions", this.catalog.expansions.length),
    ];
  }
}
