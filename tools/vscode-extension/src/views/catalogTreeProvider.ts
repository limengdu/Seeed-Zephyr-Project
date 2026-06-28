import * as vscode from "vscode";
import { readCatalog } from "../repo/dataReader";
import { locateRepoRoot } from "../repo/repoLocator";
import { Catalog } from "../model/types";
import {
  BoardNode,
  CatalogNode,
  ExampleNode,
  ExpansionNode,
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
    if (!this.catalog) {
      return [
        new MessageNode(
          "No seeed-zephyr repository found. Run 'Seeed XIAO: Set Repository Folder'.",
        ),
      ];
    }
    if (!node) {
      return [
        new GroupNode("Boards", "boards", this.catalog.boards.length),
        new GroupNode("Grove Modules", "modules", this.catalog.modules.length),
        new GroupNode("Expansion Boards", "expansions", this.catalog.expansions.length),
      ];
    }
    if (node instanceof GroupNode) {
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
    return [];
  }
}
