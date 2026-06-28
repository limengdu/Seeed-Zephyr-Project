import * as fs from "fs";
import * as path from "path";
import * as vscode from "vscode";

export interface ProjectInfo {
  appDir: string;
  board: string | undefined;
}

// Shows PlatformIO-style quick-action buttons when the workspace holds a Zephyr project.
// 当工作区里有一个 Zephyr 工程时,显示 PlatformIO 风格的快捷操作按钮。
export class ProjectStatusBar {
  private items: vscode.StatusBarItem[] = [];
  private project: ProjectInfo | undefined;

  constructor(private readonly context: vscode.ExtensionContext) {}

  // Re-detects the project and redraws the status bar buttons.
  // 重新检测工程并重绘状态栏按钮。
  refresh(): void {
    this.project = detectProject();
    this.render();
  }

  getProject(): ProjectInfo | undefined {
    return this.project;
  }

  private render(): void {
    this.clear();
    if (!this.project) {
      return;
    }
    const buttons: Array<[string, string, string]> = [
      ["$(check) Build", "seeedZephyr.projectBuild", "Build this project"],
      ["$(arrow-up) Upload", "seeedZephyr.projectFlash", "Build and flash this project"],
      ["$(plug) Monitor", "seeedZephyr.projectMonitor", "Open the serial monitor"],
    ];
    buttons.forEach(([text, command, tooltip], index) => {
      const item = vscode.window.createStatusBarItem(
        vscode.StatusBarAlignment.Left,
        100 - index,
      );
      item.text = text;
      item.command = command;
      item.tooltip = tooltip;
      item.show();
      this.items.push(item);
      this.context.subscriptions.push(item);
    });
  }

  private clear(): void {
    this.items.forEach((item) => item.dispose());
    this.items = [];
  }
}

// Detects a Zephyr project in any workspace folder: a snapshot.json or a Zephyr app.
// 在任一工作区文件夹中检测 Zephyr 工程:snapshot.json 或一个 Zephyr 应用。
function detectProject(): ProjectInfo | undefined {
  const folders = vscode.workspace.workspaceFolders ?? [];
  for (const folder of folders) {
    const dir = folder.uri.fsPath;
    const snapshot = path.join(dir, "snapshot.json");
    if (fs.existsSync(snapshot)) {
      return { appDir: dir, board: readSnapshotBoard(snapshot) };
    }
    if (
      fs.existsSync(path.join(dir, "CMakeLists.txt")) &&
      fs.existsSync(path.join(dir, "prj.conf"))
    ) {
      return { appDir: dir, board: undefined };
    }
  }
  return undefined;
}

function readSnapshotBoard(file: string): string | undefined {
  try {
    const data = JSON.parse(fs.readFileSync(file, "utf-8")) as { board?: unknown };
    return typeof data.board === "string" ? data.board : undefined;
  } catch {
    return undefined;
  }
}
