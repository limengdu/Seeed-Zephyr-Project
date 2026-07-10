import * as vscode from "vscode";
import { displayBoard, displayPort } from "./commands/projectSettings";
import { discoverProjects } from "./projectDiscovery";
import type { ProjectInfo } from "./projectDiscovery";

export type { ProjectInfo } from "./projectDiscovery";

// Shows PlatformIO-style quick-action buttons when the workspace holds a Zephyr project.
// 当工作区里有一个 Zephyr 工程时,显示 PlatformIO 风格的快捷操作按钮。
export class ProjectStatusBar {
  private items: vscode.StatusBarItem[] = [];
  private project: ProjectInfo | undefined;

  constructor(private readonly context: vscode.ExtensionContext) {}

  // Redraws the status bar for the selected project.
  // 为当前选中的项目重绘状态栏。
  refresh(project: ProjectInfo | undefined): void {
    this.project = project;
    this.render();
  }

  private render(): void {
    this.clear();
    if (!this.project) {
      return;
    }
    const buttons: Array<[string, string, string]> = [
      [
        `$(circuit-board) ${displayBoard(this.context, this.project)}`,
        "seeedZephyr.selectProjectBoard",
        "Select board",
      ],
      ["$(check) Build", "seeedZephyr.projectBuild", "Build this project"],
      ["$(arrow-up) Upload", "seeedZephyr.projectFlash", "Build and flash this project"],
      [
        `$(plug) ${displayPort(this.context, this.project)}`,
        "seeedZephyr.selectProjectPort",
        "Select serial port",
      ],
      [
        "$(rocket) Upload & Monitor",
        "seeedZephyr.projectFlashMonitor",
        "Build, flash, and open the serial monitor",
      ],
      ["$(terminal) Monitor", "seeedZephyr.projectMonitor", "Open the serial monitor"],
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

// Detects all Zephyr projects in the current multi-root workspace.
// 检测当前多根工作区中的全部 Zephyr 项目。
export function detectProjects(): ProjectInfo[] {
  const folders = vscode.workspace.workspaceFolders ?? [];
  return discoverProjects(folders.map((folder) => folder.uri.fsPath));
}
