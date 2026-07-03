import * as fs from "fs";
import * as path from "path";
import * as vscode from "vscode";

// Opens a project folder and offers the same window choices used after creation.
// 打开项目文件夹,并提供与创建完成后相同的窗口选择。
export async function openGenerated(): Promise<void> {
  const folder = await vscode.window.showOpenDialog({
    canSelectFolders: true,
    canSelectFiles: false,
    canSelectMany: false,
    openLabel: "Open project",
  });
  if (!folder || folder.length === 0) {
    return;
  }

  const dir = folder[0].fsPath;
  if (!isKnownProjectFolder(dir)) {
    const proceed = await vscode.window.showWarningMessage(
      "No generated project receipt or Zephyr app files were found. This folder may still be opened.",
      "Continue",
    );
    if (proceed !== "Continue") {
      return;
    }
  }

  await openProjectFolder(dir);
}

function isKnownProjectFolder(dir: string): boolean {
  return (
    fs.existsSync(path.join(dir, "snapshot.json")) ||
    (
      fs.existsSync(path.join(dir, "CMakeLists.txt")) &&
      fs.existsSync(path.join(dir, "prj.conf"))
    )
  );
}

async function openProjectFolder(dir: string): Promise<void> {
  // Add the project to the current window (no new OS window, keeps open tabs).
  // 把项目加入当前窗口（不新开系统窗口，保留已打开的标签）。
  const inserted = vscode.workspace.updateWorkspaceFolders(
    vscode.workspace.workspaceFolders?.length ?? 0,
    0,
    { uri: vscode.Uri.file(dir) },
  );
  if (!inserted) {
    void vscode.window.showErrorMessage("Project folder could not be added to this window.");
    return;
  }
  void vscode.window.showInformationMessage(`Added ${path.basename(dir)} to this window.`);
}
