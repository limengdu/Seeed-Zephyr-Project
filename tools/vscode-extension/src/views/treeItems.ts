import * as vscode from "vscode";
import {
  Board,
  Example,
  ExpansionBoard,
  GroveExample,
  GroveMatrixStatus,
  GroveModule,
  ValidationStatus,
} from "../model/types";
import type { DetailTarget } from "../panels/detailPanel";
import type { ProjectInfo } from "../statusBar";

export type GroupKind =
  | "projects"
  | "setup"
  | "catalog"
  | "boards"
  | "modules"
  | "expansions";

// Maps a validation status to a VS Code theme icon id.
// 把验证状态映射到 VS Code 主题图标 id。
const STATUS_ICON: Record<string, string> = {
  "hardware-tested": "verified",
  "build-only": "check",
  "build-verified": "check",
  "build-failed": "error",
  experimental: "beaker",
  blocked: "error",
  pending: "clock",
  unsupported: "circle-slash",
  excluded: "circle-slash",
  unknown: "question",
};

function statusIcon(status: ValidationStatus | GroveMatrixStatus): vscode.ThemeIcon {
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
    count?: number | string,
  ) {
    super(label, vscode.TreeItemCollapsibleState.Expanded);
    if (count !== undefined) {
      this.description = `${count}`;
    }
    this.contextValue = "group";
  }
}

export class ProjectNode extends vscode.TreeItem {
  constructor(
    label: string,
    public readonly project: ProjectInfo,
    boardLabel: string,
    portLabel: string,
  ) {
    super(label, vscode.TreeItemCollapsibleState.Expanded);
    this.description = `${boardLabel} - ${portLabel}`;
    this.iconPath = new vscode.ThemeIcon("folder-active");
    this.tooltip = project.appDir;
    this.contextValue = "project";
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
    super(
      module.displayName,
      module.examples.length > 0
        ? vscode.TreeItemCollapsibleState.Collapsed
        : vscode.TreeItemCollapsibleState.None,
    );
    this.description =
      module.examples.length > 0 ? `${module.interface} - ${module.examples.length}` : module.interface;
    this.iconPath = new vscode.ThemeIcon("circuit-board");
    this.tooltip = `${module.id}\n${module.zephyrSupport}`;
    this.contextValue = "module";
    this.command = detailCommand({ kind: "module", module });
  }
}

export class GroveExampleNode extends vscode.TreeItem {
  constructor(
    public readonly example: GroveExample,
    public readonly module: GroveModule,
  ) {
    super(example.demo, vscode.TreeItemCollapsibleState.None);
    const status = primaryGroveStatus(example);
    this.description = summarizeGroveStatus(example);
    this.iconPath = statusIcon(status);
    this.tooltip = example.expectedBehavior;
    this.contextValue = "groveExample";
    this.command = detailCommand({ kind: "groveExample", example, module });
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

export class ActionNode extends vscode.TreeItem {
  constructor(label: string, command: string, icon: string, description?: string) {
    super(label, vscode.TreeItemCollapsibleState.None);
    this.contextValue = "welcomeAction";
    this.description = description;
    this.iconPath = new vscode.ThemeIcon(icon);
    this.command = { command, title: label };
  }
}

export type CatalogNode =
  | ActionNode
  | GroupNode
  | ProjectNode
  | BoardNode
  | ExampleNode
  | ModuleNode
  | GroveExampleNode
  | ExpansionNode
  | MessageNode;

function primaryGroveStatus(example: GroveExample): GroveMatrixStatus {
  if (example.boardStatus.some((row) => row.status === "hardware-tested")) {
    return "hardware-tested";
  }
  if (example.boardStatus.some((row) => row.status === "build-verified")) {
    return "build-verified";
  }
  if (example.boardStatus.some((row) => row.status === "build-failed")) {
    return "build-failed";
  }
  return example.boardStatus.length > 0 ? "pending" : "unknown";
}

function summarizeGroveStatus(example: GroveExample): string {
  const verified = example.boardStatus.filter((row) =>
    row.status === "build-verified" || row.status === "hardware-tested"
  ).length;
  const failed = example.boardStatus.filter((row) => row.status === "build-failed").length;
  if (failed > 0) {
    return `${verified} verified - ${failed} failed`;
  }
  return `${verified} verified`;
}
