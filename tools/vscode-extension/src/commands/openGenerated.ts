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

export async function openProjectFolder(dir: string): Promise<boolean> {
  // Prefer adding the project to the current multi-root window, then reuse this
  // window as a fallback when VS Code refuses a workspace-folder edit.
  // 优先把项目加入当前多根工作区；当 VS Code 拒绝修改工作区时，复用当前窗口打开项目。
  const uri = vscode.Uri.file(dir);
  const name = path.basename(dir);
  const folders = vscode.workspace.workspaceFolders ?? [];
  const alreadyOpen = folders.some((folder) => samePath(folder.uri.fsPath, dir));
  if (alreadyOpen) {
    void vscode.window.showInformationMessage(`${name} is already open in this window.`);
    return true;
  }

  const inserted = vscode.workspace.updateWorkspaceFolders(
    folders.length,
    0,
    { uri },
  );
  if (inserted) {
    void vscode.window.showInformationMessage(`Added ${name} to this window.`);
    return true;
  }

  try {
    await vscode.commands.executeCommand("vscode.openFolder", uri, { forceReuseWindow: true });
    return true;
  } catch (error) {
    const detail = error instanceof Error ? error.message : String(error);
    void vscode.window.showErrorMessage(`Project folder could not be opened in this window: ${detail}`);
    return false;
  }
}

function samePath(left: string, right: string): boolean {
  return path.resolve(left) === path.resolve(right);
}
