import * as vscode from "vscode";
import { ActionNode, CatalogNode } from "./treeItems";

export class WelcomeTreeProvider implements vscode.TreeDataProvider<CatalogNode> {
  private readonly _onDidChangeTreeData = new vscode.EventEmitter<void>();
  readonly onDidChangeTreeData = this._onDidChangeTreeData.event;
  refresh(): void {
    this._onDidChangeTreeData.fire();
  }

  getTreeItem(node: CatalogNode): vscode.TreeItem {
    return node;
  }

  getChildren(): CatalogNode[] {
    return [
      new ActionNode(
        "Install Latest CLI",
        "seeedZephyr.installManagedCli",
        "cloud-download",
        "online latest",
      ),
      new ActionNode("Create Project", "seeedZephyr.createProject", "new-folder"),
      new ActionNode("Open Project", "seeedZephyr.openGenerated", "folder-opened"),
      new ActionNode(
        "Update Repository",
        "seeedZephyr.updateRepository",
        "sync",
        "examples and catalog",
      ),
    ];
  }
}
