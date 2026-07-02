import * as vscode from "vscode";
import { readCatalog } from "../repo/dataReader";
import { locateRepoRoot } from "../repo/repoLocator";
import { Catalog } from "../model/types";
import {
  BoardNode,
  CatalogNode,
  ExampleNode,
  ExpansionNode,
  GroveExampleNode,
  GroupNode,
  MessageNode,
  ModuleNode,
} from "./treeItems";

export class CatalogTreeProvider implements vscode.TreeDataProvider<CatalogNode> {
  private readonly _onDidChangeTreeData = new vscode.EventEmitter<void>();
  readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

  private repoRoot: string | undefined;
  private catalog: Catalog | undefined;

  constructor() {
    this.load();
  }

  // Reloads catalog data from the selected repository.
  // 从所选仓库重新加载目录数据。
  refresh(): void {
    this.load();
    this._onDidChangeTreeData.fire();
  }

  getRepoRoot(): string | undefined {
    return this.repoRoot;
  }

  getCatalog(): Catalog | undefined {
    return this.catalog;
  }

  private load(): void {
    this.repoRoot = locateRepoRoot();
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
      return this.catalogNodes();
    }
    if (node instanceof GroupNode) {
      if (!this.catalog) {
        return [];
      }
      if (node.group === "boards") {
        return this.catalog.boards.map((board) => new BoardNode(board));
      }
      if (node.group === "modules") {
        return this.catalog.modules.map((module) => new ModuleNode(module));
      }
      if (node.group === "expansions") {
        return this.catalog.expansions.map((expansion) => new ExpansionNode(expansion));
      }
      return [];
    }
    if (node instanceof BoardNode) {
      return node.board.examples.map((example) => new ExampleNode(example, node.board));
    }
    if (node instanceof ModuleNode) {
      return node.module.examples.map((example) => new GroveExampleNode(example, node.module));
    }
    return [];
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
      new GroupNode(
        "Boards",
        "boards",
        this.catalog.boards.length,
        vscode.TreeItemCollapsibleState.Collapsed,
      ),
      new GroupNode(
        "Grove Modules",
        "modules",
        this.catalog.modules.length,
        vscode.TreeItemCollapsibleState.Collapsed,
      ),
      new GroupNode(
        "Expansion Boards",
        "expansions",
        this.catalog.expansions.length,
        vscode.TreeItemCollapsibleState.Collapsed,
      ),
    ];
  }
}
