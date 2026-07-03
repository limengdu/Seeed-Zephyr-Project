import * as fs from "fs";
import * as path from "path";
import * as vscode from "vscode";
import { detectEnvironment, EnvironmentState } from "../env/environment";
import { locateRepoRoot } from "../repo/repoLocator";
import { ActionNode, CatalogNode, GroupNode, MessageNode } from "./treeItems";

export class EnvironmentTreeProvider implements vscode.TreeDataProvider<CatalogNode> {
  private readonly _onDidChangeTreeData = new vscode.EventEmitter<void>();
  readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

  private repoRoot: string | undefined;
  private environment: EnvironmentState | undefined;

  constructor(private readonly context: vscode.ExtensionContext) {
    this.load();
  }

  refresh(): void {
    this.load();
    this._onDidChangeTreeData.fire();
  }

  getRepoRoot(): string | undefined {
    return this.repoRoot;
  }

  private load(): void {
    this.repoRoot = locateRepoRoot();
    this.environment = detectEnvironment(this.repoRoot, this.context.globalStorageUri.fsPath);
  }

  getTreeItem(node: CatalogNode): vscode.TreeItem {
    return node;
  }

  getChildren(node?: CatalogNode): CatalogNode[] {
    if (!node) {
      const cliVersion = this.cliVersionLabel();
      return [
        new GroupNode("Status", "setupStatus", this.environment?.ready ? "ready" : "setup needed"),
        new GroupNode(
          "Repository",
          "setupRepository",
          "examples and catalog",
          vscode.TreeItemCollapsibleState.Collapsed,
        ),
        new GroupNode(
          "CLI",
          "setupCli",
          cliVersion ? `version ${cliVersion}` : "tool version",
          vscode.TreeItemCollapsibleState.Collapsed,
        ),
      ];
    }
    if (node instanceof GroupNode) {
      if (node.group === "setupStatus") {
        return this.statusNodes();
      }
      if (node.group === "setupRepository") {
        return this.repositoryNodes();
      }
      if (node.group === "setupCli") {
        return this.cliNodes();
      }
    }
    return [];
  }

  private statusNodes(): CatalogNode[] {
    if (!this.environment) {
      return [new MessageNode("Environment", "not checked")];
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
      new MessageNode("Repository", this.environment.repoRoot ?? "not selected"),
      new MessageNode("CLI", this.environment.cli.display),
    );

    const version = this.cliVersionLabel();
    if (version) {
      nodes.push(new MessageNode("Version", version));
    }

    return nodes;
  }

  private repositoryNodes(): CatalogNode[] {
    return [
      new ActionNode(
        "Select Repository Folder",
        "seeedZephyr.setRepoRoot",
        "repo",
        "examples and catalog",
      ),
      new ActionNode(
        "Update Repository",
        "seeedZephyr.updateRepository",
        "sync",
        "pull latest content",
      ),
      new ActionNode(
        "Refresh Environment Status",
        "seeedZephyr.recheckEnvironment",
        "refresh",
        "reload local state",
      ),
    ];
  }

  private cliNodes(): CatalogNode[] {
    return [
      new ActionNode(
        "Install Latest CLI",
        "seeedZephyr.installManagedCli",
        "cloud-download",
        "online latest",
      ),
      new ActionNode(
        "Reinstall CLI",
        "seeedZephyr.reinstallManagedCli",
        "debug-restart",
        "force latest",
      ),
      new ActionNode(
        "Verify CLI",
        "seeedZephyr.verifyCli",
        "verified",
        "check selected",
      ),
      new ActionNode(
        "Choose CLI Version",
        "seeedZephyr.selectCliVersion",
        "versions",
        "specific version",
      ),
      new ActionNode(
        "Use System CLI",
        "seeedZephyr.useExistingCli",
        "terminal",
        "PATH command",
      ),
      new ActionNode(
        "Select CLI Path",
        "seeedZephyr.selectCliPath",
        "folder-opened",
        "advanced",
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
