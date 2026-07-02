import * as path from "path";
import * as vscode from "vscode";
import { displayBoard, displayPort } from "../commands/projectSettings";
import { detectProject } from "../statusBar";
import type { ProjectInfo } from "../statusBar";
import { ActionNode, CatalogNode, MessageNode, ProjectNode } from "./treeItems";

export class ProjectsTreeProvider implements vscode.TreeDataProvider<CatalogNode> {
  private readonly _onDidChangeTreeData = new vscode.EventEmitter<void>();
  readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

  private project: ProjectInfo | undefined;

  constructor(private readonly context: vscode.ExtensionContext) {
    this.load();
  }

  refresh(): void {
    this.load();
    this._onDidChangeTreeData.fire();
  }

  private load(): void {
    this.project = detectProject();
  }

  getTreeItem(node: CatalogNode): vscode.TreeItem {
    return node;
  }

  getChildren(node?: CatalogNode): CatalogNode[] {
    if (!node) {
      return this.projectNodes();
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
}
