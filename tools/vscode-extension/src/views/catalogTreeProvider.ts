import * as vscode from "vscode";
import * as fs from "fs";
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
      if (node.group === "setupStatus") {
        return this.setupStatusNodes();
      }
      if (node.group === "setupRecommended") {
        return this.setupRecommendedNodes();
      }
      if (node.group === "setupRepository") {
        return this.setupRepositoryNodes();
      }
      if (node.group === "setupCli") {
        return this.setupCliNodes();
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
    return [
      new GroupNode("Status", "setupStatus", this.environment?.ready ? "ready" : "setup needed"),
      new GroupNode("Recommended", "setupRecommended", "start here"),
      new GroupNode("Repository", "setupRepository", "examples and catalog"),
      new GroupNode("CLI", "setupCli", "tool version"),
    ];
  }

  private setupStatusNodes(): CatalogNode[] {
    if (!this.environment) {
      return [new MessageNode("Environment", "not checked", "warning")];
    }

    const nodes: CatalogNode[] = [
      new MessageNode(
        this.environment.ready ? "Environment Ready" : "Setup Needed",
        this.environment.ready ? "ready to build" : "complete repository and CLI setup",
      ),
    ];

    for (const issue of this.environment.issues) {
      nodes.push(new MessageNode(issue, "action needed"));
    }

    nodes.push(
      new MessageNode(
        "Repository Folder",
        this.environment.repoRoot ?? "not selected",
      ),
      new MessageNode(
        "CLI Command",
        this.environment.cli.display,
      ),
      new MessageNode("CLI Source", cliSourceLabel(this.environment.cli.source)),
    );

    const version = this.cliVersionLabel();
    if (version) {
      nodes.push(new MessageNode("CLI Version", version));
    }

    return nodes;
  }

  private setupRecommendedNodes(): CatalogNode[] {
    const description = this.repoRoot ? "use repository CLI" : "install managed CLI";
    return [
      new ActionNode(
        "Use Recommended CLI",
        "seeedZephyr.useRecommendedCli",
        "check",
        description,
        "Select the CLI that best matches this workspace.",
      ),
      new ActionNode(
        "Run Full Setup",
        "seeedZephyr.setupEnvironment",
        "rocket",
        "install Zephyr tools",
        "Run the installer for the repository, Zephyr SDK, west workspace, and CLI.",
      ),
    ];
  }

  private setupRepositoryNodes(): CatalogNode[] {
    return [
      new ActionNode(
        "Select Repository Folder",
        "seeedZephyr.setRepoRoot",
        "repo",
        "examples and catalog",
        "Choose the repository checkout that provides examples and metadata.",
      ),
      new ActionNode(
        "Update Repository",
        "seeedZephyr.updateRepository",
        "sync",
        "pull latest content",
        "Pull the latest examples, metadata, and catalog files.",
      ),
      new ActionNode(
        "Refresh Environment Status",
        "seeedZephyr.recheckEnvironment",
        "refresh",
        "reload local state",
        "Reload the extension state after files or settings changed.",
      ),
    ];
  }

  private setupCliNodes(): CatalogNode[] {
    return [
      new ActionNode(
        "Install or Update Managed CLI",
        "seeedZephyr.installManagedCli",
        "cloud-download",
        "extension managed",
        "Install a CLI copy owned by the extension.",
      ),
      new ActionNode(
        "Select Managed CLI Version",
        "seeedZephyr.selectCliVersion",
        "versions",
        "choose published version",
        "Install a selected published CLI version into extension storage.",
      ),
      new ActionNode(
        "Use System CLI",
        "seeedZephyr.useExistingCli",
        "terminal",
        "PATH command",
        "Use the seeed-zephyr command already available on this computer.",
      ),
      new ActionNode(
        "Select CLI Path",
        "seeedZephyr.selectCliPath",
        "folder-opened",
        "advanced",
        "Choose a specific seeed-zephyr command or script.",
      ),
    ];
  }

  private cliVersionLabel(): string | undefined {
    if (!this.environment) {
      return undefined;
    }
    const config = vscode.workspace.getConfiguration("seeedZephyr");
    if (this.environment.cli.source === "managed") {
      return config.get<string>("managedCliVersion") || "managed";
    }
    if (this.repoRoot && usesRepoCli(this.environment.cli.command, this.repoRoot)) {
      return readRepoCliVersion(this.repoRoot) ?? "repository";
    }
    return undefined;
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

function cliSourceLabel(source: EnvironmentState["cli"]["source"]): string {
  switch (source) {
    case "configured":
      return "selected path";
    case "managed":
      return "extension managed";
    case "repo":
      return "repository checkout";
    case "path":
      return "system PATH";
    case "missing":
      return "not configured";
  }
}

function usesRepoCli(command: string, repoRoot: string): boolean {
  const wrapper = path.join(repoRoot, "scripts", "seeed-zephyr");
  try {
    return path.resolve(command) === wrapper || path.resolve(repoRoot, command) === wrapper;
  } catch {
    return command === wrapper || command === "scripts/seeed-zephyr";
  }
}

function readRepoCliVersion(repoRoot: string): string | undefined {
  const versionFile = path.join(
    repoRoot,
    "packages",
    "seeed-zephyr",
    "src",
    "seeed_zephyr",
    "__init__.py",
  );
  try {
    const content = fs.readFileSync(versionFile, "utf-8");
    return content.match(/__version__\s*=\s*"([^"]+)"/)?.[1];
  } catch {
    return undefined;
  }
}
