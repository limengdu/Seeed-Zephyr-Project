import * as vscode from "vscode";
import {
  Board,
  Example,
  ExpansionBoard,
  GroveModule,
  ValidationStatus,
} from "../model/types";
import type { DetailTarget } from "../panels/detailPanel";

export type GroupKind = "boards" | "modules" | "expansions";

// Maps a validation status to a VS Code theme icon id.
// 把验证状态映射到 VS Code 主题图标 id。
const STATUS_ICON: Record<string, string> = {
  "hardware-tested": "verified",
  "build-only": "check",
  experimental: "beaker",
  blocked: "error",
  unsupported: "circle-slash",
  unknown: "question",
};

function statusIcon(status: ValidationStatus): vscode.ThemeIcon {
  return new vscode.ThemeIcon(STATUS_ICON[status] ?? "question");
}

// Builds a tree-item click command that opens the detail panel.
// 构建一个树项点击命令,用于打开详情面板。
function detailCommand(target: DetailTarget): vscode.Command {
  return { command: "seeedZephyr.showDetail", title: "Show Detail", arguments: [target] };
}

export class GroupNode extends vscode.TreeItem {
  constructor(
    label: string,
    public readonly group: GroupKind,
    count: number,
  ) {
    super(label, vscode.TreeItemCollapsibleState.Expanded);
    this.description = `${count}`;
    this.contextValue = "group";
  }
}

export class BoardNode extends vscode.TreeItem {
  constructor(public readonly board: Board) {
    super(
      board.displayName,
      board.examples.length > 0
        ? vscode.TreeItemCollapsibleState.Collapsed
        : vscode.TreeItemCollapsibleState.None,
    );
    this.description = board.status;
    this.iconPath = statusIcon(board.status);
    this.tooltip = `${board.id}\n${board.zephyrTarget}`;
    this.contextValue = "board";
    this.command = detailCommand({ kind: "board", board });
  }
}

export class ExampleNode extends vscode.TreeItem {
  constructor(
    public readonly example: Example,
    public readonly board: Board,
  ) {
    super(example.demo, vscode.TreeItemCollapsibleState.None);
    this.description = example.validationStatus;
    this.iconPath = statusIcon(example.validationStatus);
    this.tooltip = example.expectedBehavior;
    this.contextValue = "example";
    this.command = detailCommand({ kind: "example", example, board });
  }
}

export class ModuleNode extends vscode.TreeItem {
  constructor(public readonly module: GroveModule) {
    super(module.displayName, vscode.TreeItemCollapsibleState.None);
    this.description = module.interface;
    this.iconPath = new vscode.ThemeIcon("circuit-board");
    this.tooltip = `${module.id}\n${module.zephyrSupport}`;
    this.contextValue = "module";
    this.command = detailCommand({ kind: "module", module });
  }
}

export class ExpansionNode extends vscode.TreeItem {
  constructor(public readonly expansion: ExpansionBoard) {
    super(expansion.displayName, vscode.TreeItemCollapsibleState.None);
    this.description = expansion.zephyrShield ?? "no shield";
    this.iconPath = new vscode.ThemeIcon("layers");
    this.tooltip = expansion.id;
    this.contextValue = "expansion";
    this.command = detailCommand({ kind: "expansion", expansion });
  }
}

export class MessageNode extends vscode.TreeItem {
  constructor(message: string) {
    super(message, vscode.TreeItemCollapsibleState.None);
    this.contextValue = "message";
  }
}

export type CatalogNode =
  | GroupNode
  | BoardNode
  | ExampleNode
  | ModuleNode
  | ExpansionNode
  | MessageNode;
